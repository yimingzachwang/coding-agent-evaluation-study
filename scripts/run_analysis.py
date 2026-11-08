#!/usr/bin/env python3
"""Execute the research notebook from raw Arrow in a new kernel and fresh directory."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client import KernelManager
import agent_traces_lib as atl


def notebook_source_hash(nb):
    return hashlib.sha256(json.dumps([(c.cell_type, c.source) for c in nb.cells], ensure_ascii=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = args.dataset.expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Output directory must be empty or new; existing results will not be overwritten.')
    identity = json.loads((ROOT / 'data_snapshot.json').read_text())
    checksum = atl.file_sha256(source)
    if checksum != identity['arrow_sha256']:
        parser.error('Snapshot SHA-256 differs from data_snapshot.json; use the documented snapshot.')
    output.mkdir(parents=True, exist_ok=True)
    os.environ.update(AGENT_TRACES_PROJECT_ROOT=str(ROOT), AGENT_TRACES_DATASET=str(source),
                      AGENT_TRACES_OUTPUT=str(output), MPLBACKEND='Agg',
                      HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    # Explicit kernel spec uses the runner's interpreter, not a personal installed kernel.
    kernel_dir = output / 'analysis-kernel'
    kernel_dir.mkdir()
    (kernel_dir / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Analysis Python', 'language': 'python'}))
    manager = KernelSpecManager()
    manager.kernel_dirs = [str(output)]
    nb = nbformat.read(ROOT / 'agent_traces_analysis.ipynb', as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    source_hash = notebook_source_hash(nb)
    print('Executing all analysis cells in a fresh kernel...', flush=True)
    km = KernelManager(kernel_name='analysis-kernel', kernel_spec_manager=manager)
    NotebookClient(nb, km=km, timeout=1200,
                   resources={'metadata': {'path': str(ROOT)}}).execute(cleanup_kc=True)
    nbformat.write(nb, output / 'executed_analysis.ipynb')
    exporter = HTMLExporter()
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    html, _ = exporter.from_notebook_node(nb)
    (output / 'analysis.html').write_text(html)
    (kernel_dir / 'kernel.json').unlink()
    kernel_dir.rmdir()
    files = {str(p.relative_to(output)): atl.file_sha256(p) for p in sorted(output.rglob('*')) if p.is_file()}
    manifest = {'dataset_sha256': checksum, 'dataset_revision': identity['hub_revision'],
                'notebook_source_sha256': source_hash,
                'source_sha256': {str(p.relative_to(ROOT)): atl.file_sha256(p) for p in
                                  [ROOT/'agent_traces_lib.py', Path(__file__).resolve(),
                                   ROOT/'scripts/run_pipeline.py', ROOT/'requirements.txt']},
                'python': sys.version.split()[0],
                'versions': {p: importlib.metadata.version(p) for p in
                             ['datasets','pandas','numpy','matplotlib','scikit-learn','scipy','networkx','pyarrow','nbclient','nbformat','nbconvert','ipykernel']},
                'code_cells_executed': sum(c.cell_type == 'code' for c in nb.cells), 'files': files}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Completed {manifest["code_cells_executed"]} code cells; {len(files)} artifacts. Output: {output}', flush=True)


if __name__ == '__main__':
    main()
