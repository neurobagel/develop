<div align="center">

# Federation API

[![CI](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/neurobagel/develop/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/federation-api?token=B827PI9W1U&style=flat-square&logo=codecov&link=https%3A%2F%2Fcodecov.io%2Fgh%2Fneurobagel%2Ffederation-api)](https://app.codecov.io/gh/neurobagel/federation-api)
[![Python versions static](https://img.shields.io/badge/python-3.10--3.13-blue?style=flat-square&logo=python)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/federation-api?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![Docker Image Version (tag)](https://img.shields.io/docker/v/neurobagel/federation_api/latest?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Ffederation_api%2Ftags)](https://hub.docker.com/r/neurobagel/federation_api/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurobagel/federation_api?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Ffederation_api%2Ftags)](https://hub.docker.com/r/neurobagel/federation_api/tags)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/neurobagel/federation-api?style=flat-square&label=openssf%20scorecard)](https://scorecard.dev/viewer/?uri=github.com/neurobagel/federation-api)

</div>

Please refer to our [**official documentation**](https://neurobagel.org/user_guide/api/) for more information on Neurobagel federation and how to [deploy your own federation API](https://neurobagel.org/user_guide/getting_started/).

## Launching the API
### 1. Set the local Neurobagel nodes to federate over
Create a configuration JSON file called `local_nb_nodes.json` containing the URLs and (arbitrary) names of the local nodes you wish to federate over.
Each node must be denoted by a dictionary `{}` with two key-value pairs: `"NodeName"` for the name of the node, and `"ApiURL"` for the url of the API exposed for that node. 
Multiple nodes must be wrapped in a list `[]`.

For a template `local_nb_nodes.json` file that you can clone and edit, 
see the [neurobagel/recipes](https://github.com/neurobagel/recipes/tree/main/local_federation) repo.

Examples:  

`local_nb_nodes.json` with one local node API running on `http://localhost:8000`
```json
{
    "NodeName": "Local graph",
    "ApiURL": "http://host.docker.internal:8000"
}
```
_**NOTE:** If the local node API(s) you are federating over is running on the same host machine as the federation API 
(e.g., the URL to access the node API is `http://localhost:XXXX`), 
in `local_nb_nodes.json` you **must** replace `localhost` with `host.docker.internal` in the corresponding `"ApiURL"`, 
as shown above (for more information, see the [Docker documentation](https://docs.docker.com/engine/reference/commandline/run/#add-host))._

`local_nb_nodes.json` with two local nodes
```json
[
    {
        "NodeName": "Local graph 1",
        "ApiURL": "http://host.docker.internal:8000"
    },
    {
        "NodeName": "Local graph 2",
        "ApiURL": "http://192.168.0.1"
    }
]
```

### 2. Run the Docker container
```bash
docker pull neurobagel/federation_api

# Run this next command in the same directory where your `local_nb_nodes.json` file is located
docker run -d -v ${PWD}/local_nb_nodes.json:/usr/src/local_nb_nodes.json:ro \
    --add-host=host.docker.internal:host-gateway \
    --name=federation -p 8080:8000 neurobagel/federation_api
```
NOTE: You can replace the port number `8080` for the `-p` flag with any port on the host you wish to use for the API.

## Development in the Neurobagel monorepo

This tool lives in `tools/federation-api/` of https://github.com/neurobagel/develop.

### Setup

We [use `uv`](https://docs.astral.sh/uv/getting-started/installation/) for the local development environment.

```bash
git clone https://github.com/neurobagel/develop.git
cd develop/tools/federation-api
uv sync --group dev
```

This installs the project in editable mode. Launch the API from `tools/federation-api/` with

```bash
uv run uvicorn app.main:app
```

The version is derived from the repository's `federation-api-v*` tags, so the clone needs its full history and tags (the default for `git clone`).

### Tests

From `tools/federation-api/`:

```bash
uv run pytest
```

Or from the repository root: `just test federation-api`. CI runs the tests on Python 3.10 to 3.13 whenever a pull request changes `tools/federation-api/`.

### Docker image

From the repository root:

```bash
docker build -f tools/federation-api/Dockerfile -t neurobagel/federation_api:local .
```

The build context is the repository root, so images must be built from there with `-f`. `tools/federation-api/Dockerfile.dockerignore` (next to the Dockerfile, read automatically by BuildKit) allowlists the files the image needs; everything else in the repository stays out of the build context. `just build federation-api` runs the same command.

The image contains the `app` package and its runtime dependencies, exported from `uv.lock`, and serves the API on port 8000.

### Releases

Tags: `federation-api-vX.Y.Z`. Published to: Docker Hub `neurobagel/federation_api`.
Release automation (release-please) is not set up in this repository yet, so no releases are made from it.
PR titles must follow Conventional Commits with scope `federation-api`, for example `fix(federation-api): ...`.
