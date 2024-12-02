import pytest
from fastapi import HTTPException

from app.api.security import extract_token, verify_token


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
def test_invalid_token_raises_error(monkeypatch, invalid_token):
    """Test that an invalid token raises an error from the verification process."""
    monkeypatch.setattr("app.api.security.CLIENT_ID", "foo.id")

    with pytest.raises(HTTPException) as exc_info:
        verify_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


@pytest.mark.parametrize(
    "invalid_auth_header",
    [{}, {"Authorization": ""}, {"badheader": "badvalue"}],
)
def test_query_with_malformed_auth_header_fails(
    test_app,
    set_mock_verify_token,
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


def test_token_returned_without_auth_scheme(monkeypatch, enable_auth):
    """
    Test that when a token is valid, verify_token correctly returns the token with the authorization scheme stripped.
    """
    mock_valid_token = "Bearer foo"
    assert extract_token(mock_valid_token) == "foo"


def test_valid_token_does_not_error_out(monkeypatch, enable_auth):
    """
    Test that when a valid token is passed to verify_token, the token is returned without errors.
    """

    def mock_get_signing_key_from_jwt(*args, **kwargs):
        # NOTE: The actual get_signing_key_from_jwt method should return a key object
        return "signingkey"

    def mock_jwt_decode(*args, **kwargs):
        return {
            "iss": "https://myissuer.com",
            "aud": "123abc.myapp.com",
            "sub": "1234567890",
            "name": "John Doe",
            "iat": 1730476922,
            "exp": 1730480522,
        }

    monkeypatch.setattr("app.api.security.CLIENT_ID", "123abc.myapp.com")
    monkeypatch.setattr(
        "app.api.security.JWKS_CLIENT.get_signing_key_from_jwt",
        mock_get_signing_key_from_jwt,
    )
    monkeypatch.setattr("app.api.security.jwt.decode", mock_jwt_decode)

    assert verify_token("Bearer myvalidtoken") == "myvalidtoken"
