# GitHub publication plan

**Purpose:** Our shared reference for preparing this project for publication.
**Status:** Published publicly on GitHub; local validation and initial remote verification passed.
**Updated:** November 8, 2026.

## Goal

Publish a complete, coherent research project that showcases professional AI research skills, with particular relevance to agent evaluation and benchmark design.

The repository should demonstrate how we formulate research questions, understand unfamiliar data, build reliable analysis, test explanations, and communicate useful conclusions. Present the work confidently, with claims supported by the evidence.

**Study title:** *Coding-Agent Behaviour and Evaluation Reliability: An empirical study of execution traces*

**Working research question:** What can execution traces tell us about coding-agent performance, and how do evaluation design choices affect the conclusions?

The research presentation develops three questions: comparison validity, recorded behaviour across outcomes, and the information supplied by candidate trace summaries.

## Scope

Prepare the existing research for publication. Additional analysis is very unlikely and is not a requirement for completing this project. Use the notebooks, code, saved results, and completed audit as the available evidence, with their provenance made clear.

The main work is scientific writing, organization, correction, and reproducibility. We can rerun existing calculations, verify results, fix implementation errors, and improve figures without expanding the research scope. New experiments, models, statistical comparisons, and robustness studies belong in future work unless we separately agree to include them.

Where the existing evidence cannot answer a question, state the limitation and adjust the claim. A complete account includes what was learned, what remained inconclusive, and why.

## Principles

- Tell the entire scientific story: question, motivation, method, evidence, interpretation, and implications.
- Give null and weak results a proper place. Explain what was tested, what was learned, and what remains unresolved.
- Preserve useful exploratory work and explain why a path was pursued or stopped. Every included analysis should serve a research question.
- Distinguish direct observations, statistical associations, interpretations, and hypotheses.
- Address the issues in [AUDIT.md](AUDIT.md) through factual corrections, accurate methodological descriptions, revised interpretations, and explicit limitations. Update affected conclusions, figures, and summaries using the available evidence.
- Keep the implementation straightforward. Extract reusable logic where it improves clarity or verification; introduce structure as needed.

## The research story

1. **Understand the evaluation setting:** dataset provenance, schema, task/model/job relationships, outcomes, and transcript quality.
2. **Characterize agent behaviour:** success and failure patterns, tool use, efficiency, termination, and representative cases.
3. **Present the signal analyses already performed:** behaviour, run configuration, model identity, task text, and self-reported success, including negative findings.
4. **Assess the strength of the evidence:** explain the comparisons and checks already performed, the audit findings, and the remaining limits on matching, uncertainty, and generalization.
5. **Explain the implications:** what this study establishes and what it suggests for collecting data and designing better evaluations.

## Work order

### 1. Set the scope

- [x] Choose the contribution statement and notebook outline under the implementation handoff authorization.
- [x] Map existing analyses to the research questions.
- [x] Identify which claims are supported, which need qualification or correction, and which questions belong in future work.

### 2. Correct and explain the existing work

- [x] Address the audit findings, prioritizing accurate descriptions of task overlap, feature definitions, cross-job disagreement, and transcript integrity.
- [x] Describe existing uncertainty and sensitivity checks accurately; document checks that were not performed as limitations or future work.
- [x] Correct factual and implementation errors, reconcile claims with available results, and carry changes through the narrative.

### 3. Make the repository reproducible

- [x] Organize the notebook, reusable Python code, and generated outputs clearly.
- [x] Make dataset loading explicit and record the snapshot and dependencies.
- [x] Provide one documented workflow to regenerate the published results.
- [x] Verify that refactoring preserves existing calculations and results, with focused code checks where needed.
- [x] Regenerate or remove artifacts without a current generation path.

### 4. Prepare the public presentation

- [x] Write a clear README covering the question, contributions, main findings, selected figures, and reproduction steps.
- [x] Edit the notebook into a complete research narrative with readable figures and documented methods.
- [x] Add relevant research context and citations, data provenance/access instructions, and appropriate licensing.
- [x] Verify setup and execution from a clean environment, then review the repository for publication.

## Minimum deliverables

- **README:** a concise entry point for researchers and hiring teams.
- **Research notebook:** the full story, including methods, results, null findings, limitations, and implications.
- **Reusable analysis code:** clear functions supporting the notebook and reproducible execution.
- **Published results:** figures and tables generated by the current pipeline.
- **Reproduction essentials:** dependencies, data instructions, run instructions, and verification of the existing workflow.

Keep the existing helper module if it remains easy to maintain. Decide folder names during the refactor. A separate research report is optional if it adds value beyond the notebook.

## Ready to publish when

- The research questions and contributions are clear to someone unfamiliar with the project.
- The narrative, code, tables, figures, and summaries agree.
- Material audit findings are resolved or explicitly documented as remaining limitations.
- The existing work is explained fully, including useful null findings and unresolved questions; publication does not depend on completing future analyses.
- Every published result has a reproducible source, and the documented workflow succeeds in a clean environment.
- Data access, attribution, and licensing are documented, and the repository contains only intended public material.

## Implementation outcome (November 8, 2026)

The study is framed as *Evaluating coding agents through execution traces: success, failure, and the limits of observational benchmarking*. The contribution is a structural audit, linked analysis tables, descriptive behavioural evidence, retrospective classification with existing models, and implications for evaluation design. The original 84 analysis code cells and substantive exploratory paths are retained; unsupported interpretations are corrected or qualified. No additional research studies were added.

The existing root notebook and helper module remain the entry points. A small `scripts/`, `tests/`, `docs/`, and `supporting/` layout supplies execution, focused checks, data/license documentation, and historical preparation source. Generated outputs come from a checksum-verified Arrow snapshot; raw data, backups, environments, duplicate renders, and Parquet checkpoints are excluded from proposed public contents.

The final workflow passed in an isolated Python 3.11.15 environment and a fresh kernel, launched from outside the project directory. All 84 cells ran; 15 saved/embedded figures and 41 generated artifacts were produced. Five reconciliation checks, four helper tests, manifest/claim checks, and comparisons of retained values across ten historical tables passed. See `REVIEW_NOTES.md` for exact commands, caveats, and audit dispositions.

**Approved release choices:** MIT adopted for original analysis code, with collective contributor attribution; verbatim transcript, prompt, tool-description, and argument excerpts removed from publication displays. The historical audit publication copy paraphrases its two transcript quotations; the original remains in the ignored backup. Raw data remains excluded and is acquired upstream.

**Publication outcome:** [coding-agent-trace-evaluation](https://github.com/yimingzachwang/coding-agent-trace-evaluation) is public on `main`. Initial commit `766feb279c90ca5021dfeacdb1d1297c808f23c4` was pushed and verified against the remote branch. All 48 remote file paths and blob hashes match the approved local contents; excluded local files were not uploaded. The README, its three figures, and the notebook are publicly accessible. A follow-up documentation commit records these completed checks.

**Remaining scope:** no publication blockers or further implementation work. Source data is not relicensed or redistributed. Scientific limitations and future work remain documented in the study. Local data, backups, environments, intermediate products, and handoffs remain preserved and ignored. No deployment, release, or messages to others were created.

## Research presentation revision (November 8, 2026)

The research presentation now comprises an expanded README, a continuous study in `docs/STUDY.md`, and a revised executed notebook with fuller abstract, methods, results, and discussion. The shared study title is *Coding-Agent Behaviour and Evaluation Reliability*. Figures use consistent muted colours and revised typography. The notebook retains all 84 analysis code cells and model specifications; no additional research studies were added.

The fresh-kernel replay and evidence checks passed. All 24 numerical data artifacts are byte-identical to the published edition; figure changes are visual. The public allowlist now has 49 files. Previous outputs and editorial source are preserved locally. Validation details and scope are recorded in `REVIEW_NOTES.md`.
