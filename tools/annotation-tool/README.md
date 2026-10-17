<div align="center">

# Annotation Tool

[![Website](https://img.shields.io/website?label=staging%20app&up_message=live&style=flat-square&url=https%3A%2F%2Fstaging-annotate.netlify.app)](https://staging-annotate.netlify.app/)
[![CI](https://img.shields.io/github/actions/workflow/status/neurobagel/develop/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/neurobagel/develop/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/annotation-tool?style=flat-square&logo=codecov&link=https%3A%2F%2Fapp.codecov.io%2Fgh%2Fneurobagel%2Fannotation-tool)](https://app.codecov.io/gh/neurobagel/annotation-tool)
[![Node version](https://img.shields.io/badge/node-20-green?style=flat-square&logo=nodedotjs)](https://nodejs.org/en)
[![License](https://img.shields.io/github/license/neurobagel/annotation-tool?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/neurobagel/annotation-tool?style=flat-square&label=openssf%20scorecard)](https://scorecard.dev/viewer/?uri=github.com/neurobagel/annotation-tool)

The annotation tool is a React application, developed in [TypeScript](https://www.typescriptlang.org/) using a variety of tools including [Vite](https://vite.dev/), [Cypress](https://www.cypress.io/), and [MUI](https://mui.com/).

[Quickstart](#quickstart) |
[Local Installation](#local-installation) |
[Usage](#usage) |
[Configuration](#configuration) |
[Testing](#testing) |
[Development in the Neurobagel monorepo](#development-in-the-neurobagel-monorepo) |
[License](#license)

</div>

## Quickstart

The staging version of the annotation tool is hosted at [https://staging-annotate.netlify.app/](https://staging-annotate.netlify.app/).

## Local Installation

### Building and running

From `tools/annotation-tool/` in a clone of the [Neurobagel monorepo](https://github.com/neurobagel/develop):

```bash
# Install dependencies
$ npm install

# Serve with hot module replacement at localhost:5173
$ npm run dev

# Build for production and launch server
$ npm run build
$ npm run preview
```

## Usage

1. Upload your data table (.tsv) file (and/or data dictionary)
2. Annotate the columns
   - Add/edit the column description
   - Select the data type (categorical or continuous) of the column
   - Map columns to Neurobagel standardized variables
3. Annotate the values of the annotated columns
   - Add/edit levels' description (if column data type is categorical) or units description (if column data type is continuous)
4. Download an annotated version of a BIDS-valid data dictionary for your dataset

## Configuration

The annotation tool is designed to be highly configurable, allowing it to adapt to different research contexts and data standards. You can define your own set of standardized variables and vocabularies to match your specific needs.
For detailed technical information about creating and customizing configurations, see the [Configuration Guide](CONFIGURATION.md).

## Testing

The Annotation tool uses [Cypress](https://www.cypress.io/) for integration and component testing, and [Vitest](https://vitest.dev/) for unit testing.

## Development in the Neurobagel monorepo

This tool lives in `tools/annotation-tool/` of https://github.com/neurobagel/develop.

### Setup

```bash
git clone https://github.com/neurobagel/develop.git
cd develop/tools/annotation-tool
npm ci
```

Commit hooks (husky and lint-staged) do not run in the monorepo: husky only installs hooks at the root of a git repository. Run the checks below before committing.

### Tests

From `tools/annotation-tool/`, the static checks and unit tests:

```bash
npm run lint:check
npm run format:check
npm run typecheck
npm run test:unit
```

Component tests:

```bash
npm run build
npm run test:component
```

End-to-end tests run against the production build served by `npm run preview` on port 5173:

```bash
echo "NB_DISABLE_CONFIG=false" > .env
npm run build
```

Then start the preview server in a second terminal, also from `tools/annotation-tool/`:

```bash
npm run preview
```

and run the tests in the first one:

```bash
npm run test:e2e
```

Stop the preview server with Ctrl+C when done.

From the repository root, `just test annotation-tool` runs `npm ci`, the static checks, the unit tests and the component tests. CI runs everything above, plus codespell and a [lychee](https://lychee.cli.rs/) link check configured by `lychee.toml`, whenever a pull request changes `tools/annotation-tool/`.

### Docker image

The annotation tool has no Docker image. It is deployed as a static site.

### Releases

Tags: `annotation-tool-vX.Y.Z`. Published to: the site https://annotate.neurobagel.org.
Release automation (release-please) is not set up in this repository yet, so no releases are made from it.
PR titles must follow Conventional Commits with scope `annotation-tool`, for example `fix(annotation-tool): ...`.

## License

The Neurobagel Annotation tool uses the [MIT License](https://github.com/neurobagel/annotation-tool/blob/main/LICENSE).
