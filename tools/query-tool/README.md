<div align="center">

# Query Tool

[![CI](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/neurobagel/develop/actions/workflows/ci.yml?query=branch%3Amain)
[![Node version](https://img.shields.io/badge/node-20.9-green?style=flat-square&logo=nodedotjs)](https://nodejs.org/en)
[![License](https://img.shields.io/github/license/neurobagel/query-tool?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![Docker Image Version (tag)](https://img.shields.io/docker/v/neurobagel/query_tool/latest?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fquery_tool%2Ftags)](https://hub.docker.com/r/neurobagel/query_tool/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurobagel/query_tool?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fquery_tool%2Ftags)](https://hub.docker.com/r/neurobagel/query_tool/tags)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/neurobagel/query-tool?style=flat-square&label=openssf%20scorecard)](https://scorecard.dev/viewer/?uri=github.com/neurobagel/query-tool)

[![Staging app status](https://img.shields.io/website?url=https%3A%2F%2Fneurobagel-query.netlify.app&up_message=live&up_color=B0C4DE&down_message=down&down_color=CD5C5C&style=flat-square&label=staging%20app&link=https%3A%2F%2Fneurobagel-query.netlify.app)](https://neurobagel-query.netlify.app/)
[![Deployed app status](https://img.shields.io/website?url=https%3A%2F%2Fquery.neurobagel.org&up_message=live&up_color=B0C4DE&down_message=down&down_color=CD5C5C&style=flat-square&label=deployed%20app&link=https%3A%2F%2Fquery.neurobagel.org)](https://query.neurobagel.org/)

The query tool is a React application, developed in [TypeScript](https://www.typescriptlang.org/) using a variety of tools including [Vite](https://vitejs.dev/), [Cypress](https://www.cypress.io/), and [MUI](https://mui.com/).

[Quickstart](#quickstart) |
[Local Installation](#local-installation) |
[Usage](#usage) |
[Testing](#testing) |
[Development in the Neurobagel monorepo](#development-in-the-neurobagel-monorepo) |
[License](#license)

</div>

Please refer to our [**official documentation**](https://neurobagel.org/user_guide/query_tool/) for more detailed information on how to use the query tool.

## Quickstart

The query tool is hosted at https://query.neurobagel.org/ and interfaces with [Neurobagel federation API](https://federate.neurobagel.org/docs).

## Local Installation

To run the query tool locally, you have two options:

1. Use our docker image
2. Do a manual install from a clone of the [Neurobagel monorepo](https://github.com/neurobagel/develop), in `tools/query-tool/`.

but before proceeding with either you need to set the environment variables.

### Mandatory configuration

| Environment variable     | Type    | Required                                 | Default value if not set | Example                                                   |
| ------------------------ | ------- | ---------------------------------------- | ------------------------ | --------------------------------------------------------- |
| `NB_API_QUERY_URL`       | string  | Yes                                      | -                        | `https://federate.neurobagel.org/`                        |
| `NB_QUERY_APP_BASE_PATH` | string  | No                                       | `/`                      | `/query/`                                                 |
| `NB_ENABLE_AUTH`         | boolean | No                                       | `false`                  | `false`                                                   |
| `NB_QUERY_CLIENT_ID`     | string  | Yes (if `NB_ENABLE_AUTH` is set to true) | -                        | `""`                                                      |
| `NB_QUERY_HEADER_SCRIPT` | string  | No                                       | `""`                     | `'<script defer data-domain="mydomain" src="plausible">'` |

#### `NB_API_QUERY_URL`

You'll need to set the `NB_API_QUERY_URL` environment variable required to run the query tool. `NB_API_QUERY_URL` is the [Neurobagel API](https://github.com/neurobagel/api) URL that the query tool uses to send requests to for results.

#### `NB_QUERY_APP_BASE_PATH`

If you are using a custom configuration where the query tool is accessible via a path other than the root (`/`), you need to set the `NB_QUERY_APP_BASE_PATH` to your custom path. This ensures that the query tool is correctly rendered and accessible at the specified URL

#### `NB_ENABLE_AUTH`

If the API you'd like to send queries to requires authentication, you need to set `NB_ENABLE_AUTH` to `true` as it is `false` by default. This will enable authentication flow of the app.

#### `NB_QUERY_CLIENT_ID`

If the `NB_ENABLE_AUTH` is set to `true` (it is `false` by default), you need to provide a valid client ID for the authentication.
_At the moment, query tool uses Google for authentication, so you need to obtain a client ID from Google developer console. See [documentation](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid) for more information._

#### `NB_QUERY_HEADER_SCRIPT`

If you want to add a custom script to the header of the query tool, you can set the `NB_QUERY_HEADER_SCRIPT` environment variable to the script you want to add.
This script will be added to the header of the query tool. For example, in our production deployment we use the GDPR aware analytics tool [Plausible](https://plausible.io/),
so we set the `NB_QUERY_HEADER_SCRIPT` to the script provided by Plausible.
When you use this variable, make sure you use single quotes to include the script like so:

```bash
NB_QUERY_HEADER_SCRIPT='<script defer data-domain="mydomain" src="plausible">'
```

#### Set the environment variables

To set environment variables, create a `.env` file in `tools/query-tool/` and add the environment variables there. If you're running a neurobagel node-API locally on your machine (following the instructions [here](https://github.com/neurobagel/api#local-installation)), your `.env` file would look something like this:

```bash
NB_API_QUERY_URL=http://localhost:8000/
```

if you're using the remote api, your `.env` file would look something like this:

```bash
NB_API_QUERY_URL=https://federate.neurobagel.org/
```

if you're using a remote api with authentication, your `.env` file would look something like this:

```bash
NB_API_QUERY_URL=https://federate.neurobagel.org/
NB_ENABLE_AUTH=true
NB_QUERY_CLIENT_ID=46923719231972-dhsahgasl3123.apps.googleusercontent.com
```

:warning: The protocol matters here.
If you wish to use the Neurobagel remote API, ensure your `NB_API_QUERY_URL` uses `https` instead of `http`.

### Docker installation

To obtain the query tool docker image, simply run the following command in your terminal:

```bash
docker pull neurobagel/query_tool:latest
```

This Docker image includes the latest release of the query tool and a minimal http server to serve the static tool.

To launch the query tool Docker container and pass in the `.env` file you have created, simply run

```bash
docker run -p 5173:5173 --env-file=.env neurobagel/query_tool:latest
```

Then you can access the query tool at http://localhost:5173

**Note**: the query tool is listening on port `5173` inside the docker container,
replace port `5173` by the port you would like to expose to the host.
For example if you'd like to run the tool on port `8000` of your machine you can run the following command:

```bash
docker run -p 8000:5173 --env-file=.env neurobagel/query_tool:latest
```

### Manual installation

To install the query tool directly, you'll need [node package manager (npm)](https://www.npmjs.com/) and [Node.js](https://nodejs.org/en/).
You can find the instructions on installing npm and node in the official [documentation](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Once you have npm and node installed, you'll need to install the dependencies outlined in the package.json file.
You can do so by running the following command from `tools/query-tool/`:

```bash
npm install
```

To launch the tool in developer mode run the following command:

```bash
npm run dev
```

You can also build and then run the tool from ([production](https://vitejs.dev/guide/build)) build of the application by running the following command:

```bash
npm run build && npm run preview
```

You can verify the tool is running by watching for the` info messages from Vite regarding environment, rendering, and what port the tool is running on in your terminal.

#### Developer setup

The repository's commit hooks (root `.pre-commit-config.yaml`) run this tool's `lint-staged.config.js` (typecheck, eslint, prettier) on staged files in `tools/query-tool/`. Install them once with `pre-commit install` from the repository root (for example after `pip install pre-commit`); they need `npm ci` to have been run here. The same install adds a `post-merge` hook that reruns `npm ci` here after a merge or pull that changed `package.json` or `package-lock.json`.

##### Docker compose testing environment for development

Since the query tool relies on other neurobagel tools to function, their presence is often required during development. `docker-compose.yml` in `tools/query-tool/` defines a `test` profile for this. It builds on the monorepo's shared development and test stack in `stack/` and loads example data from `examples/`, referring to both by relative path (`../../stack`, `../../examples`). It starts the example data preparation (`init_data`), a graph with the example dataset, a node API and a federation API. The federation API federates over that node API, as defined in `stack/local_nb_nodes.template.json`, plus the public Neurobagel nodes.

Pull the latest images and bring up the stack from `tools/query-tool/` with:

```bash
docker compose --profile test pull && docker compose --profile test up -d
```

The graph is ready when `docker logs query-tool-graph-1` shows `Finished setting up the Neurobagel graph backend.`. The node API is then served on port 8000 and the federation API on port 8080. Stop and remove the stack with:

```bash
docker compose --profile test down -v
```

_NOTE: Make sure your .env file in `tools/query-tool/` doesn't contain any of the environment variables used in the docker compose file as it will conflict with the configuration, since docker compose will use `.env` by default._

## Usage

To define a cohort, set your inclusion criteria using the following:

- Age: Minimum and/or maximum age (in years) of participant that should be included in the results.
- Sex: Sex of participant that should be included in the results.
- Diagnosis: Diagnosis of participant that should be included in the results
- Minimum number of imaging sessions: Minimum number of imaging sessions that participant should have to be included in the results.
- Minimum number of phenotypic sessions: Minimum number of phenotypic sessions that participant should have to be included in the results.
- Assessment tool: Non-imaging assessment completed by participant that should be included in the results.
- Imaging modality: Imaging modality of participant scans that should be included in the results.
- Pipeline name: Name of the pipeline used to process subject scans.
- Pipeline version: Version of the pipeline used to process subject scans.

Once you've defined your criteria, submit them as a query and the query tool will display the results.\
The query tool offers two different TSV files for results:

- cohort participant results TSV contains: dataset name, repository url, access link, number of matching subjects, subject id, session id, session file path, session type, age, sex, diagnosis, assessment, number of matching phenotypic sessions, number of matching imaging sessions, session imaging modality, session completed pipelines, dataset imaging modality, and dataset pipelines

- cohort participant machine results TSV contains: dataset name, repository url, access link, subject id, session id, session file path, session type, number of matching phenotypic sessions, number of matching imaging sessions, session imaging modality, session completed pipelines, dataset imaging modality, and dataset pipeline

You can refer to [the neurobagel documentation](https://neurobagel.org/user_guide/query_tool/#downloading-query-results) to see what the outputs of the query tool look like and how they are structured. You can also download the raw example output files [here](https://github.com/neurobagel/neurobagel_examples/tree/main/query-tool-results).

## Testing

The query tool utilizes the [Cypress](https://www.cypress.io/) framework for testing, configured in `cypress.config.ts`.

To run the tests interactively, execute the following command from `tools/query-tool/`:

```bash
npx cypress open
```

## Development in the Neurobagel monorepo

This tool lives in `tools/query-tool/` of https://github.com/neurobagel/develop.

### Setup

```bash
git clone https://github.com/neurobagel/develop.git
cd develop/tools/query-tool
npm ci
```

The Cypress tests import example API responses from the monorepo's `examples/` folder through the symlink `neurobagel_examples -> ../../examples`. No submodules are needed.

### Tests

From `tools/query-tool/`, the static checks:

```bash
npm run lint:check
npm run format:check
npm run typecheck
```

Component tests, built against the public federation API as in CI:

```bash
echo "NB_API_QUERY_URL=https://federate.neurobagel.org/" > .env
npm run build
npm run test:component
```

End-to-end tests run against the production build served by `npm run preview` on port 5173, with authentication enabled and a mock client ID:

```bash
printf 'NB_API_QUERY_URL=https://federate.neurobagel.org/\nNB_ENABLE_AUTH=true\nNB_QUERY_CLIENT_ID=mockclientid\n' > .env
npm run build
```

Then start the preview server in a second terminal, also from `tools/query-tool/`:

```bash
npm run preview
```

and run the tests in the first one:

```bash
npm run test:e2e
```

Stop the preview server with Ctrl+C when done.

From the repository root, `just test query-tool` runs `npm ci`, the static checks and the component tests. CI runs everything above, plus codespell, whenever a pull request changes `tools/query-tool/` or `examples/`.

### Docker image

From the repository root:

```bash
docker build -f tools/query-tool/Dockerfile -t neurobagel/query_tool:local .
```

The build context is the repository root, so images must be built from there with `-f`. `tools/query-tool/Dockerfile.dockerignore` (next to the Dockerfile, read automatically by BuildKit) allowlists the files the image needs; everything else in the repository stays out of the build context. `just build query-tool` runs the same command. The Dockerfile copies the monorepo's `examples/` folder into the build in place of the `neurobagel_examples` symlink, which Docker does not follow.

The image contains the production build of the app, served by nginx on port 5173. The `NB_*` variables are substituted when the container starts, and it exits unless `NB_API_QUERY_URL` is set (see [Mandatory configuration](#mandatory-configuration)).

Nightly images: every push to `main` that changes this tool rebuilds `<registry>/<namespace>/query_tool:nightly` for linux/amd64 and linux/arm64 (`.github/workflows/nightly.yml`; registry and namespace come from the repository variables `IMAGE_REGISTRY` and `IMAGE_NAMESPACE`, Docker Hub `neurobagel/query_tool:nightly` for the main Neurobagel repository). In nightly images the navbar shows the version `build:<commit>` instead of a release version.

### Releases

Tags: `query-tool-vX.Y.Z`. Published to: Docker Hub `neurobagel/query_tool`, and the site https://query.neurobagel.org.
Released by release-please: when a merged PR with a `feat` or `fix` commit changes `tools/query-tool/`, release-please adds query-tool to the repository's single, combined release PR, with the version bump and the new `tools/query-tool/CHANGELOG.md` entries. Merging that PR releases every tool in it: query-tool gets the tag `query-tool-vX.Y.Z` and its own GitHub release. Publishing to the channels above is not automated yet.
PR titles must follow Conventional Commits with scope `query-tool`, for example `fix(query-tool): ...`.

## License

The query tool is released under the terms of the [MIT License](LICENSE)
