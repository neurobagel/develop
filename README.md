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

## Running the full stack

Build the api, federation-api and query-tool images from this checkout and run them together:

```bash
just dev       # one local node: node API on 8000, federation API on 8080, query tool on http://localhost:3000
just dev-down  # stop it
```

`just dev` uses `stack/` (a development copy of [neurobagel/recipes](https://github.com/neurobagel/recipes)) with the images tagged `:local`. It creates `stack/.env` and `stack/local_nb_nodes.json` from their templates if they do not exist.

The full-stack tests in `e2e/` and the example API responses in `examples/` use a two-node deployment instead (`scripts/test-nodes.sh`):

```bash
just e2e        # build the images, start the two nodes, run the Cypress tests in e2e/
just examples   # build the images and regenerate examples/api-responses/
just test-nodes down
```

These deployments use the same ports, so run one at a time.

## Commit hooks

One [pre-commit](https://pre-commit.com/) configuration at the root, `.pre-commit-config.yaml`, holds every tool's hooks, each scoped to its folder and using the tool's own config files. Install it once:

```bash
pip install pre-commit   # or: uv tool install pre-commit
pre-commit install
```

This installs two git hooks: `pre-commit` runs the checks on every commit, and `post-merge` runs `npm ci` in a frontend after a merge or pull that changed its `package.json` or `package-lock.json`, so local `node_modules` stay in sync.

The frontends' hooks run their `lint-staged` configs and need `npm ci` in `tools/query-tool/` and `tools/annotation-tool/` (they fail with that instruction otherwise). To run all hooks on all files:

```bash
(cd tools/query-tool && npm ci) && (cd tools/annotation-tool && npm ci)
SKIP=markdown-link-check-docs pre-commit run --all-files
```

## Dependency updates

One `.github/dependabot.yml` covers every tool, checked weekly:

| Ecosystem | Folders | Updates |
| --- | --- | --- |
| npm | `tools/query-tool`, `tools/annotation-tool`, `docs` | Version updates, grouped into production and development dependencies across the folders; semver-major updates ignored |
| uv | `tools/api`, `tools/federation-api`, `tools/bagel-cli` | Security updates only |
| pip | `docs` | Security updates only |
| docker | the four Dockerfiles in `tools/` | Base images, grouped; major updates ignored, and minor updates of `python` (which change the Python version) ignored |
| gitsubmodule | bagel-cli's three submodules | Pin updates, grouped |
| github-actions | workflows and `.github/actions/` | Version updates |

Each pull request runs CI only for the folders it touches.

## Releases

Each tool is versioned and released on its own by [release-please](https://github.com/googleapis/release-please) (`release-please-config.json`, current versions in `.release-please-manifest.json`):

- Pull requests are squash-merged, and their title becomes the commit message, so titles must follow [Conventional Commits](https://www.conventionalcommits.org/), optionally with a tool as scope: `fix(api): ...`, `feat(query-tool): ...`. The `PR title` check enforces this.
- release-please looks at which tool folders each commit on `main` changed. It keeps **one combined release PR** open (`chore: release main`) with a section for every tool that has `feat` or `fix` commits since its last release: each tool's own version bump and `CHANGELOG.md` entries. Before 1.0, a breaking change (`feat!:`) bumps the minor version.
- Merging the release PR releases all tools in it at once: each gets its own tag `<tool>-vX.Y.Z` and its own GitHub release. A single tool cannot be released while other tools have pending changes.
- **Pull requests that change several tools:** release-please assigns a commit to every tool whose folder it changes, and ignores the commit scope. A squash-merged PR therefore gives every tool it touches the same changelog entry and the same version bump, and a `BEGIN_COMMIT_OVERRIDE` block in the PR description cannot direct entries to individual tools (each line of the block applies to all touched tools). This is harmless for `chore`, `build`, `ci`, `docs` and `test` PRs, and for one change that applies to every tool alike. For a PR with different `feat`/`fix` changes in different tools, either split it into one PR per tool, or give it one commit per tool (each touching only that tool) and merge it with a merge commit rather than squashing (with a merge commit, `main`'s first-parent history keeps only CI-tested states). The project has not yet chosen a policy for these PRs.
- release-please reads a commit override from anywhere in a merged PR's description: do not paste example override blocks into PR descriptions.
- `docs`, `chore`, `build`, `ci`, `test` and `refactor` commits do not cause releases. The CI job `release-preview` shows what release-please would propose.

## Repository-wide workflows

| Workflow | What it does |
| --- | --- |
| `ci.yml` | Runs the pre-commit hooks (and the docs link check, non-blocking), lints workflows and scripts, detects which tools a change touches, runs those tools' tests, and checks that imported source and tests are unchanged |
| `docs.yml` | Builds the docs on pull requests and deploys them to GitHub Pages on merge |
| `e2e.yml` | Runs the full-stack tests in `e2e/` against a two-node deployment of the images built from the pull request |
| `nightly.yml` | On push to `main`: rebuilds and pushes `:nightly` images (amd64 and arm64) of the tools whose image inputs changed, to `IMAGE_REGISTRY`/`IMAGE_NAMESPACE` |
| `release.yml` | On push to `main` (or by hand): runs release-please (the combined release PR; tags and GitHub releases when it is merged) |
| `pr-title.yml` | Checks that PR titles follow Conventional Commits |
| `examples.yml` | Started by hand: regenerates `examples/api-responses/` from the images built from `main` and opens a pull request if they changed |
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
| Step 8 | One root `.pre-commit-config.yaml` replaces the per-tool configs of api, federation-api, bagel-cli and docs, and the frontends' husky hooks; CI runs it on every pull request | pre-commit only reads a config at the repository root, and husky only installs hooks there | all | [Commit hooks](#commit-hooks) |
| Step 9 | One root `.github/dependabot.yml` replaces the tools' identical per-repository files; updates of the same group across tools arrive in one pull request; Dependabot also updates Docker base images (new) | One configuration for all tools; fewer, grouped update PRs | all | [Dependency updates](#dependency-updates) |
| R4 (Step 9) | Dependabot proposes pin updates for bagel-cli's external submodules (`tests/bids-examples`, `bagel/pipeline-catalog`, `bagel/communities`) weekly, grouped in one PR; a CI job checks that the wheel still bundles `communities` and `pipeline-catalog` | Replaces manual pin bumps while keeping the external repositories' provenance | bagel-cli | [bagel-cli README: Setup](tools/bagel-cli/README.md#setup) |
| Step 10 | `just dev` runs the stack from `stack/` with images built from the checkout; recipes' full-stack Cypress tests live in `e2e/` and run in CI (`e2e.yml`) against a two-node deployment of the PR's images (`scripts/test-nodes.sh`), federating over the two local nodes only | Full-stack tests now test the code in the same commit, not published images | api, federation-api, query-tool | [Running the full stack](#running-the-full-stack), [e2e/README.md](e2e/README.md) |
| R5 (Step 10) | The example API responses are generated in this repository from the APIs built from the current commit (`just examples`, `examples.yml`), instead of from published images in neurobagel_examples | An API change and its updated example responses land in one PR | api, federation-api, examples | [examples/README.md: Example API responses](examples/README.md#example-api-responses) |
| Step 11 | Nightly images are built by one root workflow from the root build context, only for tools whose image inputs changed, for linux/amd64 and linux/arm64 (query-tool was amd64 only), to the registry set by repository variables; bagel-cli's nightly image installs the wheel built in the same run (R3) | GitHub only runs root workflows; one place for registry configuration | api, federation-api, query-tool, bagel-cli | [Repository-wide workflows](#repository-wide-workflows) |
| Step 12 | Releases are cut per tool by release-please from Conventional Commits PR titles, instead of intuit/auto with PR labels, through one combined release PR; PRs are squash-merged | auto supports one package per repository | all tools | [Releases](#releases) |
