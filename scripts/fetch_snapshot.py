#!/usr/bin/env python3
"""Acquire the revision-pinned dataset externally; do not redistribute it here."""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from datasets import load_dataset
import agent_traces_lib as atl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New local Arrow filename')
    args = parser.parse_args()
    target = args.output.expanduser().resolve()
    if target.exists():
        parser.error('Output already exists; choose a new Arrow filename.')
    meta = json.loads((ROOT / 'data_snapshot.json').read_text())
    ds = load_dataset(meta['dataset_id'], split=meta['split'], revision=meta['hub_revision'])
    if len(ds.cache_files) != 1:
        parser.error('Expected one Arrow shard; inspect source rather than guessing a conversion.')
    source = Path(ds.cache_files[0]['filename'])
    if atl.file_sha256(source) != meta['arrow_sha256']:
        parser.error('Pinned source rebuilt different Arrow bytes. Do not relabel it as the recorded snapshot; obtain the recorded Arrow file or review serialization differences.')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f'Wrote {target.name}; SHA-256 matches the recorded snapshot.')


if __name__ == '__main__':
    main()
