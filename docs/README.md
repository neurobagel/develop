# Neurobagel Documentation

[![Docs](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/docs.yml?branch=main&style=flat-square&logo=github&label=docs)](https://github.com/neurobagel/develop/actions/workflows/docs.yml?query=branch%3Amain)
[![Python versions static](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?style=flat-square&logo=python)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/documentation?style=flat-square&color=purple&link=LICENSE)](LICENSE)

The neurobagel documentation.

Our docs are built with the [Material Theme](https://squidfunk.github.io/mkdocs-material/) for [MKdocs](https://www.mkdocs.org/).

## Setup

The docs live in `docs/` of the Neurobagel monorepo; run all commands below from `docs/`.

Create a new virtual environment with `python -m venv venv` and activate it.
Then install the dependencies with `pip install -r requirements.txt`

## Adding new pages to the navigation

We use [`mkdocs-awesome-nav`](https://lukasgeiter.github.io/mkdocs-awesome-nav/) to define the navigation structure of the docs.

To add a new page, add it to the `.nav.yml` (structured the same way as the `nav` section of `mkdocs.yml`) of the directory the markdown file lives in.

To add an entire subdirectory (section) of pages, you can simply specify the subdirectory name, e.g.:

```yml
  - User guide: user_guide
```

Each subdirectory can then itself contain a `.nav.yml` to organize the pages within.

Note: Both relative and absolute paths can be used to specify files or directories in `.nav.yml`.

## Updating the environment variables reference

The environment variables reference is auto-rendered from the file `docs/includes/environment_variables.yaml` using a [macro](https://mkdocs-macros-plugin.readthedocs.io/en/latest/) stored in `docs/macros/main.py`.

To update the metadata for a variable, directly edit the source yaml file.

To update the formatting of the rendered markdown reference sections, edit the macro functions inside the macro module directly.

**Variable ordering**: The order of variable sections is defined in the macro module.
For a given `ini_section`, variables appear in the order they are defined in the yaml file.

Information on excluding markdown sections or pages from macro rendering can be found [here](https://mkdocs-macros-plugin.readthedocs.io/en/latest/rendering/#solutions).

## Build

To spin up the site locally while you edit it, run:

`mkdocs serve`

More details are in the [mkdocs documentation](https://squidfunk.github.io/mkdocs-material/creating-your-site/#previewing-as-you-write).

## Deploy

Deployment is automatic: when a pull request that changes `docs/` is merged to `main`,
the `docs.yml` workflow builds the site and publishes it to GitHub Pages.

## Installing tailwind

To install tailwind, run:

```bash
npm i
```

## Rebuilding tailwind

If you need to rebuild the tailwind css, run:

```bash
npx tailwindcss build docs/stylesheets/tailwind.css -o docs/stylesheets/output.css
```

## Development in the Neurobagel monorepo

The docs live in `docs/` of https://github.com/neurobagel/develop.

### Setup

```bash
git clone https://github.com/neurobagel/develop.git
cd develop/docs
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Build

From `docs/`, build the site the way CI does, failing on any warning:

```bash
mkdocs build --strict
```

The build clones `query-tool-results/` from https://github.com/neurobagel/neurobagel_examples, so it needs network access.

CI runs this build on every pull request that changes `docs/`, and deploys the site to GitHub Pages when such a pull request is merged to `main`.

### Releases

The docs are not versioned or released; every merge to `main` that changes `docs/` deploys the site.

## Style guide

We use several tools in this repository to enforce our style guide (codespell, prettier, markdownlint...).
They can all be run in an orchestrated manner using [pre-commit](https://pre-commit.com/) python package.

The hooks are configured in `.pre-commit-config.yaml` in this folder.
In the monorepo, pre-commit only reads a configuration at the repository root,
so these hooks do not run on commit and are not checked in CI at the moment.

For markdownlint, you can also use
the [VS-code extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
to flag (and sometimes autofix)
potential formatting errors in your markdown file.
