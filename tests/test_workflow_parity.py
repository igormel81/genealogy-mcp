"""Regressions from research practice, using invented people and temporary projects only."""
import unittest

from genealogy_mcp import evidence


class EvidenceSafety(unittest.TestCase):
    def test_different_given_name_is_not_confirmed(self):
        a = dict(given='Иван', surname='Петров', birth_year=1880, birth_place='Тула')
        b = dict(a, given='Алексей')
        self.assertEqual(evidence.check_match(a, b)['verdict'], 'conflict')

    def test_different_villages_are_not_same_place(self):
        a = dict(given='Иван', surname='Петров', birth_year=1880, birth_place='Сынково Тульская губерния')
        b = dict(a, birth_place='Черняевка Тульская губерния')
        self.assertEqual(evidence.check_match(a, b)['verdict'], 'conflict')

    def test_same_named_village_in_different_provinces(self):
        a = dict(given='Иван', surname='Петров', birth_year=1880, birth_place='Сынково Тульская губерния')
        b = dict(a, birth_place='Сынково Московская губерния')
        self.assertEqual(evidence.check_match(a, b)['verdict'], 'conflict')

    def test_one_place_is_only_one_fact(self):
        a = dict(given='Иван', surname='Петров', birth_place='Тула', residence='Тула')
        r = evidence.check_match(a, a)
        self.assertEqual(r['verdict'], 'probable')
        self.assertEqual(len(r['independent_matches']), 1)

    def test_distinct_birth_and_residence_are_two_facts(self):
        a = dict(given='Иван', surname='Петров', birth_place='Тула', residence='Москва')
        self.assertEqual(evidence.check_match(a, a)['verdict'], 'confirmed')

    def test_village_without_province_and_given_equivalent(self):
        a = dict(given='Иван', surname='Петров', birth_year=1880, birth_place='село Сынково, Тульская губерния')
        b = dict(a, given='Іоаннъ', birth_place='Сынково')
        self.assertEqual(evidence.check_match(a, b)['verdict'], 'confirmed')


class ResearchWorkflow(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from unittest.mock import patch
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'GENEALOGY_MCP_HOME': self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_next_active_limit_and_owner_wait(self):
        from genealogy_mcp import project
        with self.assertRaisesRegex(ValueError, 'needs next'):
            project.upsert('test', 'lead', {'title': 'Unclear'})
        project.configure('test', {'max_active_questions': 1})
        first = project.upsert('test', 'lead', {'title': 'Question one', 'next': 'Read certificate', 'status': 'active'})['saved']
        with self.assertRaisesRegex(ValueError, 'active question'):
            project.upsert('test', 'lead', {'title': 'Question two', 'next': 'Read register', 'status': 'active'})
        project.upsert('test', 'lead', {'id': first['id'], 'status': 'waiting_owner', 'blocked_by': 'certificate'})
        with self.assertRaisesRegex(ValueError, 'waiting'):
            project.log('test', 'Search again', 'nothing', lead_id=first['id'], source_id='familysearch')
        with self.assertRaisesRegex(ValueError, 'blocked'):
            project.upsert('test', 'lead', {'id': first['id'], 'status': 'active'})
        project.upsert('test', 'lead', {'id': first['id'], 'status': 'active', 'blocked_by': None})
        self.assertEqual(len(project.research_context('test')['active_questions']), 1)

    def test_stage_gate_and_network_error_is_not_negative_search(self):
        from genealogy_mcp import project
        r = project.upsert('test', 'lead', {'title': 'Question', 'next': 'Read documents', 'expected_sources': ['archive_org']})['saved']
        change = {'id': r['id'], 'stage': 'civil_registry', 'checked': '2026-10-21', 'stage_result': 'Home archive examined'}
        with self.assertRaisesRegex(ValueError, 'sources still unchecked'):
            project.upsert('test', 'lead', change)
        project.log('test', 'Archive search', 'HTTP 503', lead_id=r['id'], source_id='archive_org', outcome='unavailable')
        with self.assertRaisesRegex(ValueError, 'sources still unchecked'):
            project.upsert('test', 'lead', change)
        project.log('test', 'Archive search', 'Not relevant to family documents', lead_id=r['id'], source_id='archive_org', outcome='not_relevant')
        self.assertEqual(project.upsert('test', 'lead', change)['saved']['stage'], 'civil_registry')

    def test_checks_do_not_complete_a_later_stage(self):
        from genealogy_mcp import project
        r = project.upsert('test', 'lead', {'title': 'Question', 'next': 'Read', 'expected_sources': ['familysearch']})['saved']
        project.log('test', 'Search', 'nothing', lead_id=r['id'], source_id='familysearch')
        project.upsert('test', 'lead', {'id': r['id'], 'stage': 'civil_registry', 'checked': '2026-10-21', 'stage_result': 'family completed'})
        with self.assertRaisesRegex(ValueError, 'sources still unchecked'):
            project.upsert('test', 'lead', {'id': r['id'], 'stage': 'existing_documents', 'checked': '2026-10-21', 'stage_result': 'attempt reuse of old check'})

    def test_latest_check_controls_stage_gate_and_plan_includes_books(self):
        from genealogy_mcp import plan, project
        r = project.upsert('test', 'lead', {'title': 'Question', 'next': 'Read', 'expected_sources': ['familysearch']})['saved']
        project.log('test', 'Search', 'nothing', lead_id=r['id'], source_id='familysearch')
        project.log('test', 'Repeat search', '503', lead_id=r['id'], source_id='familysearch', outcome='unavailable')
        with self.assertRaisesRegex(ValueError, 'sources still unchecked'):
            project.upsert('test', 'lead', {'id': r['id'], 'stage': 'civil_registry', 'checked': '2026-10-21', 'stage_result': 'attempt reuse'})
        p = plan.plan('GE', 1880, 1900)
        self.assertIn('iverieli', {x['id'] for x in p['source_checklist']})

    def test_edit_logs_and_dry_run(self):
        from genealogy_mcp import project
        r = project.upsert('test', 'person', {'given_names': 'Example', 'birth': {'date': '1900'}})['saved']
        project.upsert('test', 'person', {'id': r['id'], 'birth': {'date': '1901'}}, dry_run=True)
        self.assertEqual(len(project.load('test')['corrections']), 0)
        project.upsert('test', 'person', {'id': r['id'], 'birth': {'date': '1901'}}, reason='certificate')
        data = project.load('test')
        self.assertEqual(len(data['corrections']), 1)
        self.assertEqual(data['research_log'][-1]['result'], 'certificate')

    def test_custom_archive_is_readable_and_never_written(self):
        import json
        from pathlib import Path
        from genealogy_mcp import project
        folder = Path(self.tmp.name) / 'custom'
        folder.mkdir()
        path = folder / 'family_tree.json'
        data = project.empty()
        data['research_resources'] = [{'id': 'R1', 'name': 'Local catalogue', 'url': 'https://example.org'}]
        path.write_text(json.dumps(data))
        (folder / 'AGENTS.md').write_text('Do not send archive requests.')
        before = path.read_bytes()
        ctx = project.view(str(folder), 'workflow')
        self.assertEqual(ctx['resources'][0]['id'], 'R1')
        self.assertIn('Do not send', ctx['project_instructions'])
        self.assertTrue(project.view(str(folder))['read_only'])
        for fn in (lambda: project.upsert(str(folder), 'person', {'given_names': 'X'}),
                   lambda: project.log(str(folder), 'test', 'test')):
            with self.assertRaisesRegex(ValueError, 'read-only'):
                fn()
        project.configure(str(folder), {'allow_archive_requests': False})
        self.assertFalse(project.view(str(folder), 'workflow')['policy']['allow_archive_requests'])
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((folder / 'site.json').exists())

    def test_project_policy_changes_plan_and_prevents_draft(self):
        from genealogy_mcp import plan, project, server
        project.configure('test', {'allow_archive_requests': False, 'owner_tasks': [{'id': 'cert', 'next': 'Get certificate', 'due': '2000-01-01'}]})
        r = project.upsert('test', 'lead', {'title': 'Question', 'next': 'Waiting for certificate', 'status': 'waiting_owner', 'blocked_by': 'cert'})['saved']
        p = plan.plan('RU', 1958, 1958, context=project.research_context('test'), lead_id=r['id'])
        self.assertEqual(p['status'], 'waiting')
        self.assertEqual(p['sources'], [])
        self.assertEqual(len(p['overdue_owner_tasks']), 1)
        self.assertIn('error', server.draft_archive_request('state_archive', project='test'))
        self.assertNotIn('error', server.draft_archive_request('zags', project='test'))

    def test_moldova_revision_and_current_year(self):
        from genealogy_mcp import plan
        self.assertIn('revision_list', plan.plan('MD', 1816, 1816)['guides'])
        self.assertIn('household_book', plan.plan('RU', 2026, 2026)['guides'])
        for lang in ('en', 'ru'):
            p = plan.plan('RU', 1880, 1900, lang=lang)
            self.assertEqual(p['stages'][0], 'family')
            self.assertIn('source_checklist', p)

    def test_policy_review_precedes_plan_for_custom_instructions(self):
        import json
        from pathlib import Path
        from genealogy_mcp import project, server
        folder = Path(self.tmp.name) / 'custom-policy'
        folder.mkdir()
        (folder / 'family_tree.json').write_text(json.dumps(project.empty()))
        (folder / 'AGENTS.md').write_text('No archive requests for this project.')
        p = server.plan_research('RU', 1880, 1900, project=str(folder))
        self.assertEqual(p['status'], 'review_project_policy')
        self.assertIn('error', server.draft_archive_request('state_archive', project=str(folder)))
        project.configure(str(folder), {'allow_archive_requests': False})
        p = server.plan_research('RU', 1880, 1900, project=str(folder))
        self.assertEqual(p['status'], 'ready')
        self.assertFalse(p['policy']['allow_archive_requests'])
        self.assertEqual(sorted(x.name for x in folder.iterdir()), ['AGENTS.md', 'family_tree.json'])

    def test_gedcom_policy_and_logs_survive_reopening(self):
        import shutil
        from pathlib import Path
        from genealogy_mcp import project
        ged = Path(self.tmp.name) / 'test.ged'
        shutil.copy(Path(__file__).parent / 'sample.ged', ged)
        before = ged.read_bytes()
        project.configure(str(ged), {'allow_archive_requests': False})
        self.assertFalse(project.research_context(str(ged))['policy']['allow_archive_requests'])
        self.assertEqual(ged.read_bytes(), before)
        person = project.view(str(ged))['people_list'][0]
        project.upsert(str(ged), 'person', {'id': person['id'], 'notes': ['An invented test note']}, reason='test note')
        self.assertEqual(project.load(str(ged))['research_log'][-1]['result'], 'test note')


class CatalogueParity(unittest.TestCase):
    def test_direct_sources_and_honest_coverage(self):
        from genealogy_mcp import server, sources
        cat = {s['id']: s for s in sources.catalogue()}
        for key in ('gato', 'gaio', 'gako', 'gavo_voronezh', 'gavo_volgograd', 'ganiko', 'chekhov_archive',
                    'niab_grodno', 'kyiv_city_archive', 'khmelnytsky_archive', 'soldat', 'petrovy', 'pomnim',
                    'warheroes', 'ionb', 'nbuv', 'goskatalog', 'kounb', 'familio', 'genway',
                    'bessarabia_ru', 'familysearch_tree'):
            self.assertIn(key, cat)
            self.assertFalse(cat[key]['coverage_known'])
            self.assertIsNone(server._source_brief(cat[key], 'ru')['years'])
            self.assertNotIn('0–9999', sources.describe(cat[key]))
        self.assertNotEqual(cat['bessarabia_genealogy']['url'], cat['bessarabia_ru']['url'])
        self.assertIn('hosting suspension', sources.describe(cat['khmelnytsky_archive']))

    def test_recent_public_resources_are_in_catalogue(self):
        from genealogy_mcp import sources
        cat = {s['id']: s for s in sources.catalogue()}
        expected = ('hathitrust', 'google_books', 'gallica', 'limedia', 'retronews', 'matchid',
                    'iverieli', 'polona', 'spb_archives', 'don_archives', 'dspl', 'pubmed',
                    'cyberleninka', 'rsl', 'wayback', 'ukrfamily', 'uk_wikisource', 'digibuc',
                    'bcu_cluj', 'moldavica', 'arcanum', 'asp_moldova', 'patronim', 'famiry', 'familyspace')
        for source_id in expected:
            self.assertIn(source_id, cat)
            self.assertFalse(cat[source_id]['coverage_known'])
        self.assertNotEqual(cat['wayback']['url'], cat['archive_org']['url'])
        self.assertEqual(cat['patronim']['records'], ['catalogs'])
        self.assertEqual(cat['asp_moldova']['access'], 'request')
        self.assertNotIn('fstanitsa', cat)  # current domain no longer represents the cited historical resource

    def test_shipped_workflow_and_entry_prompts(self):
        from genealogy_mcp import server
        self.assertIn('waiting_owner', server.res_workflow())
        self.assertIn('source_id', server.start_research('An invented ancestor'))
        self.assertIn('policy', server.archive_request('Invented', 'birth record'))
