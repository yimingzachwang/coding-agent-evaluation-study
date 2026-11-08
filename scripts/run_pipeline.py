#!/usr/bin/env python3
"""Acquire or load the pinned snapshot, execute the analysis, and verify its evidence."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--dataset', type=Path, help='Existing checksum-matching Arrow snapshot')
    source.add_argument('--acquire', type=Path, help='Acquire the pinned snapshot to this new Arrow filename')
    parser.add_argument('--output', required=True, type=Path, help='New or empty analysis directory')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error('Output directory must be empty or new; existing results will not be overwritten.')
    dataset = (args.dataset or args.acquire).expanduser().resolve()
    if dataset.suffix != '.arrow':
        parser.error('Dataset path must use the .arrow extension.')
    if dataset == output or output in dataset.parents:
        parser.error('Keep the dataset outside the analysis output directory.')
    if args.acquire and dataset.exists():
        parser.error('Acquisition target already exists; use --dataset or choose a new filename.')
    if args.dataset and not dataset.is_file():
        parser.error('Dataset file does not exist.')
    if args.acquire:
        print('Stage 1/3: acquire the revision-pinned, checksum-verified snapshot.', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'scripts/fetch_snapshot.py'),
                        '--output', str(dataset)], check=True)
    else:
        print('Stage 1/3: use the local snapshot; the analysis runner verifies its checksum.', flush=True)
    print('Stage 2/3: execute the complete analysis in a fresh kernel.', flush=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/run_analysis.py'),
                    '--dataset', str(dataset), '--output', str(output)], check=True)
    print('Stage 3/3: verify execution, reconciliation, claims, hashes, and output hygiene.', flush=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_review.py'),
                    '--output', str(output)], check=True)
    print('Pipeline complete: analysis and evidence verification passed.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
