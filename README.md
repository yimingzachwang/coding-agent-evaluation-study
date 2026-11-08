# Evaluating coding agents through execution traces

**Success, failure, and the limits of observational benchmarking**

What can execution traces tell us about coding-agent performance, and how do evaluation design choices affect the conclusions?

This research case study analyzes **370 recorded attempts, 253 tasks, seven anonymized model labels, and 15 jobs** from [mfmVNfpt2q/agent-traces](https://huggingface.co/datasets/mfmVNfpt2q/agent-traces). It combines a structural data audit, linked trace tables, behavioural analysis, retrospective outcome classification, and an assessment of what the evaluation design supports. The contribution is an interpretable account of agent evaluation—including weak findings and unresolved mechanisms—with a reproducible path from raw traces to evidence.

The analysis uses a publicly accessible, ungated Hugging Face dataset. The local Arrow file is a cached snapshot of that source, with byte identity checked by SHA-256. Reproduction instructions identify the upstream revision and checksum; readers acquire the data from Hugging Face rather than from this repository. The findings describe this snapshot, while the parsing and analysis workflow can be adapted to compatible trace datasets.

## Principal findings

- **Evaluation conditions constrain model comparisons.** Raw success rates range from 35.0% to 88.3%, but task assignment is unequal. Filtering to the 79 multi-model tasks still leaves different task sets and repeat weights. These summaries describe observed performance, not a controlled capability ranking.
- **A task-paired job gap is visible; its cause is unresolved.** Cyan succeeds on 17/18 versus 10/18 common tasks across two jobs, with seven one-directional disagreements (exploratory exact sign-test p=0.015625). Role convention, prompt date, and job co-vary. The 8/26 repeated model/task disagreements are largely cross-job variation, not an irreducible randomness estimate.
- **Completed traces contain modest outcome signal.** Existing task-grouped classifiers reach AUC 0.699–0.762. The inputs combine recorded behaviour and configuration; this is retrospective classification, without evidence for an early-warning system, equivalent feature sets, or a predictive ceiling.
- **Useful weak results narrow the interpretation.** First-order tool transitions look similar across outcomes. Success keywords in the last assistant message flag about 49% of OK and 54% of WA attempts with text. Prompt length has little linear association with success (r=0.023). A lexical duplicate screen cannot rule out semantic overlap or leakage.
- **Count consistency does not establish transcript completeness.** Reward equals the OK indicator, while 90.7% of assistant messages omit `content`. An occurrence-aware audit finds 13 orphan results, 62 unanswered calls, and one reused ID, affecting 67 traces. Fifty unanswered calls occur in the terminal message; the stop mechanisms remain unverified.

![Dataset coverage and recorded outcomes](analysis_outputs/figures/07_model_status_counts.png)
*Figure 1. Unequal model sample sizes and recorded outcome counts: OK=218, WA=121, IL=26, TL=5. The grader and IL/TL stop rules are undocumented.*

![Pooled tool shares by outcome](analysis_outputs/figures/10_tool_mix_by_status.png)
*Figure 2. Action-weighted shares of the four declared tools. The five TL traces are bash-heavy and edit-light. Tool names alone do not identify semantic activity; the association does not establish a cause of failure.*

![Pooled success and failure on mixed-outcome tasks](analysis_outputs/figures/13_pooled_success_failure.png)
*Figure 3. Pooled attempts from 33 mixed-outcome multi-model tasks (83 attempts). Successes have a median 104.5 messages versus 177.0 for failures. This filters tasks but does not balance them or estimate a within-task adjusted effect. Outliers are hidden; the length axis is logarithmic.*

## Read the study

The [research notebook](agent_traces_analysis.ipynb) carries the full scientific narrative: motivation, methods, evidence, null results, cases, limitations, and implications for evaluation design. It positions the work relative to [SWE-bench](https://arxiv.org/abs/2310.06770) and [HELM](https://arxiv.org/abs/2211.09110), without claiming that this dataset belongs to either benchmark.

| Entry | Role |
|---|---|
| `agent_traces_analysis.ipynb` | Full study, executed in order from the raw snapshot |
| `agent_traces_lib.py` | Parsing, linked tables, reconciliation, and tool-ID audit |
| `scripts/run_analysis.py` | Fresh-kernel execution, rendering, and artifact manifest |
| `analysis_outputs/` | Regenerated figures, scalar tables, dictionaries, and audit files |
| [Data documentation](docs/DATA.md), `data_snapshot.json` | Provenance, exact snapshot identity, acquisition, and rights limitations |
| `requirements.txt`, `tests/` | Pinned direct dependencies and focused regression checks |
| [Supporting material](supporting/README.md) | Initial exploration and historical artifact dispositions |
| [Review notes](REVIEW_NOTES.md) | Validation evidence, audit dispositions, and publication decisions |

`PROJECT_PLAN.md` and `AUDIT.md` are project records; the local implementation handoff is preserved but ignored. The audit is historical; current dispositions are in the review notes. Authored documentation is maintained separately from generated artifacts.

## Reproduce

Use **Python 3.11**. Direct dependencies are pinned; the reviewed run uses 3.11.15 on macOS arm64. Obtain the explicit Arrow snapshot as described in [docs/DATA.md](docs/DATA.md); the raw data is intentionally not included in proposed public files.

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run_analysis.py \
  --dataset /path/to/agent-traces-train.arrow \
  --output .local_runs/reproduction
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_review.py --output .local_runs/reproduction
```

**The output directory must be new or empty.** The prepared review results already occupy `analysis_outputs`; choose a fresh path such as `.local_runs/reproduction` to reproduce without overwriting them. The script resolves the project root from its own location, so it also works from another directory when invoked by absolute path. Analysis runs offline after installation and acquisition and rejects a different snapshot checksum. No generated tables are used as inputs.

The runner executes all 84 code cells, writes `executed_analysis.ipynb` and `analysis.html` for local viewing, regenerates figures/tables, and writes `manifest.json` with source, dataset, environment, and artifact hashes. Large intermediate Parquet files and the duplicate executed notebook/HTML are local products ignored by Git. Public results are figures, concise CSVs, dictionaries, and the manifest. The manifest also records the ignored local products; regenerate them before running verification. The root notebook retains readable outputs. Raw prompts, messages, tool descriptions, and arguments are omitted from publication displays; representative cases report identifiers, scalar summaries, and paraphrased interpretations.

For an interactive session, set `AGENT_TRACES_PROJECT_ROOT`, `AGENT_TRACES_DATASET`, and `AGENT_TRACES_OUTPUT` to explicit paths before running all cells in a fresh kernel. The runner is the supported route for checking snapshot identity and output isolation.

## Interpretation and licensing

The snapshot is observational, with repeated tasks, shared jobs, unknown model versions, incomplete task overlap, and undocumented grader/stop rules. Grouping CV by task ID prevents exact task repeats crossing folds but does not test new-job transfer or eliminate semantic task overlap. Reported p-values and Wilson intervals are exploratory/descriptive; no bootstrap, new experiments, or additional validation protocols are implied.

Original analysis code is licensed under the [MIT License](LICENSE), adopted following owner approval. The collective copyright notice identifies the project contributors without assuming a personal or company name. This license does not cover the upstream dataset or other third-party material. Raw traces and verbatim trace excerpts are excluded; readers acquire data from Hugging Face under the source's applicable terms.
