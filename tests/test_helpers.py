"""Focused regression tests for explicit loading and occurrence-aware ID auditing."""
import tempfile
import unittest
from pathlib import Path
from datasets import Dataset
import agent_traces_lib as atl


def call(identifier, name='bash'):
    return {'role': 'assistant', 'tool_calls': [{'id': identifier, 'function': {'name': name}}]}


def result(identifier):
    return {'role': 'tool', 'tool_call_id': identifier}


class HelperTests(unittest.TestCase):
    def test_explicit_arrow_loading_and_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.arrow'
            original = Dataset.from_dict({'value': [1, 2]})
            original.save_to_disk(str(Path(directory) / 'saved'))
            path.write_bytes(next((Path(directory) / 'saved').glob('*.arrow')).read_bytes())
            self.assertEqual(atl.load_raw_dataset(path)['value'][:], [1, 2])
            self.assertEqual(len(atl.file_sha256(path)), 64)
            with self.assertRaises(FileNotFoundError):
                atl.load_raw_dataset(Path(directory) / 'absent.arrow')
            with self.assertRaises(ValueError):
                atl.load_raw_dataset(path, split='test')

    def test_occurrences_terminal_and_order(self):
        rows = [
            {'conversation': [call('a'), result('a'), call('a'), result('a')]},
            {'conversation': [result('b'), call('b')]},
            {'conversation': [call('c'), {'role': 'assistant', 'content': 'done'}]},
            {'conversation': [call('d')]},
            {'conversation': [result('x')]},
        ]
        events = atl.audit_tool_ids(rows)
        self.assertEqual(events.groupby('kind').size().to_dict(), {
            'reused_call_id': 1, 'result_before_call': 1, 'unanswered_nonterminal_call': 1,
            'unanswered_terminal_call': 1, 'orphan_result': 1})
        self.assertEqual(events[events.row_id == 0].kind.tolist(), ['reused_call_id'])

    def test_surplus_results_do_not_hide_unanswered_calls(self):
        rows = [{'conversation': [call('a'), call('a'), result('a'), result('other')]}]
        kinds = atl.audit_tool_ids(rows).kind.tolist()
        self.assertCountEqual(kinds, ['reused_call_id','unanswered_nonterminal_call','orphan_result'])

    def test_no_anomalies_has_stable_schema(self):
        events = atl.audit_tool_ids([{'conversation': [call('a'), result('a')]}])
        self.assertEqual(events.columns.tolist(), ['row_id', 'kind', 'msg_index', 'tool'])
        self.assertTrue(events.empty)


if __name__ == '__main__':
    unittest.main()
