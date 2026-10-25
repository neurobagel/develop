# Source of this folder

`stack/` is a development and test copy of [neurobagel/recipes](https://github.com/neurobagel/recipes), copied without history.

| | |
| --- | --- |
| Source commit | `389d0b719ebc641e3a329112b64305fa7889023f` (`v0.9.1-9-g389d0b7`), the commit the api repository pinned as its `recipes` submodule |
| Copied with | `git archive 389d0b719ebc641e3a329112b64305fa7889023f \| tar -x -C stack` |
| Left out | `.github/`; `cypress/`, `cypress.config.js`, `package.json` and `package-lock.json`, the full-stack Cypress suite, which lives in `e2e/` (copied from the same commit) |

The query-tool repository pinned recipes `v0.9.1` (`9f8db034c9586abbd8c91c4c1216928ceedec312`). It differs from the commit above only in CI files, the Cypress test and the package files, none of which are in `stack/`.

`neurobagel/recipes` stays a separate repository for operators deploying Neurobagel.
