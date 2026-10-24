# Baseline of the upstream repositories

Recorded 2026-10-17 from fresh clones of `https://github.com/neurobagel/<repo>` (`git clone --recurse-submodules`, default branch `main`). Every later "matches baseline" check compares against these counts.

## Upstream heads

| Repo | Commit | Commits (all / first-parent) | Tags (all `v*`) |
| --- | --- | --- | --- |
| federation-api | `570510a342df484cb5e412ce1d14f377389fd69d` | 221 / 214 | 21 |
| api | `0375375c88b3835d5171aa3ad610b13549e14775` | 502 / 382 | 25 |
| bagel-cli | `9d50d2e1002105f755b4029b79aa88f89aa70ceb` | 593 / 504 | 38 |
| query-tool | `b3366bb125a91e8f15ac621bd735432d08bb158c` | 640 / 635 | 36 |
| annotation-tool | `23767c40b2787b7f0ec16b392655fbbbc0cf3cf8` | 362 / 344 | 32 |
| documentation | `eaa741126217cb0f6e6d14766d93d9798d360e85` | 261 / 222 | 0 |
| neurobagel_examples | `9886428f9e4dbbe267e7f1d7fb3be265a4e62b03` | 90 | 0 |

## Submodule pins at these heads

| Repo | Path | Commit |
| --- | --- | --- |
| api | `recipes` | `389d0b719ebc641e3a329112b64305fa7889023f` (recipes `v0.9.1-9`) |
| api | `neurobagel_examples` | `25009a1e6edcf50f66df5db68f29f35c9683f7e4` |
| bagel-cli | `bagel/communities` | `5a186c7b1c0699444f30b33885429c48f188731f` |
| bagel-cli | `bagel/pipeline-catalog` | `8cb5730510de23538452ecbe7d0db4881c2e5f8b` |
| bagel-cli | `tests/bids-examples` | `a94600688a6d34a4496e049363d22d76a303d08f` |
| bagel-cli | `tests/neurobagel_examples` | `9886428f9e4dbbe267e7f1d7fb3be265a4e62b03` |
| query-tool | `neurobagel_examples` | `9886428f9e4dbbe267e7f1d7fb3be265a4e62b03` |
| query-tool | `recipes` | `9f8db034c9586abbd8c91c4c1216928ceedec312` (recipes `v0.9.1`) |

## Results

Commands are the ones each repository's CI runs. Coverage flags (`--cov ...`) and the Codecov upload were omitted; they do not change test counts.

### federation-api

`uv sync --group dev && uv run pytest`

| Python | Result |
| --- | --- |
| 3.10 | 111 passed |
| 3.11 | 111 passed |
| 3.12 | 111 passed |
| 3.13 | 111 passed |

### api

Test graph: `docker compose up -d test_graph export_datasets_metadata`, then wait for `FINISHED UPLOADING DATA` in the `api-test_graph-1` logs (took 22 s).

`uv sync --group dev && uv run pytest -m "integration or not integration"`

| Python | Result |
| --- | --- |
| 3.10 | 188 passed |
| 3.11 | 188 passed |
| 3.12 | 188 passed |
| 3.13 | 188 passed |

Without the integration marker (`uv run pytest`, Python 3.13): 182 passed, 6 deselected.

### bagel-cli

`uv sync --group dev --upgrade && uv run pytest -m "integration or not integration"`

| Python | Result |
| --- | --- |
| 3.11 | 215 passed |
| 3.12 | 215 passed |
| 3.13 | 215 passed |
| 3.14 | 215 passed |

### query-tool

Node 20.20.2, Cypress 15.21.1.

| Check | Command | Result |
| --- | --- | --- |
| Install | `npm ci` | OK |
| ESLint | `npm run lint:check` | OK |
| Prettier | `npm run format:check` | OK |
| Typecheck | `npm run typecheck` | OK |
| Codespell | `codespell` (before `npm ci`, as in CI) | OK |
| Build | `.env` = `NB_API_QUERY_URL=https://federate.neurobagel.org/`; `npm run build` | OK |
| Component | `cypress run --component` | 89 passed, 0 failed (18 specs) |
| E2E | `.env` = `NB_API_QUERY_URL=https://federate.neurobagel.org/`, `NB_ENABLE_AUTH=true`, `NB_QUERY_CLIENT_ID=mockclientid`; `npm install && npm run build`; `npm run preview`; `cypress run --e2e` against `http://localhost:5173` | 40 passed, 0 failed (9 specs) |

### annotation-tool

Node 20.20.2, Cypress 15.21.1.

| Check | Command | Result |
| --- | --- | --- |
| Install | `npm ci` | OK |
| Typecheck | `npm run typecheck` | OK |
| ESLint | `npm run lint:check` | OK |
| Prettier | `npm run format:check` | OK |
| Codespell | `codespell` | OK |
| Unit | `npm run test:unit` | 240 passed (29 files) |
| Component | `npm install && npm run build`; `cypress run --component` | 180 passed, 0 failed (37 specs) |
| E2E | `.env` = `NB_DISABLE_CONFIG=false`; `npm install && npm run build`; `npm run preview`; `cypress run --e2e` | 20 passed, 0 failed (15 specs) |
| Link check | lychee | Not run locally (depends on external sites) |

### documentation

Python 3.10 (as in upstream CD).

| Check | Command | Result |
| --- | --- | --- |
| Build | `pip install -r requirements.txt && mkdocs build` | OK, 0 warnings |
| Strict build | `mkdocs build --strict` | OK |

## Upstream pre-commit configs

`pre-commit run --all-files` with each repository's own config, for reference in Step 8:

| Repo | Result |
| --- | --- |
| federation-api | Passed |
| api | Passed |
| bagel-cli | Passed |
| documentation | Fails upstream: `markdown-link-check` reports `https://osf.io/preprints/metaarxiv/x64tn_v1` in `docs/cite.md` as dead (HTTP 503). External and network-dependent; not the migration's to fix. All other hooks pass. |

## Already failing upstream

None of the test suites as CI runs them. One suite fails upstream when run as its README says rather than as CI does (found in Step 10, 2026-10-24):

- bagel-cli on Python 3.11 with the locked dependencies (`uv sync --group dev`, no `--upgrade`): `ImportError while loading conftest` — `tests/conftest.py` imports `bids2table`, whose `_pathlib.py` creates a cloudpathlib `S3Client` at import time; on Python < 3.12 the lock pins `cloudpathlib` 0.20.0 without `boto3`, so it raises `NameError: name 'Session' is not defined`. Identical at upstream `9d50d2e`. Python 3.13 with the lock passes (215), and so does 3.11 with `--upgrade` (215), which is what upstream CI and this repository's CI run.

Three checks fail upstream:

- The documentation `markdown-link-check` hook above.
- query-tool `docker compose --profile test config --quiet` (found in Step 5, 2026-10-17), at query-tool `b3366bb` with recipes `v0.9.1`:

  ```
  service "graph" depends on undefined service "init_data": invalid compose project
  ```

  (The monorepo reports the same problem for `api`; compose picks the first service it finds.) query-tool's `docker-compose.yml` extends recipes' `api` and `graph` services, which depend on an `init_data` service that query-tool's file does not define. Upstream CI never uses this compose file. Fixed in migration Step 7a.
- api's linkspector check (found in Step 7d, 2026-10-17, linkspector 0.4.7 at api `0375375`): 55 working links, 1 failed: `README.md:41: http://purl.bioontology.org/ontology/SNOMEDCT/248152002 Status:403`. The link is external; upstream's workflow reports it as a check annotation on added lines only and does not fail the job.

## Environment and deviations

- Local runs happen in a rootless container. The Docker engine is the host's rootless Podman 6.1.2, driven through the Docker CLI (29.9.1) and compose (v5.6.0). `docker build` runs on BuildKit through buildx's docker-container driver.
- Cypress runs in `cypress/included:15.21.1` with `--network=host` and the checkout bind-mounted, because the container lacks the GUI libraries Cypress needs. CI uses `cypress-io/github-action`. The specs and results are the same.
- Codespell was run with `uvx codespell`, not `codespell-project/actions-codespell`.
- `rsync` is not available locally.
