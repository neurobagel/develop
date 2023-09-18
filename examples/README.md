# Examples
Example files using the neurobagel schema


### `data-upload/`
Examples of valid input files for Neurobagel harmonization tools, including resultant Neurobagel graph-ready dataset files.
- **example_synthetic.tsv**: valid phenotypic tabular data file (has `participant` and `session` IDs corresponding to the [`synthetic` bids-examples dataset](https://github.com/bids-standard/bids-examples/tree/master/synthetic))
- **example_synthetic.json**: valid phenotypic data dictionary for example_synthetic.tsv containing Neurobagel annotations
- **example_synthetic.jsonld**: example graph-ready subject data file for a purely phenotypic dataset. Contains subject-level annotated phenotypic attributes. Obtained by essentially applying the data dictionary (.json) to the original tabular data (.tsv) using the [Neurobagel CLI](https://github.com/neurobagel/bagel-cli) `pheno` command..

#### `pheno-bids-output/`

Example graph-ready data files containing both harmonized phenotypic and imaging (meta)data.

- **example_synthetic_pheno-bids.jsonld**: Sample output of Neurobagel CLI `bids` command on the example_synthetic.jsonld and the [BIDS `synthetic` example dataset directory](https://github.com/bids-standard/bids-examples/tree/master/synthetic). Contains subject-level annotated imaging metadata (extracted directly from the BIDS dataset structure) on top of the subject-level annotated phenotypic attributes.

### `query-tool-results/`
Example downloadable query result TSV files from the [Neurobagel query tool](https://query.neurobagel.org).