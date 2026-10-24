# Full-stack end-to-end tests

Cypress tests that run the query tool against federation and node APIs with real graph data. They come from the [neurobagel/recipes](https://github.com/neurobagel/recipes) repository (at the same commit as `stack/`, see `stack/SOURCE.md`).

The tests run against the two-node test deployment of `scripts/test-nodes.sh`: a portal (federation API on port 8080, query tool on port 3000) federating over "2 OpenNeuro Datasets" (node API on port 8000) and "BIDS Synthetic" (node API on port 8001), all using the images built from the current checkout. `simple-test.cy.js` targets an older single-node setup and is excluded, as it was upstream.

From the repository root:

```bash
just e2e
```

This builds the images, starts the deployment and runs `npx cypress run --browser chrome` here. Stop the deployment afterwards with `just test-nodes down`.

CI runs the same tests (`.github/workflows/e2e.yml`) on pull requests that change `tools/api/`, `tools/federation-api/`, `tools/query-tool/`, `stack/`, `examples/` or `e2e/`.
