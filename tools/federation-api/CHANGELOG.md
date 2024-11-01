# v0.4.2 (Fri Nov 01 2024)

#### 🚀 Enhancements

- [FIX] Ensure token forwarded to n-APIs does not include an extra scheme string [#134](https://github.com/neurobagel/federation-api/pull/134) ([@alyssadai](https://github.com/alyssadai))

#### Authors: 1

- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))

---

# v0.4.1 (Thu Oct 31 2024)

#### 🚀 Enhancements

- [FIX] Ensure Google auth token is forwarded in request to n-API [#132](https://github.com/neurobagel/federation-api/pull/132) ([@alyssadai](https://github.com/alyssadai))

#### Authors: 1

- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))

---

# v0.4.0 (Thu Oct 24 2024)

#### 💥 Breaking Changes

- [ENH] Split `/attributes` into attribute-specific resources [#126](https://github.com/neurobagel/federation-api/pull/126) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Implemented `pipeline_name` and `pipeline_version` query params [#121](https://github.com/neurobagel/federation-api/pull/121) ([@rmanaem](https://github.com/rmanaem))

#### 🚀 Enhancements

- [ENH] Add route for fetching available versions of a pipeline across n-APIs [#125](https://github.com/neurobagel/federation-api/pull/125) ([@alyssadai](https://github.com/alyssadai))

#### 🐛 Bug Fixes

- [FIX] Allow only `"true"` or `None` for `is_control` query parameter [#129](https://github.com/neurobagel/federation-api/pull/129) ([@alyssadai](https://github.com/alyssadai))

#### 🏠 Internal

- [MNT] Removed build docker nightly workflow file [#114](https://github.com/neurobagel/federation-api/pull/114) ([@rmanaem](https://github.com/rmanaem))

#### 📝 Documentation

- [FIX] Docs link [#119](https://github.com/neurobagel/federation-api/pull/119) ([@surchs](https://github.com/surchs))

#### Authors: 3

- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))
- Arman Jahanpour ([@rmanaem](https://github.com/rmanaem))
- Sebastian Urchs ([@surchs](https://github.com/surchs))

---

# v0.3.0 (Fri Aug 02 2024)

#### 💥 Breaking Changes

- [FIX] Disable redirect slashes and remove trailing slashes from routes [#109](https://github.com/neurobagel/federation-api/pull/109) ([@alyssadai](https://github.com/alyssadai))
- Add authentication to `/query` route [#104](https://github.com/neurobagel/federation-api/pull/104) ([@alyssadai](https://github.com/alyssadai))

#### Authors: 1

- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))

---

# v0.2.1 (Thu Jun 20 2024)

#### 🚀 Enhancements

- [MNT] Add welcome page at / [#99](https://github.com/neurobagel/federation-api/pull/99) ([@alyssadai](https://github.com/alyssadai))

#### 🐛 Bug Fixes

- [FIX] Explicitly check that `local_nb_nodes.json` is an existing file [#98](https://github.com/neurobagel/federation-api/pull/98) ([@alyssadai](https://github.com/alyssadai))

#### Authors: 1

- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))

---

# v0.2.0 (Wed Jun 12 2024)

#### 🚀 Enhancements

- [ENH] Implemented `NB_FEDERATE_REMOTE_PUBLIC_NODES` env var [#90](https://github.com/neurobagel/federation-api/pull/90) ([@rmanaem](https://github.com/rmanaem))
- [MNT] Set default timeout to `None` [#94](https://github.com/neurobagel/federation-api/pull/94) ([@rmanaem](https://github.com/rmanaem))

#### Authors: 1

- Arman Jahanpour ([@rmanaem](https://github.com/rmanaem))

---

# v0.1.0 (Thu Apr 11 2024)

:tada: This release contains work from new contributors! :tada:

Thanks for all your work!

:heart: Arman Jahanpour ([@rmanaem](https://github.com/rmanaem))

:heart: Sebastian Urchs ([@surchs](https://github.com/surchs))

:heart: Alyssa Dai ([@alyssadai](https://github.com/alyssadai))

### Release Notes

#### [MNT] Release new data model ([#82](https://github.com/neurobagel/federation-api/pull/82))

We have updated the Neurobagel data model to allow users to specify phenotypic information at the session level (https://github.com/neurobagel/planning/issues/83). This release updates the federation API so it can understand the new node API responses.

---

#### 💥 Breaking Changes

- [ENH] Support partial term fetching failures [#65](https://github.com/neurobagel/federation-api/pull/65) ([@alyssadai](https://github.com/alyssadai))
- [ENH] split session query parameter into phenotypic + imaging [#64](https://github.com/neurobagel/federation-api/pull/64) ([@alyssadai](https://github.com/alyssadai))

#### 🚀 Enhancements

- [MNT] Release new data model [#82](https://github.com/neurobagel/federation-api/pull/82) ([@rmanaem](https://github.com/rmanaem))
- [MNT] Switch to using logging for all non-user warnings and errors [#77](https://github.com/neurobagel/federation-api/pull/77) ([@surchs](https://github.com/surchs))
- [DOC] Update Copyright holders [#71](https://github.com/neurobagel/federation-api/pull/71) ([@surchs](https://github.com/surchs))
- [CI] Update image tag for default build [#59](https://github.com/neurobagel/federation-api/pull/59) ([@alyssadai](https://github.com/alyssadai))
- [CI] Stop pre-commit auto-fixing PRs [#57](https://github.com/neurobagel/federation-api/pull/57) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Handle partial nodes success [#55](https://github.com/neurobagel/federation-api/pull/55) ([@alyssadai](https://github.com/alyssadai))
- [FIX] Update example config to use `host.docker.internal` instead of `localhost` [#50](https://github.com/neurobagel/federation-api/pull/50) ([@alyssadai](https://github.com/alyssadai))
- [ENH] partially validate local node JSON config [#43](https://github.com/neurobagel/federation-api/pull/43) ([@surchs](https://github.com/surchs) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- [FIX] Fix docker run command in README.md [#42](https://github.com/neurobagel/federation-api/pull/42) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Switch node config format [#39](https://github.com/neurobagel/federation-api/pull/39) ([@alyssadai](https://github.com/alyssadai))
- [REF] Refactor tests [#37](https://github.com/neurobagel/federation-api/pull/37) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Add new query param for nodes that defaults to a prepopulated index [#30](https://github.com/neurobagel/federation-api/pull/30) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Implemented new endpoint to return known node APIs [#29](https://github.com/neurobagel/federation-api/pull/29) ([@rmanaem](https://github.com/rmanaem))
- [CI] Set up coveralls [#24](https://github.com/neurobagel/federation-api/pull/24) ([@rmanaem](https://github.com/rmanaem))
- [MNT] Implemented logic to make sure node URLs end with `/` [#25](https://github.com/neurobagel/federation-api/pull/25) ([@rmanaem](https://github.com/rmanaem))
- [DOC] Update constraints and example for `NB_NODES` variable value [#22](https://github.com/neurobagel/federation-api/pull/22) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Changed the favicon to neurobagel logo [#20](https://github.com/neurobagel/federation-api/pull/20) ([@rmanaem](https://github.com/rmanaem))
- [CI] Set up `test` workflow [#17](https://github.com/neurobagel/federation-api/pull/17) ([@rmanaem](https://github.com/rmanaem))
- [ENH] Added node API vocabulary endpoints and logic [#14](https://github.com/neurobagel/federation-api/pull/14) ([@rmanaem](https://github.com/rmanaem))
- [DOCS] Added link to official docs [#16](https://github.com/neurobagel/federation-api/pull/16) ([@surchs](https://github.com/surchs))
- [FIX] Ensure the value of `NB_NODES` can be properly parsed as a list by the API [#11](https://github.com/neurobagel/federation-api/pull/11) ([@alyssadai](https://github.com/alyssadai))
- [FIX] Fix syntax error in docker workflow and add relevant pre-commit hook [#10](https://github.com/neurobagel/federation-api/pull/10) ([@alyssadai](https://github.com/alyssadai))
- [ENH] Set up federation prototype and CI workflows [#9](https://github.com/neurobagel/federation-api/pull/9) ([@rmanaem](https://github.com/rmanaem) [@surchs](https://github.com/surchs) [@alyssadai](https://github.com/alyssadai))
- [CI] Set up workflows [#7](https://github.com/neurobagel/federation-api/pull/7) ([@rmanaem](https://github.com/rmanaem))
- [ENH] Turned `NEUROBAGEL_NODES` to an env var [#6](https://github.com/neurobagel/federation-api/pull/6) ([@rmanaem](https://github.com/rmanaem))
- [MNT] Cleaned up the existing code [#3](https://github.com/neurobagel/federation-api/pull/3) ([@rmanaem](https://github.com/rmanaem))
- [ENH] Very inspired first federation prototype [#1](https://github.com/neurobagel/federation-api/pull/1) ([@surchs](https://github.com/surchs))

#### 🐛 Bug Fixes

- [FIX] Expanded error catching during API request federation [#74](https://github.com/neurobagel/federation-api/pull/74) ([@alyssadai](https://github.com/alyssadai))
- [FIX] Handle empty local nodes file [#67](https://github.com/neurobagel/federation-api/pull/67) ([@alyssadai](https://github.com/alyssadai))

#### ⚠️ Pushed to `main`

- Added pre-commit config file ([@rmanaem](https://github.com/rmanaem))
- Added requirements.txt ([@rmanaem](https://github.com/rmanaem))
- Initial commit ([@rmanaem](https://github.com/rmanaem))

#### Authors: 4

- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Alyssa Dai ([@alyssadai](https://github.com/alyssadai))
- Arman Jahanpour ([@rmanaem](https://github.com/rmanaem))
- Sebastian Urchs ([@surchs](https://github.com/surchs))
