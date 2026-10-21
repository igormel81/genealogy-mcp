import copy
import json
import tempfile
import unittest
from pathlib import Path

from genealogy_mcp import event_evidence, project, server


class EventEvidence(unittest.TestCase):
    def data(self):
        return {'root_person_id': 'I1', 'people': [
            {'id': 'I1', 'source_ids': ['S1'], 'birth': {'date': '1900', 'place': 'Example'},
             'death': {'date': '1980', 'source_ids': ['S2']}, 'burial': {'place': 'Example', 'source_ids': ['missing']}},
            {'id': 'I2', 'birth': {'date': '1870', 'source_ids': ['S1']}},
            {'id': 'I3', 'birth': {'date': '1800'}}],
            'families': [{'id': 'F1', 'partners': ['I2'], 'children': ['I1'],
                          'marriage': {'date': '1899'}, 'source_ids': ['S1']}],
            'sources': [{'id': 'S1', 'title': 'Invented register', 'locator': 'Fond 1, file 2, folio 3'},
                        {'id': 'S2', 'title': 'Unlocated note', 'url': 'https://example.org'}]}

    def test_event_not_covered_by_person_source_and_no_truth_verdict(self):
        data = self.data()
        before = copy.deepcopy(data)
        r = event_evidence.report(data)
        events = {(x['record_id'], x['event']): x for x in r['items']}
        self.assertEqual(events['I1', 'birth']['status'], 'missing_reference')
        self.assertEqual(events['I1', 'death']['status'], 'needs_locator')
        self.assertEqual(events['I1', 'burial']['status'], 'broken_reference')
        self.assertEqual(events['I2', 'birth']['status'], 'reference_present')
        self.assertEqual(events['F1', 'marriage']['status'], 'missing_reference')
        self.assertNotIn('I3', {x['record_id'] for x in r['items']})
        self.assertNotIn('confirmed', str(r))
        self.assertEqual(data, before)

    def test_large_transcription_is_explicitly_truncated(self):
        data = self.data()
        data['sources'][0]['scope'] = 'x' * 3000
        result = event_evidence.report(data)
        citation = next(row for row in result['items'] if row['record_id'] == 'I2')['citations'][0]
        self.assertTrue(citation['transcription_truncated'])
        self.assertEqual(len(citation['transcription']), 2000)
        self.assertEqual(len(data['sources'][0]['scope']), 3000)

    def test_depth_limit_truncation_and_invalid_root(self):
        data = self.data()
        r = event_evidence.report(data, generations=0, limit=1)
        self.assertEqual(r['people_considered'], 1)
        self.assertEqual(r['events'], 3)
        self.assertEqual(r['truncated'], 2)
        self.assertEqual(r['items'][0]['status'], 'broken_reference')
        with self.assertRaisesRegex(ValueError, 'root person'):
            event_evidence.report(data, root_person_id='missing')
        for kwargs in ({'limit': 0}, {'limit': 1001}, {'generations': 11}):
            with self.assertRaises(ValueError):
                event_evidence.report(data, **kwargs)

    def test_cycles_terminate_and_adoption_is_not_biological_ancestry(self):
        data = self.data()
        data['families'].append({'id': 'F2', 'partners': ['I1'], 'children': ['I2']})
        self.assertEqual(event_evidence.report(data)['people_considered'], 2)
        data['families'][0]['adopted_children'] = ['I1']
        self.assertEqual(event_evidence.report(data)['people_considered'], 1)

    def test_mcp_reads_custom_folder_without_writes_or_http_access(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'family_tree.json'
            path.write_text(json.dumps(self.data()))
            before = path.read_bytes()
            result = server.project_evidence(folder)
            self.assertEqual(result['events'], 5)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(folder).iterdir()), [path])
        previous = server.ALLOW_FILES
        server.ALLOW_FILES = False
        try:
            self.assertIn('error', server.project_evidence('/tmp/unused'))
        finally:
            server.ALLOW_FILES = previous

    def test_gedcom_event_citations_survive_in_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tree.ged'
            path.write_text('0 HEAD\n1 CHAR UTF-8\n0 @I1@ INDI\n1 NAME Example /Person/\n1 BIRT\n2 DATE 1900\n2 SOUR @S1@\n0 @S1@ SOUR\n1 TITL Register\n1 PUBL Archive, file 1, folio 2\n0 TRLR\n')
            before = path.read_bytes()
            result = event_evidence.report(project.load(str(path)))
            self.assertEqual(result['items'][0]['status'], 'reference_present')
            self.assertEqual(path.read_bytes(), before)
