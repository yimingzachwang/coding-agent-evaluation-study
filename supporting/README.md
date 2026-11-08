# Supporting and historical material

`experiment_preparation.ipynb` preserves initial exploration as source, with outputs cleared. It is historical supporting material, not part of the supported execution workflow or current research evidence. The main notebook supersedes its paths and interpretations.

`AUDIT.md` and `PROJECT_PLAN.md` at the root are project records. The local `IMPLEMENTATION_HANDOFF.md` is retained but ignored because it records personal workspace paths. The audit remains a historical record; its publication copy paraphrases two transcript quotations and the original is preserved in the ignored backup; `REVIEW_NOTES.md` records dispositions and current validation.

One ignored `.local_backup/` directory preserves the original notebooks, helper module, and outputs. Six historical outputs are deliberately excluded from the public study:

| Historical artifact | Disposition |
|---|---|
| `tool_result_schema.csv`, `toolcall_argument_schema.csv` | Exploratory schema dumps without an existing generation path; use the notebook's actual-key inspection. |
| `permutation_importance.csv`, `14_blocked_permutation_importance.png` | Method absent from supplied code; no reconstruction by guessing. Excluded as evidence. |
| `executive_summary.md`, `exploration_log.md` | Stale, manually maintained companions. Replaced by authored README and notebook narrative; not advertised as generated. |

The audit's targeted feature ablation remains audit-only and is not promoted to a result. The identifier audit is retained with a reproducible occurrence-aware calculation in `agent_traces_lib.py`. Future studies recommended in the audit remain future work; no new models, comparisons, bootstrap analyses, or sensitivity protocols were added for publication preparation.
