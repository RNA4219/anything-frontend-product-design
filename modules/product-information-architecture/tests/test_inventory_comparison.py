"""IA preservation counterexamples; the helper is a diff, never an approval gate."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).parents[1]
FIXTURES = Path(__file__).parent / 'inventory-fixtures'
spec = importlib.util.spec_from_file_location('inventory_diff', MODULE / 'checks/compare_inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def case(name):
    base = FIXTURES / name
    return [json.loads((base / n).read_text()) for n in ['before.json', 'after.json']]


class InventoryComparisonTests(unittest.TestCase):
    def test_equal_total_and_category_counts_do_not_hide_membership_swap(self):
        before, after = case('equal-count-membership-swap')
        r = inventory.compare(before, after)
        self.assertEqual('COMPARED', r['status'])
        self.assertEqual('NOT_EVALUATED', r['decision'])
        self.assertEqual({'D2', 'D3'}, {x['id'] for x in r['differences']['records']['changed_fields']})
        for concept in ['P', 'Q']:
            self.assertEqual(sum(concept in x['concept_ids'] for x in before['records']),
                             sum(concept in x['concept_ids'] for x in after['records']))

    def test_same_count_compensated_id_loss_and_declared_conditions_are_exposed(self):
        base = FIXTURES
        b = json.loads((base / 'source-inventory.json').read_text())
        a = json.loads((base / 'proposed-inventory.json').read_text())
        r = inventory.compare(b, a)
        delta = r['differences']['records']
        self.assertEqual({'before':96, 'after':96}, r['counts']['records'])
        self.assertEqual(['ITEM-073'], delta['removed_ids'])
        self.assertEqual(['ITEM-X73'], delta['added_ids'])
        self.assertEqual(['ITEM-088'], [x['id'] for x in delta['changed_fields'] if x['field'] == 'scope'])
        self.assertEqual(['ITEM-090'], [x['id'] for x in delta['changed_fields'] if x['field'] == 'roles'])
        changes = {x['id']: x for x in delta['changed_fields'] if x['field'] == 'concept_ids'}
        for item_id in ['ITEM-015','ITEM-030','ITEM-045','ITEM-060','ITEM-075','ITEM-090']:
            self.assertIn('material.unspecified', changes[item_id]['before']['value'])
            self.assertNotIn('material.unspecified', changes[item_id]['after']['value'])

    def test_authorized_rename_and_unused_retirement_are_diffs_not_failures(self):
        b, a = case('approved-label-and-unused-concept')
        r = inventory.compare(b, a)
        self.assertEqual('COMPARED', r['status'])
        self.assertEqual('NOT_EVALUATED', r['decision'])
        self.assertEqual([], r['differences']['records']['changed_fields'])
        self.assertEqual(['unused'], r['differences']['concepts']['removed_ids'])
        self.assertEqual('label', r['differences']['concepts']['changed_fields'][0]['field'])

    def test_order_only_changes_are_not_membership_changes(self):
        b, _ = case('equal-count-membership-swap')
        b['records'][0]['concept_ids'] = ['P', 'Q']
        a = copy.deepcopy(b)
        a.update(revision='v2', basis_revision='v1')
        a['records'].reverse()
        a['records'][-1]['concept_ids'].reverse()
        r = inventory.compare(b, a)
        self.assertFalse(any(x['changed_fields'] or x['added_ids'] or x['removed_ids']
                             for x in r['differences'].values()))

    def test_duplicate_ids_do_not_silently_overwrite_rows(self):
        for collection in ['records', 'concepts']:
            with self.subTest(collection=collection):
                b, a = case('equal-count-membership-swap')
                a[collection].append(copy.deepcopy(a[collection][0]))
                self.assertEqual('INVALID_INPUT', inventory.compare(b, a)['status'])

    def test_malformed_data_reports_locations_without_crashing(self):
        b, a = case('equal-count-membership-swap')
        invalid = [[], None, {'case_id':'bad'}]
        for value in [None, 'reader', [None], [['nested']], ['reader', 'reader']]:
            item = copy.deepcopy(a)
            item['records'][0]['roles'] = value
            invalid.append(item)
        for item in invalid:
            with self.subTest(item=item):
                r = inventory.compare(b, item)
                self.assertEqual('INVALID_INPUT', r['status'])
                self.assertTrue(r['errors'])

    def test_wrong_basis_revision_is_visible_even_without_data_change(self):
        b, _ = case('equal-count-membership-swap')
        a = copy.deepcopy(b)
        a.update(revision='v2', basis_revision='different-source')
        r = inventory.compare(b, a)
        self.assertFalse(r['basis']['basis_matches'])
        self.assertTrue(r['input_warnings'])
        self.assertEqual('NOT_EVALUATED', r['decision'])

    def test_partial_snapshot_does_not_invent_external_concepts(self):
        b, a = case('equal-count-membership-swap')
        b['records'][0]['concept_ids'].append('external')
        r = inventory.compare(b, a)
        self.assertEqual('COMPARED', r['status'])
        self.assertEqual('external', r['references_not_in_snapshot'][0]['id'])
        self.assertFalse(r['checks_available']['whole_inventory_completeness'])

    def test_ignored_fields_and_unverified_semantics_are_explicit(self):
        b, a = case('equal-count-membership-swap')
        a['records'][0]['business_rule'] = 'unverified'
        a['approved'] = True
        r = inventory.compare(b, a)
        self.assertIn('after.records[].business_rule', r['unexamined_fields'])
        self.assertIn('after.approved', r['unexamined_fields'])
        self.assertFalse(r['checks_available']['change_authorization'])
        self.assertFalse(r['checks_available']['semantic_equivalence'])

    def test_finite_1200_record_population_detects_a_compensated_loss(self):
        b, _ = case('equal-count-membership-swap')
        base = b['records'][0]
        b['records'] = [dict(copy.deepcopy(base), id=f'R{i:04d}', label=f'Record {i}') for i in range(1200)]
        a = copy.deepcopy(b)
        a.update(revision='v2', basis_revision='v1')
        a['records'][731]['id'] = 'R-new'
        r = inventory.compare(b, a)
        self.assertEqual({'before':1200,'after':1200}, r['counts']['records'])
        self.assertEqual(['R0731'], r['differences']['records']['removed_ids'])
        self.assertEqual(['R-new'], r['differences']['records']['added_ids'])

    def test_missing_optional_hierarchy_is_not_inferred_as_confirmed_empty(self):
        b, a = case('equal-count-membership-swap')
        a['concepts'][0]['parent_ids'] = []
        r = inventory.compare(b, a)
        change = next(x for x in r['differences']['concepts']['changed_fields'] if x['field']=='parent_ids')
        self.assertFalse(change['before']['present'])
        self.assertTrue(change['after']['present'])

    def test_cli_rejects_output_aliases_without_changing_either_source(self):
        b, a = case('equal-count-membership-swap')
        for mode in ['same_path', 'symlink', 'hardlink']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                before, after = folder / 'before.json', folder / 'after.json'
                before.write_text(json.dumps(b))
                after.write_text(json.dumps(a))
                originals = [before.read_bytes(), after.read_bytes()]
                output = before if mode == 'same_path' else folder / 'result.json'
                if mode == 'symlink':
                    try:
                        output.symlink_to(after)
                    except OSError as error:
                        if getattr(error, 'winerror', None) == 1314:
                            self.skipTest('Windows でシンボリックリンクを作成する権限が必要')
                        raise
                elif mode == 'hardlink':
                    output.hardlink_to(before)
                run = subprocess.run([sys.executable, str(MODULE / 'checks/compare_inventory.py'),
                                      '--before', str(before), '--after', str(after), '--output', str(output)],
                                     capture_output=True, text=True)
                self.assertEqual(2, run.returncode, run.stderr)
                self.assertEqual('INVALID_INPUT', json.loads(run.stdout)['status'])
                self.assertEqual(originals, [before.read_bytes(), after.read_bytes()])

    def test_cli_separate_output_preserves_inputs_and_reports_comparison(self):
        b, a = case('equal-count-membership-swap')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            before, after, output = [folder / n for n in ['before.json', 'after.json', 'comparison.json']]
            before.write_text(json.dumps(b))
            after.write_text(json.dumps(a))
            originals = [before.read_bytes(), after.read_bytes()]
            run = subprocess.run([sys.executable, str(MODULE / 'checks/compare_inventory.py'),
                                  '--before', str(before), '--after', str(after), '--output', str(output)],
                                 capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)
            self.assertEqual('COMPARED', json.loads(output.read_text())['status'])
            self.assertEqual(originals, [before.read_bytes(), after.read_bytes()])
