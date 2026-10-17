# Upstream workflows kept for porting

Verbatim copies of workflows from the tools' upstream `.github/workflows/` folders, taken from each tool's imported head (`migration/imported-heads.txt`) before the folder was deleted. GitHub does not run anything in this folder.

| Workflow | From | Plan |
| --- | --- | --- |
| `linkspector.yml` | api (uses `tools/api/.linkspector.yml`) | Ported to a root workflow in migration Step 7d |
| `cff_validation.yml` | api, bagel-cli | Source for validating the single root `CITATION.cff`, which replaces the per-tool files after cutover (Step 19) |

Not kept: `handle_external_pr.yml` (no longer needed), `add_iss2project.yml` (not needed with one repository), `stale.yml` (to be set up again manually), `scorecard.yml` (replaced by one Scorecard for the monorepo at cutover), and query-tool's example-diff workflows (replaced by a check that the committed query-tool example results are current, after cutover, Step 18).

This folder is deleted once its last file is ported.
