"""
Reusable parsing and table-construction helpers for the mfmVNfpt2q/agent-traces
Hugging Face dataset.

This module is intentionally separate from the notebook so that:
  * the notebook cells stay short and narrative-focused;
  * every derived table is built by one well-named, testable function;
  * the same parsing logic can be reused across sections of the analysis
    (baseline EDA, outcome analysis, conversation analysis, tool-use
    analysis, modelling, etc.) without duplicating explode/parse code.

Design principle: every derived table carries a `row_id` column that is the
positional index into the original Hugging Face dataset (0..369). This is
the join key that lets every table -- messages, tool calls, proxy requests,
tool definitions -- be traced back to the row-level metadata table and to
each other. Nothing here mutates or overwrites the original dataset.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Any
from pathlib import Path
import hashlib

import numpy as np
import pandas as pd
from datasets import Dataset

DATASET_ID = "mfmVNfpt2q/agent-traces"
KNOWN_TOOL_NAMES = {"read", "bash", "edit", "write"}
DATE_RE = re.compile(r"Current date:\s*(\d{4}-\d{2}-\d{2})")

# ---------------------------------------------------------------------------
# Plotting style: a fixed categorical palette (8 hues)
# used consistently across every figure in the notebook. Models are assigned
# hues in a fixed alphabetical order (never re-cycled per chart), and status
# categories use a semantic 4-step "state" palette so severity reads at a
# glance: OK=recorded success, WA=recorded failure; IL/TL semantics remain interpretive.
# ---------------------------------------------------------------------------

CATEGORICAL_PALETTE = [
    "#2a78d6",  # 1 blue
    "#008300",  # 2 green
    "#e87ba4",  # 3 magenta
    "#eda100",  # 4 yellow
    "#1baf7a",  # 5 aqua
    "#eb6834",  # 6 orange
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]
MODEL_ORDER = ["model-atlas", "model-cyan", "model-delta", "model-flint", "model-garnet", "model-orion", "model-vega"]
MODEL_COLORS = dict(zip(MODEL_ORDER, CATEGORICAL_PALETTE))

STATUS_ORDER = ["OK", "WA", "IL", "TL"]
STATUS_COLORS = {
    "OK": "#0ca30c",  # good
    "WA": "#ec835a",  # serious (wrong output)
    "IL": "#fab219",  # warning (iteration/request cap)
    "TL": "#d03b3b",  # critical (wall-clock timeout)
}
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID_COLOR = "#e1e0d9"
SURFACE = "#fcfcfb"


def set_plot_style() -> None:
    """Apply one consistent, muted style to every matplotlib figure in the
    notebook: light surface, hairline gridlines, system sans-serif, ink-toned
    text. Called once near the top of the notebook."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "axes.edgecolor": GRID_COLOR,
            "axes.labelcolor": INK_SECONDARY,
            "axes.titlecolor": INK_PRIMARY,
            "text.color": INK_PRIMARY,
            "xtick.color": INK_MUTED,
            "ytick.color": INK_MUTED,
            "grid.color": GRID_COLOR,
            "grid.linewidth": 0.8,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 10.5,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "figure.dpi": 110,
            "legend.frameon": False,
        }
    )

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_raw_dataset(path: str | Path, split: str = "train") -> Dataset:
    """Read an explicit Arrow snapshot, without cache discovery or network access."""
    if split != "train":
        raise ValueError("This study supports only the train snapshot")
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix != ".arrow":
        raise ValueError("Dataset path must name an Arrow file")
    return Dataset.from_file(str(source))


# ---------------------------------------------------------------------------
# Small parsing primitives (kept separate so they are independently testable)
# ---------------------------------------------------------------------------

def _extract_system_prompt_date(system_prompt: str | None) -> str | None:
    if not system_prompt:
        return None
    m = DATE_RE.search(system_prompt)
    return m.group(1) if m else None


def _safe_len(x: Any) -> int:
    return len(x) if x else 0


def _text_len(x: Any) -> int:
    if x is None:
        return 0
    if isinstance(x, str):
        return len(x)
    return len(str(x))


def _is_blank(x: Any) -> bool:
    return x is None or (isinstance(x, str) and x.strip() == "")


def approx_token_count(text: str | None) -> float:
    """Very rough token estimate (chars / 4). Documented as an approximation,
    not a tokenizer-accurate count -- used only for relative comparisons."""
    if not text:
        return 0.0
    return len(text) / 4.0


# ---------------------------------------------------------------------------
# Row-level metadata + derived scalar features
# ---------------------------------------------------------------------------

def build_row_table(ds: Dataset) -> pd.DataFrame:
    """One row per dataset example (370 rows), combining the original scalar
    columns with derived scalar features summarizing the nested structures.

    This is the central "fact table" that most downstream analysis joins
    against via `row_id`.
    """
    records = []
    for row_id, row in enumerate(ds):
        conv = row["conversation"] or []
        tools = row["tools"] or []
        proxy = row["proxy_requests"] or []

        role_counts = Counter(m.get("role") for m in conv)
        assistant_msgs = [m for m in conv if m.get("role") == "assistant"]
        tool_msgs = [m for m in conv if m.get("role") == "tool"]
        user_msgs = [m for m in conv if m.get("role") == "user"]

        n_tool_calls = sum(len(m.get("tool_calls") or []) for m in assistant_msgs)
        tool_call_names = [
            tc.get("function", {}).get("name")
            for m in assistant_msgs
            for tc in (m.get("tool_calls") or [])
        ]
        n_malformed_tool_calls = sum(
            1 for n in tool_call_names if n not in KNOWN_TOOL_NAMES and n != "task_complete"
        )
        n_task_complete_calls = sum(1 for n in tool_call_names if n == "task_complete")

        reasoning_lens = [
            _text_len(m.get("reasoning_content"))
            for m in assistant_msgs
            if not _is_blank(m.get("reasoning_content"))
        ]
        n_assistant_with_reasoning = len(reasoning_lens)
        n_assistant_blank_content = sum(1 for m in assistant_msgs if _is_blank(m.get("content")))

        total_chars = sum(_text_len(m.get("content")) for m in conv) + sum(
            _text_len(m.get("reasoning_content")) for m in assistant_msgs
        )

        proxy_statuses = Counter(p.get("status") for p in proxy)

        first_role = conv[0].get("role") if conv else None
        last_role = conv[-1].get("role") if conv else None

        records.append(
            {
                "row_id": row_id,
                "model": row["model"],
                "job": row["job"],
                "trial": row["trial"],
                "task_id": row["task_id"],
                "status": row["status"],
                "reward": row["reward"],
                "n_proxy_requests": row["n_proxy_requests"],
                # --- conversation shape ---
                "n_messages": len(conv),
                "n_system_msgs": role_counts.get("system", 0),
                "n_developer_msgs": role_counts.get("developer", 0),
                "n_user_msgs": role_counts.get("user", 0),
                "n_assistant_msgs": role_counts.get("assistant", 0),
                "n_tool_msgs": role_counts.get("tool", 0),
                "first_message_role": first_role,
                "last_message_role": last_role,
                "system_role_convention": "developer" if role_counts.get("developer", 0) > 0 else "system",
                # --- tool use ---
                "n_tools_available": len(tools),
                "tool_names_available": tuple(sorted(t.get("function", {}).get("name") for t in tools)),
                "n_tool_calls": n_tool_calls,
                "n_malformed_tool_calls": n_malformed_tool_calls,
                "n_task_complete_calls": n_task_complete_calls,
                "tool_call_to_msg_ratio": (n_tool_calls / len(assistant_msgs)) if assistant_msgs else np.nan,
                # --- reasoning / content ---
                "n_assistant_with_reasoning": n_assistant_with_reasoning,
                "frac_assistant_with_reasoning": (n_assistant_with_reasoning / len(assistant_msgs)) if assistant_msgs else np.nan,
                "median_reasoning_len": statistics.median(reasoning_lens) if reasoning_lens else np.nan,
                "total_reasoning_chars": sum(reasoning_lens),
                "n_assistant_blank_content": n_assistant_blank_content,
                "total_conversation_chars": total_chars,
                "approx_total_tokens": total_chars / 4.0,
                # --- system prompt / tools text ---
                "system_prompt_len": _text_len(row["system_prompt"]),
                "system_prompt_date": _extract_system_prompt_date(row["system_prompt"]),
                "tools_definition_total_len": sum(
                    _text_len(t.get("function", {}).get("description")) for t in tools
                ),
                # --- proxy requests ---
                "n_proxy_requests_parsed": len(proxy),
                "n_proxy_200": proxy_statuses.get(200, 0),
                "n_proxy_429": proxy_statuses.get(429, 0),
                "n_proxy_503": proxy_statuses.get(503, 0),
                "n_proxy_other": sum(v for k, v in proxy_statuses.items() if k not in (200, 429, 503)),
                "has_rate_limit_events": proxy_statuses.get(429, 0) > 0,
            }
        )

    df = pd.DataFrame.from_records(records)
    df["success"] = (df["status"] == "OK").astype(int)
    assert (df["success"] == df["reward"]).all(), "reward did not match status==OK for all rows"
    return df


# ---------------------------------------------------------------------------
# Message-level table (explode conversation)
# ---------------------------------------------------------------------------

def build_message_table(ds: Dataset) -> pd.DataFrame:
    """One row per conversation message across all 370 traces.

    Preserves `row_id` and `msg_index` (position within the trace) so the
    table can be re-joined to the row-level table or used for within-trace
    sequence analysis (e.g. role-transition matrices).
    """
    records = []
    for row_id, row in enumerate(ds):
        for msg_index, m in enumerate(row["conversation"] or []):
            role = m.get("role")
            content = m.get("content")
            tool_calls = m.get("tool_calls") or []
            records.append(
                {
                    "row_id": row_id,
                    "msg_index": msg_index,
                    "role": role,
                    "content_len": _text_len(content),
                    "content_is_blank": _is_blank(content),
                    "has_reasoning": not _is_blank(m.get("reasoning_content")),
                    "reasoning_len": _text_len(m.get("reasoning_content")),
                    "n_tool_calls": len(tool_calls),
                    "tool_call_id": m.get("tool_call_id"),  # only present for role == 'tool'
                }
            )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Tool-call table (explode assistant tool_calls)
# ---------------------------------------------------------------------------

def build_toolcall_table(ds: Dataset) -> pd.DataFrame:
    """One row per individual tool call made by the assistant.

    `matched_known_tool` flags whether the parsed function name is one of
    the four declared tools (read/bash/edit/write) or the sentinel
    `task_complete` action; everything else is flagged as an unrecognized name; its cause is unknown and documented in the
    data-quality audit rather than silently dropped.
    """
    records = []
    call_counter = 0
    for row_id, row in enumerate(ds):
        for msg_index, m in enumerate(row["conversation"] or []):
            if m.get("role") != "assistant":
                continue
            for tc_index, tc in enumerate(m.get("tool_calls") or []):
                fn = tc.get("function", {}) or {}
                name = fn.get("name")
                args = fn.get("arguments") or {}
                records.append(
                    {
                        "row_id": row_id,
                        "msg_index": msg_index,
                        "tc_index": tc_index,
                        "call_id": tc.get("id"),
                        "name": name,
                        "matched_known_tool": name in KNOWN_TOOL_NAMES or name == "task_complete",
                        "n_arguments": len(args) if isinstance(args, dict) else np.nan,
                        "arg_keys": tuple(sorted(args.keys())) if isinstance(args, dict) else None,
                        "command_arg_len": _text_len(args.get("command")) if isinstance(args, dict) else 0,
                        "path_arg": args.get("path") if isinstance(args, dict) else None,
                        "call_seq": call_counter,
                    }
                )
                call_counter += 1
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Proxy-request table (explode proxy_requests)
# ---------------------------------------------------------------------------

def build_proxy_table(ds: Dataset) -> pd.DataFrame:
    """One row per proxy request. The dataset only records an HTTP-like
    `status` per request (no timestamps, no endpoint/method), so this table
    is deliberately thin -- richer proxy-level analysis (e.g. request type)
    is not possible from the available fields, which is noted explicitly in
    the data-quality audit rather than inferred.
    """
    records = []
    for row_id, row in enumerate(ds):
        for idx, p in enumerate(row["proxy_requests"] or []):
            records.append(
                {
                    "row_id": row_id,
                    "proxy_index": idx,
                    "status": p.get("status"),
                }
            )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Tool-definition table (explode tools)
# ---------------------------------------------------------------------------

def build_tooldef_table(ds: Dataset) -> pd.DataFrame:
    """One row per tool *definition* offered to the agent (not per call)."""
    records = []
    for row_id, row in enumerate(ds):
        for idx, t in enumerate(row["tools"] or []):
            fn = t.get("function", {}) or {}
            params = fn.get("parameters") or {}
            n_props = len((params.get("properties") or {})) if isinstance(params, dict) else np.nan
            records.append(
                {
                    "row_id": row_id,
                    "tool_index": idx,
                    "name": fn.get("name"),
                    "description_len": _text_len(fn.get("description")),
                    "n_parameters": n_props,
                    "strict": fn.get("strict"),
                }
            )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def run_consistency_checks(
    ds: Dataset,
    row_df: pd.DataFrame,
    msg_df: pd.DataFrame,
    toolcall_df: pd.DataFrame,
    proxy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Run a battery of reconciliation assertions between the raw dataset and
    the derived tables. Returns a small report DataFrame (check, passed,
    detail) rather than raising on soft/expected issues; hard structural
    invariants use `assert` because a failure there means a bug in the
    parsing code, not a property of the data.
    """
    results = []

    # Hard invariants: bugs in our own code would violate these.
    assert len(row_df) == len(ds), "row table row count must equal dataset length"
    assert msg_df.groupby("row_id").size().reindex(row_df["row_id"], fill_value=0).equals(
        row_df.set_index("row_id")["n_messages"]
    ), "exploded message counts must reconcile with row-level n_messages"

    # Soft / data-quality checks: report, do not assert, since mismatches are
    # findings about the DATA, not about our parsing.
    proxy_counts = proxy_df.groupby("row_id").size().reindex(row_df["row_id"], fill_value=0)
    mismatch = (proxy_counts.values != row_df["n_proxy_requests"].values).sum()
    results.append(
        {
            "check": "len(proxy_requests) == n_proxy_requests",
            "n_rows_checked": len(row_df),
            "n_failures": int(mismatch),
            "passed": mismatch == 0,
        }
    )

    toolcall_counts = toolcall_df.groupby("row_id").size().reindex(row_df["row_id"], fill_value=0)
    mismatch2 = (toolcall_counts.values != row_df["n_tool_calls"].values).sum()
    results.append(
        {
            "check": "exploded tool-call count == row-level n_tool_calls",
            "n_rows_checked": len(row_df),
            "n_failures": int(mismatch2),
            "passed": mismatch2 == 0,
        }
    )

    dup_trials = row_df["trial"].duplicated().sum()
    results.append(
        {"check": "trial column is unique per row", "n_rows_checked": len(row_df), "n_failures": int(dup_trials), "passed": dup_trials == 0}
    )

    status_reward = (row_df["reward"] == (row_df["status"] == "OK").astype(int)).all()
    results.append(
        {
            "check": "reward == 1{status == 'OK'} for every row",
            "n_rows_checked": len(row_df),
            "n_failures": int((~(row_df["reward"] == (row_df["status"] == "OK").astype(int))).sum()),
            "passed": bool(status_reward),
        }
    )

    job_single_model = row_df.groupby("job")["model"].nunique()
    results.append(
        {
            "check": "each job maps to exactly one model",
            "n_rows_checked": int(job_single_model.shape[0]),
            "n_failures": int((job_single_model != 1).sum()),
            "passed": bool((job_single_model == 1).all()),
        }
    )

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Aggregate table builders
# ---------------------------------------------------------------------------

def build_task_level_table(row_df: pd.DataFrame) -> pd.DataFrame:
    """One row per task_id, summarizing how many models/trials attempted it
    and the spread of outcomes. Useful for identifying tasks that support
    multi-model coverage (n_models > 1)."""
    g = row_df.groupby("task_id")
    out = g.agg(
        n_attempts=("row_id", "size"),
        n_distinct_models=("model", "nunique"),
        n_distinct_jobs=("job", "nunique"),
        mean_reward=("reward", "mean"),
        std_reward=("reward", "std"),
        mean_n_proxy_requests=("n_proxy_requests", "mean"),
        models=("model", lambda s: tuple(sorted(s.unique()))),
    ).reset_index()
    out["outcome_std_within_task"] = out["std_reward"].fillna(0)
    return out


def build_model_level_table(row_df: pd.DataFrame) -> pd.DataFrame:
    """One row per model, with headline aggregate statistics. This is the
    coarsest, most easily-misleading table in the project (see Section 11 /
    Simpson's-paradox checks in the notebook) and should always be read
    alongside the task-overlap descriptions, not in isolation."""
    g = row_df.groupby("model")
    out = g.agg(
        n_trials=("row_id", "size"),
        n_distinct_tasks=("task_id", "nunique"),
        mean_reward=("reward", "mean"),
        median_n_proxy_requests=("n_proxy_requests", "median"),
        mean_n_messages=("n_messages", "mean"),
        mean_n_tool_calls=("n_tool_calls", "mean"),
        mean_malformed_tool_calls=("n_malformed_tool_calls", "mean"),
    ).reset_index()
    return out


def audit_tool_ids(ds: Dataset) -> pd.DataFrame:
    """Count-aware per-trace call/result pairing, with a separate ordering check.

    Pair occurrences of each ID in their observed order, without assuming IDs are
    unique. A terminal unanswered call is descriptive, not proof of a valid cutoff.
    No tool/proxy join or explanation of an anomaly is inferred.
    """
    events = []
    for row_id, row in enumerate(ds):
        conv = row.get("conversation") or []
        calls, results = {}, {}
        for index, message in enumerate(conv):
            if message.get("role") == "assistant":
                for call in message.get("tool_calls") or []:
                    calls.setdefault(call.get("id"), []).append((index, (call.get("function") or {}).get("name")))
            elif message.get("role") == "tool":
                results.setdefault(message.get("tool_call_id"), []).append(index)
        for call_id in calls.keys() | results.keys():
            cs, rs = calls.get(call_id, []), results.get(call_id, [])
            for occurrence, (index, name) in enumerate(cs):
                if call_id is None:
                    kind = "missing_call_id"
                elif occurrence >= len(rs):
                    kind = "unanswered_terminal_call" if index == len(conv)-1 else "unanswered_nonterminal_call"
                elif rs[occurrence] <= index:
                    kind = "result_before_call"
                else:
                    kind = None
                if kind:
                    events.append(dict(row_id=row_id, kind=kind, msg_index=index, tool=name))
            for index in rs[len(cs):]:
                events.append(dict(row_id=row_id, kind="orphan_result", msg_index=index, tool=None))
            for index, name in cs[1:]:
                events.append(dict(row_id=row_id, kind="reused_call_id", msg_index=index, tool=name))
    return pd.DataFrame(events, columns=["row_id", "kind", "msg_index", "tool"]).sort_values(
        ["row_id", "msg_index", "kind"], ignore_index=True)
