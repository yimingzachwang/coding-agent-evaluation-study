#!/usr/bin/env python3
"""Verify generated evidence, source identity, and notebook execution for local review."""
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import nbformat
from run_analysis import notebook_source_hash
import agent_traces_lib as atl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, help='Optional preserved original output directory')
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = json.loads((output / 'manifest.json').read_text())
    nb = nbformat.read(output / 'executed_analysis.ipynb',4)
    current = nbformat.read(ROOT / 'agent_traces_analysis.ipynb',4)
    assert notebook_source_hash(nb) == notebook_source_hash(current) == manifest['notebook_source_sha256'], 'Stale notebook source'
    for name, digest in manifest['source_sha256'].items():
        assert atl.file_sha256(ROOT / name) == digest, f'Changed source: {name}'
    for name, digest in manifest['files'].items():
        assert atl.file_sha256(output / name) == digest, f'Changed artifact: {name}'
    cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(cells) == 84
    assert [c.execution_count for c in cells] == list(range(1,85))
    assert not [o for c in cells for o in c.outputs if o.output_type == 'error']
    stderr = [o.text for c in cells for o in c.outputs if o.output_type == 'stream' and o.name == 'stderr']
    assert not stderr, f'Notebook stderr needs review: {stderr}'
    images = sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
    figures = list((output / 'figures').glob('*.png'))
    assert images == len(figures) == 15, (images, len(figures))
    report = pd.read_csv(output / 'data_audit/consistency_checks.csv')
    assert len(report) == 5 and report.passed.all()
    f = json.loads((output / 'findings.json').read_text())
    expected = {'n_attempts':370, 'n_tasks':253, 'status_counts':{'OK':218,'WA':121,'IL':26,'TL':5},
                'tasks_with_one_attempt':161,'tasks_with_repeats':92,'multi_model_tasks':79,
                'cyan_common_tasks':18,'cyan_run01_successes':17,'cyan_run07_successes':10,
                'cyan_sign_test_p':0.015625, 'repeated_model_task_groups':26,
                'repeated_groups_disagreeing':8,'repeated_groups_spanning_jobs':25,
                'id_anomaly_counts':{'orphan_result':13,'unanswered_terminal_call':50,'unanswered_nonterminal_call':12,'reused_call_id':1},
                'id_affected_traces':67,'short_wa_traces':8,'short_wa_with_closing_text':2,
                'rate_limited_traces':29, 'text_cluster_count':30, 'repository_families':77}
    for key,value in expected.items():
        assert f[key] == value, (key, f[key], value)
    assert np.isclose(f['maximum_lexical_similarity'],0.883091,atol=1e-6)
    assert round(f['text_cluster_ari'],3) == .387
    assert round(f['assistant_missing_content_fraction']*100,1) == 90.7
    scores = pd.read_csv(output / 'derived_tables/logistic_cv_scores.csv', index_col=0)
    np.testing.assert_allclose(scores.AUC, [0.699179,0.698877,0.703766], atol=1e-6)
    medians = pd.read_csv(output / 'derived_tables/pooled_mixed_task_medians.csv',index_col=0)
    np.testing.assert_allclose(medians.n_messages, [177,104.5])
    subset = pd.read_csv(output / 'derived_tables/raw_and_shared_subset_rates.csv',index_col=0)
    assert subset.n_distinct_subset_tasks.tolist() == [23,24,34,26,16,25,22]
    row = pd.read_parquet(output / 'derived_tables/row_level_final.parquet')
    assert 'user_prompt' not in row and 'final_msg_text' not in row
    if args.baseline:
        count = 0
        for path in (output / 'derived_tables').glob('*.parquet'):
            old_path = args.baseline / 'derived_tables' / path.name
            if not old_path.exists():
                continue
            old, new = pd.read_parquet(old_path), pd.read_parquet(path)
            shared = old.columns.intersection(new.columns).difference(['failure_category'])
            pd.testing.assert_frame_equal(old[shared], new[shared], check_dtype=False)
            count += 1
        print(f'Compared {count} historical Parquet tables: shared retained values match; renamed outcome std and corrected taxonomy excluded.')
    for artifact in output.rglob('*'):
        if artifact.is_file() and artifact.suffix in {'.csv','.json','.ipynb','.html'}:
            text = artifact.read_text()
            assert not re.search(r'(?<![A-Za-z0-9_-])(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)', text), f'Potential credential: {artifact.name}'
            assert not re.search(r'/Users/[A-Za-z0-9_.-]+/|/var/folders/[A-Za-z0-9]+', text), f'Machine path in artifact: {artifact.name}'
    print(f'PASS: 84 sequential cells, {images} embedded/saved figures, five reconciliation checks, recorded claims, hashes, and output hygiene.')


if __name__ == '__main__':
    main()
