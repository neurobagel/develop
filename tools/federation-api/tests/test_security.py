import pytest
from fastapi import HTTPException
from google.oauth2 import id_token

from app.api.security import verify_and_extract_token


def test_missing_client_id_raises_error_when_auth_enabled(
    monkeypatch, test_app, enable_auth
):
    """Test that a missing client ID raises an error on startup when authentication is enabled."""
    # We're using what should be default values of CLIENT_ID and AUTH_ENABLED here
    # (if the corresponding environment variables are unset),
    # but we set the values explicitly here for clarity
    monkeypatch.setattr("app.api.security.CLIENT_ID", None)

    with pytest.raises(ValueError) as exc_info:
        with test_app:
            pass

    assert "NB_QUERY_CLIENT_ID is not set" in str(exc_info.value)


# Ignore startup warning that is unrelated to the current test
@pytest.mark.filterwarnings(
    "ignore:No local Neurobagel nodes defined or found"
)
def test_missing_client_id_ignored_when_auth_disabled(monkeypatch, test_app):
    """Test that a missing client ID does not raise an error when authentication is disabled."""
    monkeypatch.setattr("app.api.security.CLIENT_ID", None)
    monkeypatch.setattr("app.api.security.AUTH_ENABLED", False)

    with test_app:
        pass


@pytest.mark.parametrize(
    "invalid_token",
    ["Bearer faketoken", "Bearer", "faketoken", "fakescheme faketoken"],
)
def test_invalid_token_raises_error(invalid_token):
    """Test that an invalid token raises an error from the verification process."""
    with pytest.raises(HTTPException) as exc_info:
        verify_and_extract_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


@pytest.mark.parametrize(
    "invalid_auth_header",
    [{}, {"Authorization": ""}, {"badheader": "badvalue"}],
)
def test_query_with_malformed_auth_header_fails(
    test_app,
    set_mock_verify_and_extract_token,
    enable_auth,
    invalid_auth_header,
    monkeypatch,
):
    """
    Test that when authentication is enabled, a request to the /query route with a
    missing or malformed authorization header fails.
    """
    monkeypatch.setattr("app.api.security.CLIENT_ID", "foo.id")

    response = test_app.get(
        "/query",
        headers=invalid_auth_header,
    )

    assert response.status_code == 403


def test_verified_token_returned_without_auth_scheme(monkeypatch, enable_auth):
    """
    Test that when a token is valid, verify_token correctly returns the token with the authorization scheme stripped.
    """
    mock_valid_token = "Bearer foo"
    mock_id_info = {
        "iss": "https://accounts.google.com",
        "azp": "123abc.apps.googleusercontent.com",
        "aud": "123abc.apps.googleusercontent.com",
        "sub": "1234567890",
        "email": "jane.doe@gmail.com",
        "email_verified": True,
        "nbf": 1730476622,
        "name": "Jane Doe",
        "picture": "https://lh3.googleusercontent.com/a/example1234567890",
        "given_name": "Jane",
        "family_name": "Doe",
        "iat": 1730476922,
        "exp": 1730480522,
        "jti": "123e4567-e89b",
    }

    def mock_oauth2_verify_token(param, request, client_id, **kwargs):
        return mock_id_info

    monkeypatch.setattr(
        id_token, "verify_oauth2_token", mock_oauth2_verify_token
    )

    assert verify_and_extract_token(mock_valid_token) == "foo"
