<div align="center">

# Neurobagel API

[![CI](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/neurobagel/develop/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/api?token=ZEOGQFFZMJ&style=flat-square&logo=codecov&link=https%3A%2F%2Fcodecov.io%2Fgh%2Fneurobagel%2Fapi)](https://app.codecov.io/gh/neurobagel/api)
[![Python versions static](https://img.shields.io/badge/python-3.10--3.13-blue?style=flat-square&logo=python)](https://www.python.org)  
[![License](https://img.shields.io/github/license/neurobagel/api?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![Docker Image Version (tag)](https://img.shields.io/docker/v/neurobagel/api/latest?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fapi%2Ftags)](https://hub.docker.com/r/neurobagel/api/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurobagel/api?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fapi%2Ftags)](https://hub.docker.com/r/neurobagel/api/tags)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/neurobagel/api?style=flat-square&label=openssf%20scorecard)](https://scorecard.dev/viewer/?uri=github.com/neurobagel/api)

</div>

The Neurobagel API is a REST API, developed in [Python](https://www.python.org/) using [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://docs.pydantic.dev/).

Please refer to our [**official documentation**](https://neurobagel.org/user_guide/api/) for more information on how to use the API.

- [Quickstart](#quickstart)
- [Local installation](#local-installation)
  - [Clone the repo](#clone-the-repo)
  - [Set the environment variables](#set-the-environment-variables)
  - [Docker](#docker)
    - [Option 1 (RECOMMENDED): Use the Neurobagel Docker Compose recipe](#option-1-recommended-use-the-neurobagel-docker-compose-recipe)
    - [Option 2: Use the latest image from Docker Hub](#option-2-use-the-latest-image-from-docker-hub)
    - [Option 3: Build the image using the Dockerfile](#option-3-build-the-image-using-the-dockerfile)
    - [Send a test query to the API](#send-a-test-query-to-the-api)
  - [Python](#python-development-environment)
    - [Install dependencies](#install-dependencies)
    - [Launch the API](#launch-the-api)
  - [Troubleshooting](#troubleshooting)
- [Development in the Neurobagel monorepo](#development-in-the-neurobagel-monorepo)
- [The default Neurobagel SPARQL query](#the-default-neurobagel-sparql-query)
- [Updating dependencies](#updating-dependencies)
- [License](#license)

## Quickstart
The API is hosted at https://api.neurobagel.org/ and interfaces with Neurobagel's graph database. Queries of the graph can be run using the `/query` route.

Example: **I want to query for only female participants in the graph.** 
The URL for such a query would be https://api.neurobagel.org/query?sex=snomed:248152002, where `snomed:248152002` is a [standardized term from the SNOMED CT database](http://purl.bioontology.org/ontology/SNOMEDCT/248152002) corresponding to female sex.

Interactive documentation for the API is available at https://api.neurobagel.org/docs.

## Local installation
The below instructions assume that you have a local instance of or access to a remotely hosted graph database to be queried. 
If this is not the case and you need to first build a graph from data, refer to our documentation for [getting started locally with a graph backend](https://neurobagel.org/user_guide/getting_started/).

### Clone the repo
The API lives in `tools/api/` of the Neurobagel monorepo:
```bash
git clone https://github.com/neurobagel/develop.git
cd develop/tools/api
```

### Set the environment variables
Create a file called `.env` in `tools/api/` to store the environment variables used by the app. 
See the Neurobagel recipes repo for a [template `.env` file](https://github.com/neurobagel/recipes/blob/main/template.env) you can copy and edit.

To run API requests against a graph, at least two environment variables must be set: `NB_GRAPH_USERNAME` and `NB_GRAPH_PASSWORD`.

**See our [official documentation](https://neurobagel.org/user_guide/config/#environment-variables) for all the possible Neurobagel environment variables that you can set in `.env`, and to check which variables are relevant for your specific installation and setup.**

> :warning: **Important:** 
> - Variables set in the shell environment where the API is launched **_should not be used as a replacement for the `.env` file_** to configure options for the API or graph server software.
> - To avoid conflicts related to [Docker's environment variable precedence](https://docs.docker.com/compose/environment-variables/envvars-precedence/), 
> also ensure that any variables defined in your `.env` are not already set in your current shell environment with **different** values.

The below instructions for Docker and Python assume that you have at least set `NB_GRAPH_USERNAME` and `NB_GRAPH_PASSWORD` in your `.env`.

### Docker
First, [install Docker](https://docs.docker.com/get-docker/).

You can then run a Docker container for the API in one of three ways:
#### Option 1 (RECOMMENDED): Use the Neurobagel Docker Compose recipe

Follow the instructions in our [official documentation](https://neurobagel.org/user_guide/getting_started/) for using the template configuration files provided in our [recipes](https://github.com/neurobagel/recipes) repository to spin up a local Neurobagel API and graph backend using [Docker Compose](https://docs.docker.com/compose/install/).

**TIP:** Double check that Neurobagel environment variables are resolved with your expected values using the command `docker compose config`.

#### Option 2: Use the latest image from Docker Hub
```bash
docker pull neurobagel/api
docker run -d --name=api -p 8000:8000 --env-file=.env neurobagel/api
```
**NOTE:** The above `docker run` command uses recommended default values for `NBI_API_PORT_HOST` and `NB_API_PORT` in the `-p` flag.
If you wish to set different port numbers, modify your `.env` file accordingly and run the below commands instead:
```bash
export $(cat .env | xargs)  # export your .env file to expose your set port numbers to the -p flag of docker run
docker run -d --name=api -p ${NB_API_PORT_HOST}:${NB_API_PORT} --env-file=.env neurobagel/api
```
> :warning: **IMPORTANT:** If using the above command, do not wrap any values for variables in the `.env` file in quotation marks, as they will be interpreted literally and may lead to [issues](https://github.com/docker/for-linux/issues/1208).

#### Option 3: Build the image using the Dockerfile
After cloning the repository, build the Docker image from the repository root and run it from `tools/api/`:
```bash
docker build -t neurobagel/api tools/api
cd tools/api
docker run -d --name=api -p 8000:8000 --env-file=.env neurobagel/api
```
**NOTE:** The above `docker run` command uses recommended default values for `NBI_API_PORT_HOST` and `NB_API_PORT` in the `-p` flag. 
If you wish to set different port numbers, modify your `.env` file accordingly and run the below commands instead:
```bash
# from tools/api/, after building the image as above
export $(cat .env | xargs)  # export your .env file to expose your set port numbers to the -p flag of docker run
docker run -d --name=api -p ${NB_API_PORT_HOST}:${NB_API_PORT} --env-file=.env neurobagel/api
```
> :warning: **IMPORTANT:** If using the above command, do not wrap any values for variables in the `.env` file in quotation marks, as they will be interpreted literally and may lead to [issues](https://github.com/docker/for-linux/issues/1208).

#### Send a test query to the API
By default, after running the above steps, the API should be served at localhost, http://127.0.0.1:8000/query, on the machine where you launched the Dockerized app. To check that the API is running and can access the knowledge graph as expected, you can navigate to the interactive API docs in your local browser (http://127.0.0.1:8000/docs) and enter a sample query, or send an HTTP request in your terminal using `curl`:
``` bash
# example: query for female subjects in graph
curl http://127.0.0.1:8000/query?sex=snomed:248152002 
```
The response should be a list of dictionaries containing info about datasets with participants matching the query.

### Python (development environment)

#### `uv`
We use `uv` to facilitate dependency management and reproducible environments.
If you are setting up a local development environment for the first time, 
install `uv` following the [docs](https://docs.astral.sh/uv/getting-started/installation/).

#### Install dependencies

After cloning the repository, install the package in editable mode with development dependencies using [uv](https://docs.astral.sh/uv/):

```bash
uv sync --group dev
```

This will create a virtual environment (if one doesn't exist)
called `.venv` in `tools/api/` and install all project and dev dependencies into that environment.

#### Launch the API

To launch the API, make sure you're in `tools/api/` and that your [`.env` file has been configured](#set-the-environment-variables).

Export the variables defined in your `.env` file:
```bash
export $(cat .env | xargs)
```

You can then launch the API using either of these methods:

**Option 1: Using uv run (recommended)**
```bash
uv run python -m app.main
```
This launches the API inside the project environment without requiring you to activate a virtual environment first.

**Option 2: Activate the virtual environment manually**
```bash
source .venv/bin/activate
python -m app.main
```

```bash
INFO:     Will watch for changes in these directories: ['home/usr/directory/']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12683] using StatReload
INFO:     Started server process [12685]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
...
```
You can verify the API is running once you receive info messages similar to the above in your terminal.

### Troubleshooting
If you get a 401 response to your API request with an `"Unauthorized: "` error message, your `NB_GRAPH_USERNAME` and `NB_GRAPH_PASSWORD` pair may be incorrect. Verify that these environment variables have been exported and/or have the correct values.

## Development in the Neurobagel monorepo

This tool lives in `tools/api/` of https://github.com/neurobagel/develop.

### Setup

```bash
git clone https://github.com/neurobagel/develop.git
cd develop/tools/api
uv sync --group dev
```

The version is derived from the repository's `api-v*` tags, so the clone needs its full history and tags (the default for `git clone`).

The tests use example data and the test graph configuration from the monorepo's shared folders, reached through two symlinks in `tools/api/`: `neurobagel_examples -> ../../examples` and `recipes -> ../../stack`. No submodules are needed.

### Tests

The tests use [Pytest](https://docs.pytest.org/). From `tools/api/`, run the unit tests (integration tests are skipped by default):

```bash
uv run pytest
```

The integration tests of SPARQL queries need the test graph store and the datasets metadata it exports. Start them from `tools/api/`:

```bash
docker compose up -d test_graph export_datasets_metadata
```

Wait until `docker logs api-test_graph-1` shows `FINISHED UPLOADING DATA`, then run all tests:

```bash
uv run pytest -m "integration or not integration"
```

Or only the integration tests:

```bash
uv run pytest -m "integration"
```

_NOTE: Don't have a `.env` file in `tools/api/` while testing, as docker compose would read it and override the test configuration._

When you are done, stop and remove the test services and their volumes:

```bash
docker compose down -v
```

From the repository root, `just test api` starts the test graph, waits for it and runs all tests. CI runs them on Python 3.10 to 3.13 whenever a pull request changes `tools/api/`, `stack/` or `examples/`.

### Docker image

From the repository root:

```bash
docker build -t neurobagel/api:local tools/api
```

The image contains the `app` package and its runtime dependencies, exported from `uv.lock`, and serves the API on port 8000. It requires at least `NB_GRAPH_USERNAME` and `NB_GRAPH_PASSWORD` and a datasets metadata file at runtime (see [Set the environment variables](#set-the-environment-variables)).

### Releases

Tags: `api-vX.Y.Z`. Published to: Docker Hub `neurobagel/api`.
Release automation (release-please) is not set up in this repository yet, so no releases are made from it.
PR titles must follow Conventional Commits with scope `api`, for example `fix(api): ...`.

## The default Neurobagel SPARQL query

[`docs/default_neurobagel_query.rq`](docs/default_neurobagel_query.rq) contains a sample default SPARQL query sent by the Neurobagel API to a graph database to retrieve all available phenotypic and imaging data.
This file is mainly intended for reference because in normal operations, 
the API will always talk to the graph on behalf of the user.

(For developers) 
To regenerate this sample query when the API query template is updated, first launch an interactive Python terminal from `tools/api/`:

```bash
uv run python
```
Then, run the following commands:
```python
from app.main import fetch_supported_namespaces_for_config
from app.api import env_settings
from app.api.utility import create_query

env_settings.CONTEXT = fetch_supported_namespaces_for_config(env_settings.DEFAULT_NEUROBAGEL_CONFIG)

with open("docs/default_neurobagel_query.rq", "w") as file:
    file.write(create_query(return_agg=False))
```

## Updating dependencies

We use `uv` to manage dependencies. 
To [add a new dependency](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies), use:

```bash
uv add <dependency>
```

`uv` creates a lockfile (`uv.lock`) with exact version pins based on the `pyproject.toml`. We use this lockfile for deterministic builds
and to make sure that production and development environments are the same.

If you modify existing dependencies in the `pyproject.toml`,
you must also [update the lockfile](https://docs.astral.sh/uv/concepts/projects/sync/) using:

```bash
uv lock
```

## License

Neurobagel API is released under the terms of the [MIT License](LICENSE)
