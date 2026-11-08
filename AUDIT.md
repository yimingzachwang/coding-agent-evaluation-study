# Notebook and analysis pipeline audit

**Publication copy:** two transcript quotations are paraphrased below following the decision to omit verbatim excerpts. The original audit is preserved in the ignored local backup. Findings are unchanged.

Audited November 6, 2026: `agent_traces_analysis.ipynb`, `agent_traces_lib.py`, `experiment preparation.ipynb`, the bundled Arrow dataset, and `analysis_outputs/`.

The table-building code reproduces the saved data, but several headline interpretations need correction. The most consequential problems concern task matching, the meaning of the prediction features, and attributing differences between jobs to random outcome noise.

## Verification performed

- Executed all 84 analysis code cells sequentially in the existing Python 3.11.15 `quant` environment, with plotting directed to a noninteractive backend.
- Substituted a direct load of the bundled Arrow snapshot for the Hub loader and redirected all generated outputs to a temporary directory. This verifies downstream execution separately from the loader issue below.
- Rebuilt the five base tables and compared their shared columns against the saved Parquet files; all matched. The final row table also matched in full, allowing dtype differences in the comparisons.
- Reproduced the five existing consistency checks, status counts, published logistic-regression scores, and the cyan paired comparison.
- Tested the normal loader with an empty Hugging Face cache and offline mode, audited tool-call/result identifiers, and reran a targeted feature ablation.

The original notebooks, library, data, and saved analysis outputs were left unchanged.

## Findings, in priority order

### 1. High: the comparisons labelled “matched” do not adequately control task assignment

**Locations:** notebook cells 110–112 (Section 13.2), 139–140 (Section 18.1); executive summary findings 3 and “Strongest evidence.”

The model ranking filters to tasks attempted by multiple models, then independently averages each model's outcomes. The models still have different task sets: respectively 23, 24, 34, 26, 16, 25, and 22 distinct tasks for atlas, cyan, delta, flint, garnet, orion, and vega. No task was attempted by all seven models. Restricting to this union does not make the comparison paired or remove task difficulty as a confound. Repeats also give some model/task cells additional weight.

The success/failure comparison similarly pools all attempts on mixed-outcome tasks before calculating medians. It does not calculate a within-task contrast or balance task weights, so its reported difference cannot be described as an adjusted within-task effect.

There is also a direct ranking error: the raw bottom two are **flint (35%) and atlas (40%)**, not atlas and delta. The claim that atlas/delta are bottom two under both specifications contradicts the displayed table.

**Correction:** report pairwise comparisons on each pair's common tasks, explicitly aggregate repeats, and show task-level uncertainty. Calculate success/failure differences within task before pooling. Correct the ranking narrative and summary.

### 2. High: the “trace-shape equals model identity” headline depends on configuration metadata

**Locations:** notebook cells 114–118 (Section 14); executive summary finding 6.

The feature set labelled “trace-shape features only” includes `dev_role`, a harness configuration flag constant within each job, as well as rate-limit information. It therefore does not isolate trace behaviour from run configuration.

Using the same logistic regression and task-grouped folds:

| Feature set | AUC | Accuracy | Brier score |
|---|---:|---:|---:|
| Published “trace shape” | 0.699179 | 0.635135 | 0.217593 |
| Same features, removing `dev_role` | 0.646880 | 0.624324 | 0.233373 |
| `dev_role` alone | 0.625196 | 0.656757 | 0.222315 |

Removing that single configuration flag materially lowers AUC. Equal AUCs rounded to three decimals also do not establish statistical equivalence; the published model-identity-only model has better accuracy and Brier score than the published shape-only model.

Trace length and final tool fractions are available after the trace completes. These scores can describe retrospective outcome classification, but do not establish prediction before execution or at an early intervention point. Task-grouped CV evaluates new tasks with jobs still represented in training; it does not establish transfer to new jobs or configurations.

**Correction:** separate configuration, identity, and behavioural feature sets. State the prediction time and validation population. Use fixed trace prefixes to test early prediction, and uncertainty estimates for model comparisons. Compare AUC with an AUC baseline and accuracy with an accuracy baseline.

### 3. High: the claimed irreducible run-to-run noise is not identified by these repeats

**Locations:** notebook cells 69–70 and integrated findings; executive summary findings 4–5.

The observed 8/26 disagreement rate is correct. However, **25 of the 26 repeated model/task groups span different jobs**. The only repeated group wholly within one job has two failures. Seven of the eight disagreements are the same cyan run-01/run-07 flips already highlighted as a configuration/date difference.

These observations cannot separate random variation under a fixed configuration from systematic differences between jobs. They do not establish an irreducible noise rate or a ceiling on achievable prediction. Likewise, a whole-dataset regression reusing these observations is not independent corroboration of the cyan comparison, and its coefficient does not identify a role-convention effect.

**Correction:** call this cross-job outcome disagreement. Reserve claims about stochasticity for repeats under controlled, identical conditions; describe the regression as another analysis of the same evidence.

### 4. Medium: the bundled dataset is not actually a loader fallback

**Locations:** `agent_traces_lib.py:107–113`; notebook Sections 2, 3, and “Reproducing this notebook.”

The loader only calls `load_dataset(DATASET_ID, split=split)`. It neither reads the adjacent Arrow file nor specifies that directory as its cache. With an empty cache and offline mode, loading fails with `ConnectionError` despite the bundled Arrow file being present. The downstream replay required loading that file explicitly.

No dataset revision is pinned, so an online refresh is not guaranteed to reproduce this snapshot. Package versions are printed but not captured in an installable lock or requirements file. `NOTEBOOK_DIR = Path.cwd()` also does not implement the advertised independence from kernel launch directory.

**Correction:** support an explicit local snapshot path, record its checksum and dataset revision, pin dependencies, and make the project/output root explicit.

### 5. Medium: identifier integrity issues are absent from the “all checks passed” audit

**Location:** `agent_traces_lib.py:386–456`, `run_consistency_checks`.

The checks reconcile counts, but never validate correspondence between assistant call IDs and tool-result IDs. A count-aware audit within each trace found:

- **13 tool results** without a matching call occurrence;
- **62 tool calls** without a matching result occurrence: 50 bash, 6 edit, 4 read, and 2 write;
- **one reused call ID**, in row 105;
- **67 traces** affected by at least one of these conditions.

An unanswered final call can be expected at a cutoff; these are audit findings, not 67 proven corrupt traces. Orphan results and duplicate IDs need separate inspection. They matter for any reconstruction of action/result sequences and make total-count reconciliation insufficient evidence of complete transcripts.

**Correction:** add ID uniqueness, pairing, and ordering checks; distinguish expected terminal cutoffs from unexplained mismatches and report affected rows.

### 6. Medium: six saved outputs have no generation path in the current notebook

**Locations:** notebook final-output cells 165–167 and reproduction instructions.

A complete replay into an empty directory did not produce these existing files:

```
data_audit/tool_result_schema.csv
data_audit/toolcall_argument_schema.csv
derived_tables/permutation_importance.csv
figures/14_blocked_permutation_importance.png
final_summary/executive_summary.md
final_summary/exploration_log.md
```

The notebook claims every companion artifact regenerates. It does not write either Markdown companion, and contains no permutation-importance calculation. These files therefore have no reproducible generation path in the supplied pipeline; their presence after a normal rerun can conceal stale results.

The data-quality report also says removing the eight traces ending on tool messages was checked in Section 18, but that section contains no such exclusion analysis. Excluding TL from separately normalized status groups is an identity operation: it cannot validate robustness of the other groups' shares.

**Correction:** add the missing generation and sensitivity steps, or explicitly mark these files and claims as outside the reproducible pipeline. Track expected outputs per run.

### 7. Medium: several narrative conclusions contradict the computed evidence

- **Premature termination:** cells 100–104 label eight short WA traces as premature, then claim they end without closing text. Two have closing summaries; row 70, the notebook's own example, claims its tests passed. Row 347 also reports passing tests. Message count alone does not verify that the agent abandoned the task.
- **Repository recovery:** cell 128 describes ARI **0.387** as recovering the repository groups “almost exactly.” The clustering uses 30 clusters for **77 families**; that interpretation is unsupported.
- **Repeated-task prevalence:** **161/253 tasks (63.6%)** have one attempt. The notebook twice states that most tasks have multiple attempts. Repetition still matters, but applies to 92 tasks.
- **Missing content:** the integrated findings say approximately **9%** of assistant messages omit `content`; the actual result is **90.7%**.
- **Near duplicates:** maximum TF-IDF cosine similarity is **0.883091**, while the summary says no pair exceeds 0.88. More substantively, distinct issue numbers and a chosen similarity threshold do not prove tasks are unrelated or exclude all leakage. The defensible claim is that this particular text screen found no stronger duplicate candidate.

**Correction:** derive repeated numerical statements from computed results, soften causal/semantic labels, and review narrative text against saved outputs before delivery.

## Results that held up

The raw snapshot contains 370 traces and 253 tasks, with status counts OK=218, WA=121, IL=26, TL=5. Reward exactly equals `status == 'OK'`. The parsing helpers reproduce the saved tables, and scaling is correctly inside the CV pipeline. Grouping validation by task prevents the same task's repeated attempts from crossing folds.

The cyan comparison reproduces exactly: 17/18 successes versus 10/18, seven discordant pairs in one direction, two-sided sign-test p=0.015625. This is an observed difference between two jobs; its mechanism remains unresolved.

The primary remediation order is: correct the matching and headline interpretations, separate feature groups and prediction timing, make loading and output generation reproducible, then extend transcript integrity checks.
