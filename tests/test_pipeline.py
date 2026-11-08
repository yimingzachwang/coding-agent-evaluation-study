"""Exercise the pipeline CLI's input isolation and non-destructive failure paths."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / 'scripts/run_pipeline.py'


class PipelineTests(unittest.TestCase):
    def run_pipeline(self, *args):
        return subprocess.run([sys.executable, str(PIPELINE), *map(str, args)],
                              text=True, capture_output=True, timeout=60)

    def test_populated_output_rejected_before_acquisition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'results'
            output.mkdir()
            sentinel = output / 'existing.txt'
            sentinel.write_text('preserve existing results')
            dataset = root / 'snapshot.arrow'
            result = self.run_pipeline('--acquire', dataset, '--output', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), 'preserve existing results')
            self.assertFalse(dataset.exists())
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_acquisition_cannot_fill_analysis_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results'
            result = self.run_pipeline('--acquire', output / 'snapshot.arrow', '--output', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_wrong_checksum_stops_without_creating_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / 'snapshot.arrow'
            dataset.write_bytes(b'not the pinned snapshot')
            output = root / 'results'
            result = self.run_pipeline('--dataset', dataset, '--output', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Snapshot SHA-256 differs', result.stderr)
            self.assertNotIn('Stage 3/3', result.stdout)
            self.assertFalse(output.exists())
            self.assertEqual(dataset.read_bytes(), b'not the pinned snapshot')


if __name__ == '__main__':
    unittest.main()
