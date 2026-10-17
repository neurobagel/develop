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

```bash
just --list           # show all recipes
just lint             # lint GitHub workflows and shell scripts
just check-unchanged  # check that imported tools' source and tests are unchanged
```

`just lint` needs [actionlint](https://github.com/rhysd/actionlint) and [shellcheck](https://www.shellcheck.net/).

## Migration

`migration/` holds the migration's records: the upstream test baseline, the paths that must stay unchanged, and the imported upstream commits. `scripts/` holds the scripts that import tools and check them.

## Changes from the standalone repositories

| ID | What changed | Why | Affected tools | Details |
| --- | --- | --- | --- | --- |
