# Examples
Example inputs and outputs from Neurobagel tools.

## `api-responses/`
Examples of responses returned by Neurobagel APIs.

## `data-upload/`
Examples of valid input files for Neurobagel harmonization tools, including resultant Neurobagel graph-ready dataset files.
- **example_synthetic.tsv**: valid phenotypic tabular data file (has `participant` and `session` IDs corresponding to the [`synthetic` bids-examples dataset](https://github.com/bids-standard/bids-examples/tree/master/synthetic))
- **example_synthetic_participants.json**: valid BIDS data dictionary without Neurobagel annotations, ready to be used in the annotation tool along with example_synthetic.tsv
- **example_synthetic.json**: valid phenotypic data dictionary for example_synthetic.tsv containing Neurobagel annotations
- **example_synthetic.jsonld**: example graph-ready subject data file for a purely phenotypic dataset. 
Contains subject-level annotated phenotypic attributes. Obtained by applying the data dictionary (.json) to the original tabular data (.tsv) using the [`bagel pheno`](https://github.com/neurobagel/bagel-cli) command.
- **nipoppy_proc_status_synthetic.tsv**: valid Nipoppy processing pipeline status file (has participant and session IDs drawn from a subset of [bids-examples `synthetic`](https://github.com/bids-standard/bids-examples/tree/master/synthetic))

### `pheno-bids-output/`

Example graph-ready data files containing harmonized phenotypic and raw imaging (meta)data.

- **example_synthetic_pheno-bids.jsonld**: Sample output of [`bagel bids`](https://github.com/neurobagel/bagel-cli) command on example_synthetic.jsonld and the [`synthetic` bids-examples dataset](https://github.com/bids-standard/bids-examples/tree/master/synthetic). Contains subject-level annotated imaging metadata (inferred from the BIDS directory structure) on top of the subject-level annotated phenotypic attributes.

### `pheno-derivatives-output/`

Example graph-ready data files containing harmonized phenotypic and imaging derivative (meta)data.

- **example_synthetic_pheno-derivatives.jsonld**: Sample output of `bagel derivatives` command on example_synthetic.jsonld and nipoppy_proc_status_synthetic.tsv. Contains subject-level imaging derivative metadata on top of the subject-level annotated phenotypic attributes.

### `pheno-bids-derivatives-output/`

Example graph-ready data files containing harmonized phenotypic, raw imaging, and imaging derivative (meta)data.

- **example_synthetic_pheno-bids-derivatives.jsonld**: Sample output when `bagel pheno`, `bagel bids`, and `bagel derivatives` commands have all been run, using example_synthetic.tsv, [bids-examples `synthetic`](https://github.com/bids-standard/bids-examples/tree/master/synthetic), and nipoppy_proc_status_synthetic.tsv.
Contains subject-level raw imaging and imaging derivative metadata on top of the subject-level annotated phenotypic attributes.

## `query-tool-results/`
Example downloadable query result TSV files from the [Neurobagel query tool](https://query.neurobagel.org).
