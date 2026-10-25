<div align="center">

# Neurobagel CLI

[![CI](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/neurobagel/develop/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/bagel-cli?token=R1KI9KIP8D&style=flat-square&logo=codecov&link=https%3A%2F%2Fcodecov.io%2Fgh%2Fneurobagel%2Fbagel-cli)](https://app.codecov.io/gh/neurobagel/bagel-cli)
[![Python versions static](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat-square&logo=python)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/bagel-cli?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/bagel?style=flat-square&logo=pypi&link=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Fbagel)](https://pypi.org/project/bagel/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/bagel?style=flat-square&logo=python&label=pypi%20downloads&link=https%3A%2F%2Fpypistats.org%2Fpackages%2Fbagel)](https://pypistats.org/packages/bagel)
[![Docker Image Version (tag)](https://img.shields.io/docker/v/neurobagel/bagelcli/latest?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fbagelcli%2Ftags)](https://hub.docker.com/r/neurobagel/bagelcli/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurobagel/bagelcli?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Fbagelcli%2Ftags)](https://hub.docker.com/r/neurobagel/bagelcli/tags)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/neurobagel/bagel-cli?style=flat-square&label=openssf%20scorecard)](https://scorecard.dev/viewer/?uri=github.com/neurobagel/bagel-cli)

</div>

The Neurobagel CLI is a Python command-line tool to automatically parse and describe subject phenotypic and imaging attributes in an annotated dataset for integration into the Neurobagel graph.

**For information on how to use the CLI, please refer to the [official Neurobagel documentation](https://neurobagel.org/user_guide/cli/).**

## Installation
The Neurobagel CLI is available as a Python package that can be installed from PyPI using:

```bash
pip install bagel
```

(If you prefer to run the CLI using Docker or Singularity containers instead, please refer to the [Neurobagel documentation](https://neurobagel.org/user_guide/cli/).)

## Development in the Neurobagel monorepo

This tool lives in `tools/bagel-cli/` of https://github.com/neurobagel/develop.

### Setup

To work on the CLI, we suggest a development environment that is as close as possible to the one we run in production.
We [use uv](https://docs.astral.sh/uv/getting-started/installation/) to set up local development environments.

Clone with submodules, then install the CLI and all development dependencies in editable mode:

```bash
git clone --recurse-submodules https://github.com/neurobagel/develop.git
cd develop/tools/bagel-cli
uv sync --group dev
```

If you already cloned without `--recurse-submodules`, run `git submodule update --init` from the repository root.

bagel-cli uses three external repositories as git submodules, registered in the repository's root `.gitmodules`:

| Path in `tools/bagel-cli/` | Repository | Used for |
| --- | --- | --- |
| `bagel/communities` | [neurobagel/communities](https://github.com/neurobagel/communities) | Community configurations, bundled into the package |
| `bagel/pipeline-catalog` | [nipoppy/pipeline-catalog](https://github.com/nipoppy/pipeline-catalog) | Processing pipeline catalog, bundled into the package |
| `tests/bids-examples` | [bids-standard/bids-examples](https://github.com/bids-standard/bids-examples) | Example BIDS datasets for the tests |

Dependabot checks these three submodules weekly and proposes pin updates together in one pull request, which runs bagel-cli's tests and a check that the wheel still contains `bagel/communities/` and `bagel/pipeline-catalog/`. To update a pin by hand instead, check out the new commit in the submodule and commit the changed submodule path.

The Neurobagel example data used by the tests comes from the monorepo's `examples/` folder through the symlink `tests/neurobagel_examples -> ../../../examples`.

The version is derived from the repository's `bagel-cli-v*` tags, so the clone needs its full history and tags (the default for `git clone`).

To check your changes on every commit, install the repository's commit hooks (configured in the root `.pre-commit-config.yaml`; the bagel-cli hooks are black, flake8, isort, codespell and the other checks bagel-cli used before):

```bash
uv run pre-commit install
```

To run the CLI during local development, from `tools/bagel-cli/`:

```bash
uv run bagel
```

### Tests

From `tools/bagel-cli/`:

```bash
uv run pytest -m "integration or not integration"
```

Or from the repository root: `just test bagel-cli`. CI runs the tests on Python 3.11 to 3.14 whenever a pull request changes `tools/bagel-cli/`, `examples/` or `.gitmodules`. Like the upstream repository's CI, it installs with `uv sync --group dev --upgrade`, so it also tests against the newest allowed dependency versions.

### Package

From `tools/bagel-cli/`:

```bash
uv build
```

The wheel bundles `bagel/communities/` and `bagel/pipeline-catalog/`; the source distribution leaves out `tests/`.

### Docker image

The `neurobagel/bagelcli` image contains exactly the `bagel` wheel that is
published to PyPI for the same version. Nightly images contain the wheel
built from `main` at that commit: every push to `main` that changes bagel-cli
builds the wheel once and then `<registry>/<namespace>/bagelcli:nightly` from it,
for linux/amd64 and linux/arm64 (`.github/workflows/nightly.yml`; registry and
namespace come from the repository variables `IMAGE_REGISTRY` and
`IMAGE_NAMESPACE`, Docker Hub `neurobagel/bagelcli:nightly` for the main
Neurobagel repository). Its `--version` is a `.devN` version after the last
`bagel-cli-v*` tag.

How the image is built:
- The release workflow builds the wheel once.
- It uploads that wheel to PyPI.
- It then builds the Docker image from the same wheel file.
- If the PyPI upload fails, no image is pushed.

The image no longer runs `pip install bagel` from PyPI while building.
So the build does not depend on PyPI having the new release yet, and the
image cannot end up with a different version than its tag.

Using the image is unchanged: `docker pull neurobagel/bagelcli`,
`docker run --rm neurobagel/bagelcli --help`, and Apptainer via
`apptainer pull bagel.sif docker://neurobagel/bagelcli`.

Build the image locally (from the repository root):

```bash
rm -rf tools/bagel-cli/dist
(cd tools/bagel-cli && uv build --wheel)
docker build -f tools/bagel-cli/Dockerfile -t neurobagel/bagelcli:local .
```

`just build bagel-cli` runs the same three commands. The build context is the repository root; `tools/bagel-cli/Dockerfile.dockerignore` lets in only the wheel, and the build fails unless `tools/bagel-cli/dist/` holds exactly one.

Check which version an image contains:

```bash
docker run --rm neurobagel/bagelcli:<tag> --version
```

### Releases

Tags: `bagel-cli-vX.Y.Z`. Published to: PyPI `bagel`, Docker Hub `neurobagel/bagelcli`.
Release automation (release-please) is not set up in this repository yet, so no releases are made from it.
PR titles must follow Conventional Commits with scope `bagel-cli`, for example `fix(bagel-cli): ...`.

### Updating dependencies
If new runtime or development dependencies are needed, [add them with `uv add`](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies). 
To change the version constraints of existing dependencies,
edit `pyproject.toml` and then update the lockfile using
[`uv lock`](https://docs.astral.sh/uv/concepts/projects/sync/#creating-the-lockfile).

## Regenerating the Neurobagel vocabulary file
Terms in the Neurobagel namespace (`nb` prefix) and their class relationships are serialized to a file 
called [nb_vocab.ttl](https://github.com/neurobagel/recipes/blob/main/vocab/nb_vocab.ttl), which is automatically
uploaded to new Neurobagel graph deployments.
This vocabulary is used by Neurobagel APIs to fetch available attributes and attribute instances from a graph store.

When the Neurobagel graph data model is updated (e.g., if new classes or subclasses are created), 
this file should be regenerated by running, from `tools/bagel-cli/`:
```bash
uv run python helper_scripts/generate_nb_vocab_file.py
```
This will create a file called `nb_vocab.ttl` in the current working directory.
