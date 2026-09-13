# Datathon analysis: AI-assisted customer experience recovery

Prepared from the supplied 2026 UNSW DataSoc X Atlassian Datathon brief, README and three CSV files. All empirical results below are calculated from those files. Proposed features, targets and financial scenarios are explicitly identified. No external market claims or assumed Atlassian product capabilities are used.

## 1\. Recommended story

**Use behavioural signals to identify customers who may need help before a satisfaction score is available, then use an AI assistant to turn those signals into a clear, human-reviewed support action.**

Suggested title: **Customer Experience Radar: turn declining engagement into timely support.**

The business question is: *Which customers should support teams review, what evidence explains the concern, and what action should the team take?*

The supplied data supports a modest relationship between declining product usage and low satisfaction. It does not support a confident churn prediction, automated diagnosis or quantified revenue-saving claim. A submission is stronger when it demonstrates these distinctions and explains what the proposed pilot will establish.

No analysis can guarantee finalist selection. The strategy here directly addresses the organisers' scoring priorities: a specific problem, reproducible evidence, a feasible solution and a concise business story.

## 2\. What the slides require

Source: brief, pages 2-8.

|Requirement|Implication for the submission|
|-|-|
|Understand customer experience and protect business value|Link the analytical finding to a support decision and measurable customer outcome.|
|Define a story, present insights, recommend or build a solution|Show a complete evidence-to-action chain.|
|Business leaders are the audience|Explain who acts, why, and what changes. Put model specifications in the appendix.|
|Story and problem: 15%|State the missing-feedback problem and target user clearly.|
|Analysis: 30%|Use all three tables, audit the data, compare baselines and report uncertainty.|
|Solution and recommendation: 35%|Give the workflow, owners, implementation steps, evaluation plan and decision gates.|
|Presentation and Q\&A: 20%|Rehearse an eight-minute story and prepare for limitations and causality questions.|
|Submission: PowerPoint or PDF by 3pm Monday 14 September|Submit a self-contained deck. The extracted slide does not specify the timezone.|
|Heats and final: 8 minutes plus 4 minutes Q\&A|Allocate approximately half the pitch to action, implementation and impact.|

## 3\. Data audit and analytical boundaries

|Item|Actual finding|Consequence|
|-|-|-|
|Customers|8,320 unique customer IDs and unique emails|This is the analytical population supplied, not the 300,000+ users mentioned in the slides.|
|Support tickets|8,469 distinct ticket IDs|A customer can have multiple tickets.|
|Usage|42,210 rows; 8,442 distinct customer-product pairs; five months per pair|Join on customer ID and product after resolving the customer email.|
|Products|Jira, Confluence, Trello, Bitbucket and Loom|Include all five provided products. The slide names four.|
|Purchase dates|1 January 2020 to 30 December 2021|Purchase date is not ticket creation date.|
|Usage period|January-May 2023|Do not describe this as a 24-month usage panel.|
|First responses|31 May-2 June 2023|Complete May aggregates can overlap the earliest support activity.|
|Resolution timestamps|31 May-2 June 2023|Timing requires validation.|
|Invalid ordering|1,365 of 2,769 paired resolution timestamps precede first response: 49.3%|Do not report average resolution duration or claim slow response caused dissatisfaction.|
|Ticket creation timestamp|Not supplied|Response latency, queue age and exact prediction-time availability cannot be established.|
|CSAT|2,769 observed scores, all on closed tickets|Low CSAT is observable only for this selected subset.|
|Unrated tickets|5,700, comprising 2,819 Open and 2,881 Pending Customer Response|Missing ratings are unknown outcomes, not neutral or negative sentiment.|
|Text|Sixteen categorical subjects; no customer-authored description; sampled resolution strings are incoherent|No defensible customer-language sentiment benchmark can be built from these files.|
|Conflicting identity attributes|149 name, 143 age and 99 gender disagreements between joined ticket and master records|Use exact unique email for the provided join; omit those demographic fields from models.|
|Active days|85 usage rows exceed days in their calendar month|Flag and exclude or repair after confirmation. A model sensitivity excludes active-day features.|
|Commercial outcome|No revenue, prices, churn, renewals, seats or account mapping|Do not infer actual dollars saved or count customer IDs as companies.|

The README explicitly calls this a synthetic dataset. Findings demonstrate an analytical method within the supplied exercise, not verified conditions among real Atlassian customers.

### Correct joins

1. Normalise CSV column names to lowercase with underscores.
2. Join tickets to customers using Customer Email, validated many-to-one. All 8,469 tickets match.
3. Aggregate monthly usage at customer-product level.
4. Join those features on Customer ID and Product Purchased = Product. All tickets have matching usage histories.
5. Validate the final row count remains 8,469. Do not join all products for a customer to each ticket or expand tickets across raw monthly rows.

The master customer ID groups repeated tickets for model validation. Do not use customer email, name or IDs as predictors.

## 4\. Main findings

### Finding A: most tickets have no observed satisfaction outcome

* 2,769 / 8,469 = **32.7%** have a rating.
* 5,700 / 8,469 = **67.3%** have no rating.
* Among rated tickets, 1,102 / 2,769 = **39.8%** have a rating of 1 or 2 out of 5.

Interpretation: a workflow that uses only completed CSAT misses the current experience of open and pending cases. The data does not establish that existing Atlassian support operates this way; this is the opportunity demonstrated by the supplied files.

Customer benefit: support can ask a relevant question while the case is still active. Business benefit: a focused review queue may use support capacity more effectively. Both benefits require prospective testing.

### Finding B: usage decline is associated with low satisfaction

Define baseline sessions as the mean of January and February. Define recent sessions as the mean of April and May. For the product associated with the ticket:

`session\_change = recent\_sessions / baseline\_sessions - 1`

All observed session baselines are positive. A decline flag means `session\_change <= -0.20`. This is an interpretable exploratory threshold, not an optimised or validated operating threshold.

|Rated ticket group|Tickets|CSAT 1-2|Low-CSAT rate|95% Wilson interval|
|-|-:|-:|-:|-:|
|Sessions down at least 20%|437|219|**50.1%**|45.4%-54.8%|
|All other session changes|2,332|883|**37.9%**|35.9%-39.9%|

Difference: **12.2 percentage points**. Relative rate: **1.32 times**, or approximately 32% higher. These are different ways to describe the same association, not a 32-percentage-point difference.

A bootstrap resampling customer IDs, with 2,000 repetitions, gives a 95% interval of approximately **7.3-17.2 percentage points** for the difference. An exploratory chi-square test gives p < 0.001. This pattern also survives a simple Bonferroni adjustment across the eleven categorical comparisons examined, but all analyses remain exploratory and synthetic.

The decline flag catches only 219 / 1,102 = **19.9%** of observed low-CSAT tickets. It is a focused signal, not a comprehensive detector. About half of flagged rated tickets score 3-5, so do not automate punitive or high-cost actions based on this flag.

Sensitivity checks:

* At a 30% threshold, 117 / 211 = **55.5%** have low CSAT, compared with 985 / 2,558 = **38.5%** among the rest. The smaller queue has higher observed concentration, but excludes more cases.
* Keeping just one rated ticket per customer gives **50.0% versus 37.8%**. Retention uses smallest ticket ID, not an assumed chronology.
* Comparing March-April against January-February, excluding May, gives **46.3% versus 38.7%**. The effect is weaker but directionally consistent. Missing ticket creation dates still prevent a genuine pre-ticket claim.
* The 20% decline association has the same direction in all five products, with smaller segment samples. This is not evidence that product differences themselves are statistically established.

|Product|Declining group n|Low CSAT, declining|Other group n|Low CSAT, other|
|-|-:|-:|-:|-:|
|Bitbucket|83|55.4%|444|38.3%|
|Confluence|81|48.1%|482|37.3%|
|Jira|76|59.2%|507|37.1%|
|Loom|122|41.8%|420|38.6%|
|Trello|75|50.7%|479|38.2%|

Do not claim that falling usage causes low satisfaction, that support caused the decline, or that either measure proves churn. Common underlying problems or the synthetic generator could create the association.

### Finding C: ordinary ticket categories offer little separation

Observed low-CSAT rates by product range from **38.9% to 41.0%**. Across the full rated subset, tests for product, ticket type, subject, priority, channel, plan, industry, region and company size do not establish associations at the conventional 5% level in these comparisons.

This does not prove those attributes never matter. It means the supplied sample gives little support for a story such as “one product or channel is driving dissatisfaction.” Avoid choosing the largest bar from near-equal categories and presenting it as a root cause.

### Finding D: there is a concrete, manageable candidate queue

Applying the 20% usage rule to unrated tickets identifies:

* **855 tickets**, or **15.0%** of the 5,700 unrated tickets.
* **853 distinct customer IDs**.
* **430 Open** and **425 Pending Customer Response** tickets.
* **415 Medium or Low priority** tickets, showing that this signal can add a different review dimension without overriding critical incident priorities.
* 322 Standard, 207 Premium, 87 Enterprise and 239 Free tickets.

These are **review candidates with unknown satisfaction**, not 855 dissatisfied customers or 853 customers about to churn. The distinction between tickets, customer IDs and companies must remain visible.

A tighter 30% threshold yields **413 unrated tickets**. Choose capacity and intervention costs first; test thresholds prospectively rather than selecting whichever produces the most dramatic percentage.

## 5\. What the AI experiments actually show

Target: CSAT <= 2 among rated, closed tickets. This is a low-satisfaction proxy, not a sentiment annotation or churn label.

Inputs:

* Ticket/context model: product, type, subject, priority, channel, industry, region, company size and plan.
* Usage model: baseline, recent and percentage-change features for sessions, active days, product actions, collaborators and integrations.
* Combined models: both sets, using logistic regression and a random forest.

Excluded: satisfaction as an input, resolution text, invalid support durations, names, emails, IDs and conflicting age/gender fields. No post-resolution field is used to predict satisfaction.

Evaluation: an initial 75/25 split grouped by customer ID, random seed 42. There are 2,077 training tickets and 692 test tickets, with zero overlapping customers. The test set has 274 low-CSAT outcomes, a 39.6% prevalence. Preprocessing is fitted on training rows only. This is an exploratory retrospective holdout, not an untouched external validation set.

|Method|Initial holdout ROC AUC|Low-CSAT tickets among top 139 reviewed|Precision at approximately 20% capacity|
|-|-:|-:|-:|
|Rank by session decline|**0.602**|**73**|**52.5%**|
|Usage logistic regression|0.598|71|51.1%|
|Combined random forest|0.576|67|48.2%|
|Low recent sessions alone|0.542|64|46.0%|
|Ticket/context logistic regression|0.515|63|45.3%|
|Combined logistic regression|0.579|61|43.9%|
|Priority ranking|0.519|59|42.4%|

The top-139 result describes retrospective identification, not recovered customers. Priority ties are resolved by stable source order; it is an illustrative baseline, not a simulation of an actual operational queue. Critical incidents must retain their safety and service priority regardless of this experiment.

AUC measures ranking discrimination: approximately 0.5 is chance and 1.0 is perfect. These values around 0.6 are modest. Accuracy is less useful for the proposed limited-capacity queue.

A second five-fold validation groups by customer ID, with stratification and random seed 123:

|Method|Mean ROC AUC|Mean precision in top 20%|
|-|-:|-:|
|Session-decline ranking|**0.596**|**49.7%**|
|Usage logistic regression|0.589|49.5%|
|Usage logistic regression without active-day fields|0.593|49.9%|
|Combined logistic regression|0.571|46.8%|
|Ticket/context logistic regression|0.510|41.6%|

The rule and usage models are practically similar here; no statistically established superiority of one over the other is claimed. Removing the active-day fields leaves the conclusion intact. The random forest did not add compelling value in the initial comparison, so further tuning was not pursued.

**Decision: deploy neither a confident churn model nor autonomous risk decisions. Start with a transparent rule as the analytical baseline; evaluate AI assistance around the review workflow.** A future model must beat that baseline on a new, chronologically separated dataset and on business outcomes before replacing it.

Important remaining limits: selection bias from closed-only labels; synthetic generation; no ticket creation time; limited five-month history; exploratory feature/threshold choices; and no prospective evaluation. Transferring a pattern from rated closed tickets to open tickets is a hypothesis to test, not established calibration.

## 6\. Proposed solution: Customer Experience Radar

Target user: the support agent reviewing a ticket, supported by a team lead or customer-success specialist. This is a proposed workflow; no production integration or evaluated language-model assistant has been built in this analysis.

### A. Evidence layer

Compute verified aggregates and attach source ticket ID, product, periods, counts, change, status and data-quality notes. Show missing CSAT explicitly as “unknown”. A rules engine identifies review candidates and respects existing priority handling.

Deduplicate interventions by customer-product, with account-level grouping when a trustworthy account mapping becomes available. The current data does not supply organisation IDs.

### B. AI assistance layer

An assistant receives only the evidence it needs and produces:

1. A short explanation of the observed signal.
2. A question that helps the agent check whether the decline reflects a customer problem.
3. A suggested routing or follow-up action, requiring human approval.
4. An explicit statement of what is unknown.

Numbers must come from deterministic calculations, not language-model arithmetic. Every factual sentence should trace to a supplied field or approved knowledge source. Do not label a customer frustrated or likely to churn without evidence.

For a future system with genuine customer messages, AI could extract issue themes, detect expressed sentiment and group recurring problems. That extension needs authentic text, human-labelled evaluation samples and permissioned knowledge. The current random-looking resolution strings are unsuitable training or retrieval material.

### C. Action layer

|Evidence|Proposed agent action|What to measure|
|-|-|-|
|Open ticket and usage decline|Review the case and ask whether a specific task remains blocked|Agent usefulness rating; task progress; customer effort|
|Pending response and usage decline|Review the previous request; make the next question clear and easy to answer|Response completion and repeated-contact rate|
|Several substantiated cases sharing an issue|Route a reviewed issue summary to the relevant product team|Confirmed recurring issues and subsequent remediation|
|Missing, contradictory or insufficient evidence|Abstain from diagnosis and ask the agent to inspect the source|Unsupported-claim and correction rates|

Routing by issue can use existing subject categories as context, but those categories have not been shown to explain dissatisfaction in this dataset.

### Concrete demonstration using a real supplied record

**Ticket 3884, Confluence, Standard plan, Open, Medium priority.**

Verified evidence: average sessions fell from **20 in January-February to 8 in April-May**, a **60% decrease**. Satisfaction is **unknown**.

Proposed agent-facing output:

> Confluence sessions decreased 60%, from an average of 20 to 8 per month across the compared periods. This ticket is open and has no satisfaction score. Review the ticket and ask whether the customer is currently blocked from completing a task. The data does not establish the reason for the decline or whether the customer intends to leave.

This is a manually specified example of the intended output, not a measured result from a language model. Keep that label on the demo. Do not invent an integration failure, technical diagnosis or customer quote.

A compact prototype should show only a queue, one evidence card and an editable action suggestion. A large generic dashboard would dilute the main decision.

## 7\. Measuring value without fabricating ROI

### What is measured now

* A 12.2-percentage-point difference in observed low-CSAT rates between usage groups.
* 855 unrated review candidates under one exploratory rule.
* Modest retrospective discrimination, with simple rules performing similarly to AI models.

### What the pilot must measure

* Primary customer outcome: a directly collected measure of whether the customer's task is unblocked at a predeclared follow-up time.
* AI workflow outcome: agent time per eligible case, including verification and corrections.
* Supporting outcomes: follow-up CSAT, response rate, repeat contacts, and subsequent usage relative to baseline.
* Longer-term business outcomes, once joined correctly: renewals, retention and contribution margin.

Do not use increased usage alone as proof of a better experience. Some customers may accomplish tasks with fewer sessions. Measure the customer's actual outcome alongside activity.

### Separate targeting value from AI-assistance value

First test the assistant on the same rule-eligible population: randomly assign eligible customer-product units to rule plus standard agent workflow versus rule plus AI assistance. This isolates whether the assistant improves the agent/customer outcome.

Then, if sample size allows, compare a capacity-matched standard queue against the new targeting policy. A three-arm design could test standard queue, rule-only workflow and rule-plus-AI workflow, but requires more observations. Randomise at a level that avoids different tickets from the same customer entering different arms. Use account-level randomisation once account IDs exist.

Set the outcome, follow-up window, exclusion rules, service guardrails and analysis before starting. Record non-response and report response rates by arm. Determine required sample size from baseline outcome rates and the smallest useful effect; do not promise the 853 candidate IDs are enough. A two-week pilot can assess workflow feasibility; it may be too short or small to establish retention impact.

### Illustrative planning arithmetic, not observed benefits

If each of the 855 candidate tickets were reviewed once and AI saved **3 net minutes per review**, including verification, that is:

`855 × 3 / 60 = 42.75 staff-hours`

Those three minutes are an assumption to test. The count is a snapshot, not a monthly arrival rate, and customer-level deduplication could reduce reviews. Do not annualise it.

For customer recovery, assume all 853 unique candidate IDs are eligible and define a measurable success outcome. Hypothetical absolute improvements of 2, 5 and 10 percentage points correspond to approximately **17, 43 and 85 additional successful outcomes**. These are scenarios, not expected results and not customers retained.

A future monetary case should use:

`Net value = incremental retained accounts × contribution margin per retained account + verified staff-hours saved × fully loaded hourly cost - implementation and operating costs`

The provided files cannot populate this equation. Plan type is useful context, not a revenue amount or seat count. Avoid prioritising paying customers at the expense of essential support access; severity and customer need remain separate considerations.

## 8\. Implementation plan and ownership

|Stage|Proposed work|Owner|Completion condition|
|-|-|-|-|
|Datathon prototype|Reproduce joins, show evidence, compare baselines, present one transparent output example|Team analyst and presenter|Every headline traces to an attached source or reproducible calculation|
|Data-readiness phase|Add creation time, reliable usage timestamps, genuine text, account IDs and consistent outcomes|Data engineer and support operations|Valid point-in-time dataset and auditable identity joins|
|Shadow evaluation|Run the rule and assistant without changing customer treatment|ML engineer and support lead|Agent review finds factual output sufficiently reliable to justify a pilot|
|Controlled pilot|Test rule plus AI against rule plus standard workflow|Support lead and analyst|Predeclared customer and workflow metrics available with uncertainty|
|Expansion decision|Broaden only where results justify cost and service impact|Business sponsor|Measured incremental value; acceptable correction and failure rates|

Suggested evaluation gates are design decisions, not current results. Require zero fabricated numerical facts in the demonstration, source support for all displayed factual claims, and abstention where evidence is missing. Real deployment thresholds must be agreed by the owning team and tested on representative cases.

Essential safeguards are specific to the proposal: minimise personal data sent to a model; retrieve only permitted knowledge; separate customer text from system instructions; keep agents in control of messages and routing; log evidence and edits; and monitor unequal false-positive rates and service access across relevant product/plan/region groups. Do not use age or gender to allocate support.

## 9\. Eight-minute deck blueprint

Use nine main slides with a total speaking time of 480 seconds. Keep technical and audit detail in an appendix. Each chart should carry a denominator, period, synthetic-data note and source reference in a readable footer.

|Slide|Time|Headline|Content and visual|
|-|-:|-|-|
|1|35s|Help customers while their experience is still unknown|Problem, chosen AI question and one-sentence proposal.|
|2|45s|67% of supplied tickets have no satisfaction score|Rated versus unrated chart; explain that missing means unknown.|
|3|65s|A 20% usage decline marks a 12-point satisfaction gap|50.1% versus 37.9% with intervals and sample sizes. Define periods.|
|4|55s|More complex models did not improve the baseline|Compact five-fold comparison: context 0.510, usage 0.589, rule 0.596 AUC. Explain modest signal.|
|5|45s|The signal identifies 855 cases for review|Queue size; 853 customer IDs; Open/Pending breakdown; unknown outcomes.|
|6|85s|AI turns verified evidence into a useful next step|Ticket 3884 evidence card; proposed assistant output; agent approval.|
|7|65s|Test whether AI adds value to the same review queue|Rule-only versus rule-plus-AI experiment; customer and agent outcomes.|
|8|55s|Start small and measure value before scaling|Owners, data readiness, shadow mode and pilot. Label any scenario assumptions.|
|9|30s|Approve a measured customer-recovery pilot|Restate evidence, concrete action and the decision requested.|

Suggested opening:

“Support ratings describe only a third of the tickets in this dataset. We asked whether product behaviour could help teams identify customers who may need help while their experience is still unknown. We found a useful but modest signal, tested it against AI models, and designed an assistant that makes the evidence actionable.”

Suggested close:

“Customers whose sessions fell at least 20% had a 50% low-satisfaction rate, compared with 38% for the rest. That signal identifies 855 unrated cases for review. We recommend a transparent queue and a human-reviewed AI assistant, with a controlled pilot to establish whether customers get unblocked sooner.”

Appendix slides: dataset reconciliation; exact joins; outcome selection bias; timing defects; threshold and earlier-period sensitivity; full model results; group-split method; evaluation plan; assumptions and business-case equation.

## 10\. Questions judges are likely to ask

**Why AI if a rule performs as well?**
The experiments show that AI risk scoring is not yet justified. The proposed AI role is translating verified evidence into concise explanations and agent actions. Its incremental value is explicitly tested against the same rule without AI. Future models have a clear baseline to beat.

**Is this really sentiment analysis?**
No. CSAT 1-2 is an observed low-satisfaction proxy. The supplied files lack authentic customer messages. True language sentiment extraction is a future extension with a different evaluation dataset.

**Have you proved customers will churn?**
No. There is no churn label or renewal data. We propose a review queue and measure actual customer outcomes before making retention claims.

**Could low usage be normal?**
Yes. Seasonality, completed work, different roles or changing needs can all matter. The assistant asks a clarifying question rather than diagnosing the decline. More history and task-level outcomes are required.

**Are the open tickets actually dissatisfied?**
We do not know. The observed association comes from closed rated tickets. The pilot must collect outcomes on open and pending cases to test whether it transfers.

**Why not automate messages to all 855?**
The flag has many non-low-CSAT cases even in the rated subset. Human review and a low-burden intervention are appropriate while benefits and harms are unknown. Duplicate tickets should not trigger duplicate contact.

**Why exclude response time?**
Creation times are absent and 49.3% of paired resolution timestamps precede first response. Calculating a reliable response or resolution SLA from those fields would be misleading.

**How did you prevent leakage?**
Customers are separated between training and test, preprocessing is train-only, and resolution/CSAT inputs are excluded. However, missing creation times and the May overlap prevent a fully verified point-in-time prediction claim. An earlier March-April sensitivity shows the association persists more weakly.

**How much money does this save?**
The dataset cannot establish it. We show planning scenarios and identify the additional commercial fields needed. Savings and recovery effects must come from the controlled pilot.

**How do you know the language model is accurate?**
No language model has been evaluated in this analysis. The prototype specifies evidence-grounded outputs. Before deployment, evaluate factual consistency, supported recommendations, abstention and agent correction time on representative cases.

**What would you do next with more data?**
First obtain trusted ticket timestamps, genuine text, account mapping and post-intervention outcomes. Establish the operational baseline, then test the assistant and only increase model complexity when measured value improves.

## 11\. Submission quality checks

* Use the actual supplied sample size and five-month usage window.
* State that the data is synthetic.
* Keep percentages attached to the correct denominator.
* Use “12.2 percentage points” or “1.32 times,” not “32 percentage points.”
* Distinguish tickets, customer IDs and business accounts.
* Label 855 as review candidates, not predicted churners.
* Do not imply the model comparisons establish production performance.
* Label the AI evidence-card text as a proposed output example.
* Give the rule-only comparison equal visibility to the AI proposal.
* Put feasibility, ownership and the evaluation decision on the main slides.
* Use readable charts with zero baselines for bar charts.
* Rehearse to eight minutes and retain the audit details for Q\&A.

## 12\. Reproducibility and sources

The package includes `analyse.py`, `validate.py`, `charts.py`, numerical JSON results, segment CSV tables, a ticket-level evidence CSV, and three PNG charts. No customer names or email addresses are included in the exported evidence table. The user-supplied raw data is not duplicated in this package.

Requirements: Python with pandas, NumPy, SciPy, scikit-learn and Matplotlib. The analysis was executed using the available Python environment. Exact package versions appear in `environment.txt`.

After extracting the original input ZIP and this package, run from the package folder:

```bash
python analyse.py /absolute/path/to/extracted/input ./results
python validate.py /absolute/path/to/extracted/input ./results
python charts.py ./results
```

`analyse.py` creates the main tables and model comparisons. `validate.py` uses the same preparation to run five-fold and descriptive sensitivity checks. `charts.py` reads the generated JSON/CSV results. Default paths reflect the original working environment; explicit paths above make the package portable.

Primary sources: `2026 UNSW DataSoc X Atlassian Datathon.pdf`, particularly pages 4-8; `README.md`; `customers.csv`; `customer\_support\_tickets.csv`; `product\_usage.csv`, all supplied by the user. All empirical claims in this report are derived from those inputs. The solution design and scenario assumptions are original proposals, not additional facts supplied by the organisers.

