# Upstream workflows kept for porting

Verbatim copies of workflows from the tools' upstream `.github/workflows/` folders, taken from each tool's imported head (`migration/imported-heads.txt`) before the folder was deleted. GitHub does not run anything in this folder.

| Workflow | From | Plan |
| --- | --- | --- |
| `handle_external_pr.yml` | every tool (identical in the five tool repositories; documentation's differs) | Ported to one root workflow in migration Step 7d |
| `linkspector.yml` | api (uses `tools/api/.linkspector.yml`) | Ported to a root workflow in Step 7d |
| `cff_validation.yml` | api, bagel-cli | Ported to a root workflow in Step 7d, validating `tools/api/CITATION.cff` and `tools/bagel-cli/CITATION.cff` |
| `updated_examples.yaml`, `generate_examples_diff.yaml`, `comment_examples_diff.yaml` | query-tool | Kept pending a maintainer decision |

Not kept: `stale.yml` (to be set up again manually), `add_iss2project.yml` (no longer needed with one repository), `scorecard.yml` (replaced by one Scorecard for the monorepo).

Step 7d deletes this folder once every workflow is ported or decided on.
