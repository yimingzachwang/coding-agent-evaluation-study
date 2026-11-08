# Dataset provenance and access

The study analyzes the `train` split uploaded by **mfmVNfpt2q** as [mfmVNfpt2q/agent-traces on Hugging Face](https://huggingface.co/datasets/mfmVNfpt2q/agent-traces). Credit for the traces belongs to their source and underlying contributors; this repository contributes analysis, not the dataset or agent models.

On November 8, 2026, the [Hub dataset API](https://huggingface.co/api/datasets/mfmVNfpt2q/agent-traces) reported public, ungated access, revision `1be8b9a763288ba2a4efbf8c354bc66cffa50368`, and a source file named `candidate_traces.jsonl`. The API independently confirmed the revision; the local cache-directory name alone was not treated as proof. It reported no card/license metadata, and the README endpoint returned HTTP 404. The local `dataset_info.json` has empty description, citation, homepage, and license fields. Public visibility establishes access, but does not by itself establish unrestricted redistribution rights on GitHub. [Hugging Face's Terms of Service](https://huggingface.co/terms-of-service#your-content) grant users rights in public-repository content through its services and functionalities, while preserving accompanying licenses. We have not verified a dataset-specific license or the rights in underlying third-party content.

`data_snapshot.json` records the Arrow identity: **370 rows**, **102,502,768 bytes**, SHA-256 **`3ee604f3e5b607a4f8d5860ba850f6022616b01b909d881cf6c5f03f8bd09bcb`**. The metadata's logical dataset byte count is 102,486,804; it is not the physical file size. Preserve row order: `row_id` is its positional index, not a global trace identifier. The supported workflow checks exact Arrow bytes before execution.

## Reproducibility and scope

This study uses the publicly accessible Hugging Face source. The local Arrow file is a cached snapshot, not a separate private dataset; the acquisition check reproduced its SHA-256 exactly. Pinning the source revision and recording the checksum allow readers to identify and obtain the analyzed data without this repository redistributing the raw traces.

Public availability supports reproducibility and independent inspection. It does not establish representativeness or generalization to other models, tasks, jobs, or harnesses. The workflow is reusable with compatible data, but the reported findings remain scoped to this snapshot.

## Use a local snapshot

Pass the Arrow file explicitly to the runner. This works offline, without Hugging Face cache discovery. The existing local snapshot remains available in its original directory and is ignored by Git. Do not commit it or the approximately 98 MiB source data.

## Acquire externally

After installing `requirements.txt`, use:

```sh
python scripts/fetch_snapshot.py --output /path/outside/repository/agent-traces-train.arrow
```

This uses `datasets.load_dataset` at the verified revision, then checks its cached Arrow shard against the recorded checksum before copying it. A different serialization is rejected rather than silently treated as identical. It requires network access and source availability; the analysis itself does not. Source access and byte-identical reconstruction must be verified in the intended deployment environment. Do not substitute a current unpinned dataset or manually disable the checksum guard.

## Rights and interpretation

Dataset-specific redistribution terms for the source traces and underlying third-party content remain unverified. The approved release approach publishes original code, scientific narrative, aggregate results, and case identifiers/scalar metadata. Raw data, raw-text tables, and verbatim prompt/message/tool-description/argument excerpts are excluded. Readers obtain the dataset directly from Hugging Face using the pinned acquisition instructions.

The original analysis code is covered by the [MIT License](../LICENSE). Its collective notice names the project contributors; no personal or company attribution has been inferred. This license does not apply to the dataset, embedded issue text, tool outputs, or other externally owned material. Public access supports reproducibility and does not establish broader scientific generalization.

Model labels are anonymized. The grader, exact model identities, harness version, and IL/TL stop rules are undocumented in the verified metadata. Prompt dates are embedded strings, not guaranteed execution timestamps. The notebook marks interpretations accordingly.
