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
just check-unchanged  # check that imported tools' source and tests are unchanged
```

`just lint` needs [actionlint](https://github.com/rhysd/actionlint) and [shellcheck](https://www.shellcheck.net/).

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
