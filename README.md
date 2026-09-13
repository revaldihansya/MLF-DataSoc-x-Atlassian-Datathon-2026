# Datathon Python starter

A portable first-stage project for the supplied UNSW DataSoc x Atlassian synthetic dataset. Cleaning, joins, exploration and charts run independently. No machine-learning model is trained here. The purpose is to decide which questions are measurable and which findings deserve deeper validation.

## What is included

| File | Responsibility |
|---|---|
| `.gitignore` | Exclude all local data/results, environments and caches |
| `setup_project.py` | Create local directories and optionally import the separately supplied data ZIP |
| `settings.py` | Usage periods, outcome predictors, category dictionaries and analyst-defined subject grouping |
| `common.py` | Shared integrity checks, missing-outcome handling and confidence intervals |
| `clean_data.py` | Load immutable raw sources; profile types, categories, dates, duplicates and missing values; flag errors |
| `merge_data.py` | Summarise usage; validate joins; create ticket and customer-product analysis tables |
| `explore_data.py` | Descriptive product/subject comparisons, exploratory tests and statistical-extreme review |
| `visualize_data.py` | Create four charts from the computed report tables |
| `run_pipeline.py` | Run in dependency order and record success/failure |
| `tests/test_integrity.py` | Eight targeted tests of missing labels, invalid inputs, keys and usage calculations |
| `data/raw/` | Created locally; place the three original CSVs here (not committed or bundled) |
| `outputs/` | Created by the scripts; generated results, reports and figures (not committed or bundled) |

Python is the analytical source of truth. CSV files are used between scripts because they are simple to inspect, open in Excel and regenerate. There is no authored Excel workbook in this starter. A future `export_excel.py` should be a separate presentation/export layer, copying raw data and selected computed outputs without changing calculations. It should not be part of the analytical dependency chain. A Python notebook can be added for discussion and experimentation, but reusable functions belong in these scripts.

## Run

Open a terminal in the extracted project directory. Use a Python environment that supports the pinned dependencies (the supplied code was run on Python 3.12; see `environment.txt`).

```bash
python -m pip install -r requirements.txt
python setup_project.py --data-zip /path/to/original-data.zip
python run_pipeline.py
python -m unittest discover -s tests -v
```

The raw data is supplied separately, never generated. `setup_project.py` imports exactly `customers.csv`, `customer_support_tickets.csv`, and `product_usage.csv` from the original ZIP. It refuses to replace different existing inputs and is safe to rerun with the same files.

Alternatively, run `python setup_project.py` to create the local folders, then manually copy those three CSVs into `data/raw/`. The directory is intentionally absent from a fresh clone: Git does not track empty directories and the whole directory is ignored. You do not need `.gitkeep` files.

Each pipeline stage creates its own generated subdirectories and CSV/PNG outputs. A stage does not silently run earlier stages: it tells you which prerequisite is missing. `run_pipeline.py` runs every stage in order. Unit tests use small in-memory fixtures and can run without any private data.

Or execute one stage at a time:

```bash
python clean_data.py
python merge_data.py
python explore_data.py
python visualize_data.py
```

The correct execution order is **clean, summarise/merge, explore, visualise**. There is no benefit to performing an unsafe raw join first simply to preserve the original step numbering.

To use another local input directory and separate outputs:

```bash
python run_pipeline.py --raw-dir /path/to/input --output-dir /path/to/results
```

In Windows, use your actual Windows paths; quotation marks are required around paths with spaces. Relative paths also work. Run any later stage with the same `--output-dir`. Stages overwrite generated outputs at that location, never the raw sources. If the pipeline fails, consult `reports/run_status.json`; prior outputs can remain and must not be treated as a new successful run.

## Source integrity

The code-only package contains no raw data or generated results. The original dataset used for verification has 8,320 customers, 8,469 tickets and 42,210 usage rows. Each cleaning run records the actual input SHA-256 hashes and counts in `outputs/reports/input_manifest.json`. This lets collaborators check that their separately obtained inputs match without committing the inputs.

## Git workflow

Commit the Python scripts, `tests/`, `.gitignore`, `README.md`, `requirements.txt` and `environment.txt`. Do not commit data or generated results.

The default generated directory is `outputs/` (plural). Both `/outputs/` and `/output/`, plus `/data/`, are ignored recursively. If you choose another output folder inside the repository using `--output-dir`, add that folder to `.gitignore` too. Keep source ZIPs outside the repository or inside ignored `data/`.

If data/results were **already tracked by Git**, adding `.gitignore` will not untrack them. Run this from the repository root only in that situation:

```bash
git rm -r --cached --ignore-unmatch data outputs output
git add .gitignore
git commit -m "Stop tracking local datasets and generated outputs"
```

`--cached` removes files from Git's index while preserving local copies. This does not remove files from old commits. No Git repository is initialised or remote configured by the Python setup script.

## Cleaning decisions

- Normalise headers, trim text, standardise email case, and map whitespace/case variants of documented categories to their known spelling. No fuzzy spelling guesses are made. Unknown categories are retained and flagged. Inventories expose other category values for manual review.
- Parse dates using explicit source formats. Purchase dates use day-month-year, account creation uses year-month-day, usage uses year-month, and response timestamps use day-month-year plus time.
- Coerce invalid numeric or date values to missing in the cleaned copy and log each affected row. Raw data remains intact.
- Flag exact duplicates, but do not silently delete them. Missing or duplicate dimension keys block the merge so that an ambiguous customer record cannot multiply tickets.
- Keep repeated customer tickets: different ticket IDs are not duplicate records.
- Preserve unknown satisfaction as missing throughout. Do not fill it with zero, an average, or a predicted label.
- Mask the 85 impossible active-day values in the cleaned usage column while retaining other fields and the row. This is not a guessed correction to 28 or 30 days.
- Flag the 1,365 impossible timestamp orderings, retain the timestamps for inspection and do not calculate support durations.
- Do not automatically remove statistical extremes. Report IQR fences within products and counts outside them separately from logical impossibilities.
- Customer age/gender/name conflicts are audited during joins and those fields are excluded from the analysis table. Ticket/customer names and email are also omitted from that table. Raw copies retain all original fields.

Limitations of the cleaner: this is a documented, dataset-specific validator, not a universal data-repair engine. It does not infer missing event chronology, impose undocumented limits on engagement, repair incomplete customer history, infer cancellation completion, or resolve ambiguous entities through approximate name matching. New data requires reviewing schema, category dictionaries and business definitions first.

## Two analysis units

`processed/analysis_tickets.csv`: one row per support ticket. Use it for ticket categories, rating coverage and ticket-associated CSAT. It contains 8,469 rows after joins.

`processed/usage_summary.csv` and `processed/analysis_customer_product.csv`: one row per customer-product pair. Use them for product usage so a customer with several tickets is not counted several times. They contain 8,442 rows.

Monthly usage stays in `clean/usage.csv` for time-series inspection. Do not join all monthly usage rows directly to all ticket rows and then count or average them as independent customers.

Customer email joins tickets to the customer master using a validated many-to-one join. Customer ID plus product joins the usage summary to tickets, again many-to-one. Left joins preserve tickets and unmatched records are reported. Duplicate/missing master keys stop processing.

Every customer-product pair in this supplied usage table has at least one supplied ticket. Therefore `tickets_per_observed_customer_product` is a description of this selected sample, not population support incidence. Its values are approximately 1 across products. It should not drive a product-quality ranking.

## Usage features

The default exploratory baseline is January-February 2023 and the recent window is April-May 2023. Means require both months to be present and valid for that metric. Missing months are not zero usage; incomplete windows produce a missing feature.

Change is recent mean divided by baseline mean minus one. Zero baselines produce missing relative changes and an explicit zero-baseline flag, not infinity or a fabricated percentage. Baseline and recent levels remain available to inspect.

The alternative `sessions_earlier_change` compares March-April against January-February, excluding May. May overlaps the earliest first-response timestamps. There is no ticket creation timestamp, so neither feature is guaranteed to be a pre-ticket predictor. All current windows are descriptive and must be redesigned around a known decision time before predictive deployment.

## What Step 3 actually does

Start with a question and a measurable outcome. Do not automatically train models for every column.

| Question | Method/output |
|---|---|
| What is observed, missing or inconsistent? | Column profile, category inventory, quality summaries and missingness-by-status table |
| Does ticket-associated CSAT differ by product, type, subject, plan, etc.? | Low-CSAT rate, denominator, Wilson interval and exploratory chi-square/Cramer's V |
| Does usage change accompany higher or lower recorded satisfaction? | Spearman rank association with the ordinal 1-5 rating |
| Do issue subjects differ in satisfaction within each product? | Product-subject tables/heatmap and per-product omnibus tests |
| Is refund-request ticket share different across products? | Product ticket-mix summary and exploratory product association test |
| Are usage patterns comparable? | Customer-product changes and product-month usage tables; interpret cross-product session counts cautiously |

The column roles are explicit. IDs identify units; they are not predictors. Names and emails are join/privacy fields. Age/gender are excluded. Text is unsuitable for genuine customer-sentiment analysis in these files. Dates are inspected for chronology rather than automatically correlated as integers. Categories use categorical methods; they are never encoded as arbitrary 1,2,3 product labels for a Pearson correlation.

The source dictionary only calls CSAT a Customer Satisfaction Rating; it does not supply survey wording that separates product quality from support service. Use **ticket-associated satisfaction**. It cannot independently establish either product satisfaction or agent quality.

### Product-experience indicators

| Indicator | Valid interpretation | Invalid interpretation |
|---|---|---|
| Refund-request type share | Proportion of supplied tickets whose type is Refund request | Completed refund rate among all customers |
| Refund subject share | Proportion of supplied tickets with Refund request as subject | Interchangeable with Ticket Type |
| Cancellation-request share | Mix of recorded request types | Actual churn or completed cancellation rate |
| Technical issue/subject share | Mix of supplied reported topics | Verified product defect incidence |
| Within-customer engagement change | Recorded behaviour changed across windows | Product dissatisfaction or churn proved |
| CSAT within a product's tickets | Rating distribution for those recorded support interactions | Direct product-quality survey |
| Ticket counts by time | Not computed without credible event timestamps | Using purchase date as ticket creation date |

`TECHNICAL_SUBJECTS` is an analyst-defined grouping. It is not a verified feature classification. Keep its definition visible, test sensitivity to regrouping, and avoid conflating feature requests, bugs, account problems and billing friction. These files do not identify individual features or provide feature-specific exposure denominators.

### Testing choices and limits

Descriptive tables retain all tickets. Their Wilson intervals are ticket-level approximations and do not account for repeated tickets from a customer. For a selected headline, use a customer-cluster bootstrap or appropriate clustered regression before making an inferential claim.

The starter's basic association tests use one rated ticket per customer, selected by the smallest ticket ID for reproducibility, to avoid treating repeated tickets as independent. Ticket ID is not assumed to be chronological. This changes the analysis population slightly and does not establish independence across people in the same company. There are no company/account IDs to resolve that dependence.

Chi-square tests are not reported automatically when an expected cell count is below five. Review exact or permutation approaches or substantively justified category consolidation in that situation. Cramer's V describes association strength. Spearman rho describes a rank association with the ordinal score. Neither estimates a causal effect.

All finite p-values in this run, including within-product and ticket-mix tests, form one exploratory testing family. The output includes Benjamini-Hochberg and the more conservative Benjamini-Yekutieli adjustments. BY accommodates arbitrary dependence. Adjustment does not validate every analytical assumption, fix confounding or turn exploratory results into confirmation.

An adjusted small p-value is not automatically an important business finding. Read effect size, sample size, interval, consistency and actionability together. The actual starter finds a small rank correlation of about 0.168 between session change and CSAT despite a very small p-value. This is a useful example of statistical detectability versus strong predictive power.

## How to read the outputs

Start with:

1. `reports/input_manifest.json`, `data_quality_summary.csv`, and `join_audit.json`.
2. `reports/product_comparison.csv` and `rating_missingness_by_status.csv`.
3. `reports/product_subject_outcomes.csv` and `usage_decline_outcomes.csv`.
4. `reports/exploratory_association_tests.csv`, reading effects and adjusted p-values together.
5. `figures/` for visuals. Charts display what has been computed; their colours do not establish significance.

There are four figures: product ticket satisfaction, refund-request ticket share, product-subject heatmap, and confirmed data-quality issues. Extreme-value counts are in a separate CSV and are not automatic exclusions.

## Corrected project stages

1. Define the business decision and measurable outcomes; inventory sources.
2. Clean each table and audit keys/types/dates/missingness.
3. Aggregate and join at explicit units; engineer interpretable variables; explore associations and visualise iteratively.
4. Investigate errors and robustness, build final charts and select a defensible problem.
5. Perform deeper confirmation or prediction only if it supports the selected decision.
6. Design an intervention, implementation and evaluation plan, then present the evidence-to-action argument.

Stage 5 is optional model work, not an obligation to train an impressive algorithm. Statistical regression can study adjusted associations; classification can predict a labelled outcome; clustering can describe groups without labels. They answer different questions. A regression coefficient, SHAP value, feature importance or cluster label does not prove what intervention will help.

For an adjusted product-specific question, consider a small set of product-by-subject interactions with appropriate customer clustering and uncertainty. Do not claim different product effects just because one product has p<0.05 and another does not. Do not fit every possible interaction without considering cell sizes and overfitting.

For prediction, predefine the target, scoring time, allowed predictors and capacity metric. Use customer-grouped validation, ideally a later time period when trustworthy timestamps exist. Fit imputation, encoding, scaling and any learned outlier threshold on training data only. Benchmark against a simple rule. The dataset has already been explored, so do not call a later split a pristine untouched validation set. Strong confirmation requires new data.

No model may ingest the CSAT-derived flags, resolution information, source row, identifiers or post-decision information simply because those columns are present. Use an explicit feature whitelist.

Stage 6 is more than a summary: specify who acts, what they do, which customers are eligible, what role AI plays, its baseline comparator, costs, failure handling, success metrics and a controlled evaluation. Do not claim financial savings or churn prevention from data without those outcomes.

## Suggested next decision

Review the quality report, product comparison and subject heatmap together. Identify two or three hypotheses worth investigating, including at least one shared across products. Select a problem based on evidence and an actionable intervention, not a predetermined requirement to deliver one solution per product. The five provided products can still receive different workflows if the data supports those differences.

## Technical references

- pandas merge cardinality validation and null-key behaviour: https://pandas.pydata.org/docs/reference/api/pandas.merge.html
- SciPy chi-square assumptions: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.chi2_contingency.html
- SciPy multiple-testing procedures: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html

These references document the implementation methods. All business-data findings come from the user-supplied synthetic files, not outside Atlassian data.
