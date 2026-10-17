# Neurobagel

> **Test run.** This repository is a sandbox for migrating Neurobagel's tool repositories into one monorepo. Its history, tags, images and releases are for rehearsal only and go to test channels. Do not use it in place of the tool repositories under https://github.com/neurobagel yet.

Neurobagel is a distributed data discovery network. This repository will hold its core tools, each as an independent project with its own source, tests, version and releases:

| Folder | Tool |
| --- | --- |
| `tools/api` | Node API |
| `tools/federation-api` | Federation API |
| `tools/bagel-cli` | `bagel` CLI for preparing metadata |
| `tools/query-tool` | Query tool web app |
| `tools/annotation-tool` | Annotation tool web app |
| `docs` | Documentation site |
| `examples` | Example data used by the tools' tests |
| `stack` | Docker Compose stack for development and tests |

Folders are added as each tool is imported.

## Working in this repository

Tasks are run with [just](https://github.com/casey/just) from the repository root:

Some tools use external git submodules, so clone with `git clone --recurse-submodules`.

```bash
just --list           # show all recipes
just lint             # lint GitHub workflows and shell scripts
just test <tool>      # run a tool's tests, for example `just test federation-api`
just build <tool>     # build a tool's Docker image from the repository root, tagged neurobagel/<image>:local
just check-unchanged  # check that imported tools' source and tests are unchanged
```

`just lint` needs [actionlint](https://github.com/rhysd/actionlint) and [shellcheck](https://www.shellcheck.net/).

## Repository-wide workflows

| Workflow | What it does |
| --- | --- |
| `ci.yml` | Lints workflows and scripts, detects which tools a change touches, runs those tools' tests, and checks that imported source and tests are unchanged |
| `docs.yml` | Builds the docs on pull requests and deploys them to GitHub Pages on merge |
| `linkspector.yml` | Checks the links in api's `README.md` (configured by `tools/api/.linkspector.yml`) on changes to api's Markdown |

## Migration

`migration/` holds the migration's records: the upstream test baseline, the paths that must stay unchanged, and the imported upstream commits. `scripts/` holds the scripts that import tools and check them.

## Changes from the standalone repositories

| ID | What changed | Why | Affected tools | Details |
| --- | --- | --- | --- | --- |
| Step 2 | federation-api imported with full history; tags renamed from `vX.Y.Z` to `federation-api-vX.Y.Z`; hatch-vcs reads versions from those tags at the repository root; CI moved to the root `ci.yml` and `test-python.yml` | One tag namespace per tool in a shared repository; GitHub only runs root workflows | federation-api | [README: Development in the Neurobagel monorepo](tools/federation-api/README.md#development-in-the-neurobagel-monorepo) |
| Step 3 | `neurobagel_examples` imported with full history into `examples/` | Example data is versioned with the tools that test against it | api, bagel-cli, query-tool | [examples/README.md](examples/README.md) |
| Step 3 | `recipes` copied without history into `stack/` as the development and test stack, at the commit api pinned | The tools' test stacks come from one shared folder instead of per-tool submodules | api, query-tool | [stack/SOURCE.md](stack/SOURCE.md) |
| Step 3 | api imported with full history; tags renamed to `api-vX.Y.Z`; its `recipes` and `neurobagel_examples` submodules replaced by symlinks to `stack/` and `examples/` | Submodules declared in a subfolder's `.gitmodules` are ignored by git | api | [README: Development in the Neurobagel monorepo](tools/api/README.md#development-in-the-neurobagel-monorepo) |
| Step 4 | bagel-cli imported with full history; tags renamed to `bagel-cli-vX.Y.Z`; its `bids-examples`, `pipeline-catalog` and `communities` submodules registered in the root `.gitmodules`; its `neurobagel_examples` submodule replaced by a symlink to `examples/` | Submodules declared in a subfolder's `.gitmodules` are ignored by git; example data comes from `examples/` | bagel-cli | [README: Development in the Neurobagel monorepo](tools/bagel-cli/README.md#development-in-the-neurobagel-monorepo) |
| Step 5 | query-tool imported with full history; tags renamed to `query-tool-vX.Y.Z`; its `recipes` and `neurobagel_examples` submodules replaced by symlinks to `stack/` and `examples/`; its Docker image built from a copy of the folder with symlinks resolved | Submodules declared in a subfolder's `.gitmodules` are ignored by git; Docker does not follow symlinks out of the build context | query-tool | [README: Development in the Neurobagel monorepo](tools/query-tool/README.md#development-in-the-neurobagel-monorepo) |
| Step 6 | annotation-tool imported with full history; tags renamed to `annotation-tool-vX.Y.Z`; its CI (static checks, unit, component and e2e tests, lychee link check) moved to the root `ci.yml` and `test-node.yml` | One tag namespace per tool; GitHub only runs root workflows | annotation-tool | [README: Development in the Neurobagel monorepo](tools/annotation-tool/README.md#development-in-the-neurobagel-monorepo) |
| Step 7 | documentation imported with full history into `docs/`; the site is built on pull requests and deployed with `actions/deploy-pages` on merge, instead of `mkdocs gh-deploy` | GitHub only runs root workflows; one Pages site per repository | docs | [docs/README.md: Development in the Neurobagel monorepo](docs/README.md#development-in-the-neurobagel-monorepo) |
| R1 (Step 7a) | api and query-tool compose files refer to `../../stack` and `../../examples` directly; their `recipes` symlinks are removed. query-tool's `test` profile gains the `init_data` service and `neurobagel_data` volume it was missing, so it starts again, and its federation API mounts the committed `stack/local_nb_nodes.template.json` (the profile's own node API) instead of a `local_nb_nodes.json` that did not exist. | Makes the dependency on the shared stack explicit and removes two symlinks; query-tool's test profile was already broken upstream (see `migration/baseline.md`) | api, query-tool | [api README](tools/api/README.md#setup), [query-tool README](tools/query-tool/README.md#docker-compose-testing-environment-for-development) |
| R2 (Step 7b) | api, federation-api and query-tool images are built from the repository root (`docker build -f tools/<tool>/Dockerfile .`, or `just build <tool>`), with an allowlist `tools/<tool>/Dockerfile.dockerignore` per image; query-tool's Dockerfile copies `examples/` directly; the temporary `scripts/materialize-context.sh` is removed | Docker does not follow symlinks out of a tool folder; one build context for all images, with each image's files listed explicitly | api, federation-api, query-tool | [api](tools/api/README.md#docker-image), [federation-api](tools/federation-api/README.md#docker-image), [query-tool](tools/query-tool/README.md#docker-image) |
| R3 (Step 7c) | The bagel-cli image installs one pre-built wheel (`tools/bagel-cli/dist/*.whl`), the same file that is published to PyPI, instead of running `pip install bagel` from PyPI; `Dockerfile.nightly` is removed and nightly and release images share one Dockerfile | The image always contains exactly the released (or nightly) artifact, and the build no longer depends on PyPI having the new release yet | bagel-cli | [bagel-cli README: Docker image](tools/bagel-cli/README.md#docker-image) |
| Step 7d | api's link check runs from the root workflow `linkspector.yml`, in `tools/api`; the other upstream repository-automation workflows are not carried over (`handle_external_pr`, `add_iss2project`, `stale`, `scorecard`, query-tool's example-diff workflows) or are replaced later | GitHub only runs root workflows | api | [Repository-wide workflows](#repository-wide-workflows) |
