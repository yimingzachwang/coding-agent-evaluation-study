# Local review notes — November 8, 2026

**Refactoring and local validation are complete. The owner authorized local Git initialization, commitment of the 48-file allowlist, and public GitHub publication on November 8, 2026.** MIT for original code and removal of verbatim excerpts are implemented. No Git repository existed at intake. The study is now [published publicly on GitHub](https://github.com/yimingzachwang/coding-agent-trace-evaluation) on `main`; initial push and remote-content verification passed.

## Start here

Read [README.md](README.md), then [the executed research notebook](agent_traces_analysis.ipynb), especially Sections 6, 8, 13–15, and 18–22. The locally generated `analysis_outputs/analysis.html` is convenient for review but excluded from proposed public files. [Data provenance](docs/DATA.md) records external acquisition and data exclusions; [LICENSE](LICENSE) contains the approved MIT license for original code.

## Main changes

Retained all 84 analysis code cells and existing model specifications, with a coherent scientific narrative and substantive weak/null paths. Corrected claims throughout the notebook, figures, dictionaries, and README. Added explicit offline Arrow loading, checksum enforcement, revision-pinned acquisition, reliable paths, fresh-kernel execution, output manifests, concise result CSVs and `findings.json`, and four focused helper tests. Added occurrence-aware ID checks without inventing anomaly causes. Renamed a task-table field that contained a standard deviation but was labelled variance; values are unchanged. Metadata joins now validate their cardinality.

The preparation notebook survives as output-cleared historical source under `supporting/`. Original source and outputs survive in one ignored `.local_backup/` directory. Missing-method artifacts and stale companions are excluded, as explained in `supporting/README.md`. Raw data remains locally available and ignored. The local handoff is ignored because it contains personal workspace paths. `PUBLIC_FILES.txt` lists the proposed public contents.

## Validation commands and outcomes

Commands below preserve the validation arguments, replacing personal absolute paths with `REPO` and the available Python 3.11.15 interpreter with `PYTHON311`. The latter was the existing `quant` interpreter.

```sh
"$PYTHON311" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
```

An isolated virtual environment (without system site packages), Python **3.11.15**, macOS arm64: installation succeeded, pip reported no broken requirements, and **4/4 tests passed**. Pinned acquisition was also checked:

```sh
python scripts/fetch_snapshot.py --output .local_runs/acquired/agent-traces-train.arrow
```

This command ran with the available `quant` Python and returned the recorded SHA-256 exactly. It used the existing Hugging Face cache; a clean-cache network re-download was not tested. Hub metadata was checked online independently. The final analysis used this acquired, checksum-matching Arrow file:

```sh
REPO="$PWD"
cd /private/tmp
"$REPO/.venv/bin/python" "$REPO/scripts/run_analysis.py" \
  --dataset "$REPO/.local_runs/acquired/agent-traces-train.arrow" \
  --output "$REPO/analysis_outputs"
cd "$REPO"
.venv/bin/python scripts/check_review.py \
  --output analysis_outputs --baseline .local_backup/analysis_outputs
```

**Passed:** 84 sequential cells in a fresh kernel; 41 generated artifacts plus the manifest; 15 embedded and saved figures; five count/metadata reconciliation checks; recorded headline values; source/artifact checksums; no notebook errors or stderr. Retained shared values across **10 original Parquet tables** match, excluding corrected taxonomy labels, removed raw-text fields, and the renamed standard-deviation field. No saved table was an analysis input. `check_review.py` verifies evidence and output hygiene; it is a software/reproduction check, not a new research validation protocol.

All figures were inspected in a contact sheet, with key plots, the revised process diagram, and coverage graph inspected at full size. Headless Chrome rendered the notebook opening and classification excerpt for visual QA. All 48 proposed public files (2.37 MiB total) passed checks for local links, size, execution state, raw-file exclusions, credential-pattern candidates, and personal machine paths. The historical audit publication copy paraphrases its two transcript quotations; its original is preserved in the ignored backup. Sandbox restrictions required approved access for Jupyter loopback ports and package/source downloads; comparison commands emitted harmless Arrow CPU-probe warnings outside notebook outputs. Chrome emitted host display diagnostics but produced usable screenshots.

## Audit dispositions

| Finding | Disposition |
|---|---|
| Shared-task comparisons and rankings | **Corrected/qualified:** unequal task coverage and repeat weights explicit; raw bottom two flint/atlas; subset bottom two atlas/delta; pooled medians described without adjustment claims. Pairwise estimation deferred. |
| Feature sets and classification claims | **Corrected:** behaviour/configuration labels, retrospective timing, metric-specific baselines, task-grouped population. Equivalence, causal separation, and predictive-ceiling claims removed. Audit ablation remains audit-only. |
| Repeated-pair disagreement | **Qualified and reproduced:** 8/26, with 25 groups spanning jobs; seven cyan flips. No irreducible randomness or independent-regression-corroboration claim. Controlled repeats deferred. |
| Transcript integrity | **Reproduced:** 13 orphan results, 62 unanswered calls (50 terminal/12 nonterminal), one reused ID, 67 affected traces. Occurrence pairing/ordering scope explicit; causes unresolved. |
| Loading, paths, and dependencies | **Corrected:** explicit Arrow path, SHA-256, independently verified revision, pinned dependencies, clean-environment execution from another directory. |
| Missing-generation artifacts and sensitivity | **Excluded/qualified:** historical schema dumps, permutation importance, and Markdown companions excluded. No terminal-tool exclusion claimed; TL removal is a normalization identity. |
| Contradictory descriptions | **Corrected:** short WA includes closing summaries; ARI 0.387 for 30 clusters/77 families; 161/253 tasks occur once; content missing 90.7%; lexical maximum 0.883091 without leakage-exclusion claims. Also corrected stale 429 counts to 29 traces (48.3% vs. 59.8% success). |

## Public-source clarification

A follow-up anonymous access check confirmed `private: false`, `gated: false`, and HTTP 200 for the source file. The local analysis file is a checksum-matching cached copy of the public Hugging Face dataset, not a separate private dataset. README and data documentation now make external acquisition explicit. Public access supports reproducibility; it does not establish that the findings generalize beyond the snapshot.

Publishing original code, analysis, and aggregate findings with an upstream data link is a sensible release approach. The source-content question concerns redistribution, rather than whether the dataset is publicly accessible; raw traces and verbatim excerpts are now excluded. Hugging Face's public-repository terms grant rights through its services; no unrestricted GitHub redistribution license or underlying third-party rights has been verified. Publication authorization was subsequently supplied in the owner's GitHub handoff; it does not change these data-rights limitations.

## Approved release choices and publication

The owner approved MIT for original code and removal of verbatim trace excerpts. `LICENSE` adopts MIT with the collective notice “Copyright (c) 2026 The project contributors”; no personal or company name has been invented. The license excludes upstream data and other third-party material. The previous draft remains in the ignored backup.

Publication displays now show field types, scalar case summaries, and paraphrased interpretations. Raw prompts/messages, tool descriptions, malformed-name fragments, and argument values are omitted. The original study calculations and its 84 code cells are preserved. Two direct transcript quotations in the public audit are paraphrased; the full original audit remains local.

The fresh-kernel workflow and evidence checks passed again after these display changes: all 84 cells executed, all findings were unchanged, and all 38 table/figure artifacts were byte-identical to the prior validated run. Changed publication displays were inspected; all 48 proposed public files passed the link, size, exclusion, credential-pattern, and personal-path checks. Refactoring is complete. The subsequent GitHub handoff authorizes publication; the current publication checks are recorded below.

Unresolved scientific limitations are documented in the study: observational assignment, unknown model/grader/stop semantics, cross-job confounding, incomplete transcript pairing, small groups, no score-difference uncertainty, and no evidence for early prediction or new-job generalization. These require qualified claims and future work, not added experiments in this preparation pass.

## Publication checks — November 8, 2026

The owner selected the authenticated local Git account `yimingzachwang` after it differed from the connected plugin account. The intended destination is the new public repository `yimingzachwang/coding-agent-trace-evaluation`, branch `main`. The existing configured Git author identity is retained.

Reconfirmed before publication: `pip check` passed; all four helper tests passed; `check_review.py --output analysis_outputs --baseline .local_backup/analysis_outputs` passed source/artifact hashes, 84 sequential cells, 15 figures, five reconciliation checks, recorded claims, output hygiene, and retained values across ten historical tables. No analysis or display source changed, so a further full replay was unnecessary. The 48-file allowlist passed local-link, size, credential-pattern, personal-path, and notebook-output checks. The README preparation-status sentence was removed; methodological and data/license limitations remain.

Initial commit `766feb279c90ca5021dfeacdb1d1297c808f23c4` (`Publish agent trace evaluation study`) was pushed successfully to `origin/main`. `origin` is `https://github.com/yimingzachwang/coding-agent-trace-evaluation.git`; `main` tracks `origin/main`. Both `git ls-remote` and the connected GitHub read tools confirmed the same initial commit. Repository visibility is public. Its complete recursive tree contains exactly the 48 allowlisted files, with every blob hash matching the local commit and no excluded files present.

Anonymous HTTP requests returned 200 for the repository and notebook pages. The raw README, executed root notebook, and all three README figures returned 200 and matched local bytes. A follow-up documentation commit records these verified publication checks; its final commit identity is available in Git history and the publication completion report. No analysis sources or generated results changed during publication.

There are no technical publication blockers. Local source data, environments, backups, duplicate executed products, caches, editor files, and handoffs remain preserved and ignored. No website deployment, release, or messages to others were created. Scientific and data-rights limitations above remain applicable.
