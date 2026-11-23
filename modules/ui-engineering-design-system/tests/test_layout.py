"""Counterexamples for the input model. No DOM, browser or AT is executed."""
import copy
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('layout', ROOT / 'checks/layout.py')
layout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(layout)


def base(kind):
    return {'schema': 'C-layout-model/1', 'kind': kind,
            'context': {'id': 'synthetic-state-1', 'coordinate_space': 'viewport-css-px',
                        'css_width': 320, 'css_height': 640, 'scroll_direction': 'vertical'},
            'evidence': {'kind': 'synthetic_geometry', 'ref': 'authored test data; not measured'}}


def target(tid, rect, **changes):
    value = {'id': tid, 'action_id': tid, 'geometry': {'kind': 'effective_rect', 'rect': rect,
             'limitations': [], 'uncertainty': 0}, 'exception': None}
    value.update(changes)
    return value


def target_doc(*values):
    return {**base('targets'), 'targets_complete': True, 'targets': list(values)}


def reflow_doc():
    return {**base('reflow'), 'inventory_complete': True, 'page_overflow': False,
            'required_ids': ['instructions', 'confirm'],
            'regions': [{'id': 'main', 'reflows': True, 'exception': None}],
            'items': [{'id': iid, 'region_id': 'main', 'availability': 'present',
                       'evidence_ref': 'synthetic retained-item record'} for iid in ['instructions', 'confirm']]}


def exception(kind, conditions, ref='authored evidence claim'):
    return {'kind': kind, 'conditions': conditions, 'evidence_ref': ref}


class TargetModelTests(unittest.TestCase):
    def check(self, doc, expected):
        result = layout.inspect(doc)
        self.assertEqual(result['status'], expected, result)
        self.assertEqual(result['ui_status'], 'HOLD')
        self.assertEqual(result['wcag_conformance'], 'NOT_ASSESSED')
        return result

    def test_size_threshold_does_not_round(self):
        for width, size in [(24, 'PASS'), (Decimal('23.999'), 'UNDERSIZED')]:
            result = self.check(target_doc(target('a', [0, 0, width, 24])), 'MODEL_PASS')
            self.assertEqual(result['results'][0]['size'], size)
        # An isolated undersized target can satisfy spacing; this is not a size PASS.

    def test_circle_tangency_and_exact_intrusion(self):
        for x, expected in [(24, 'MODEL_PASS'), (Decimal('23.999999999999999999'), 'MODEL_FAIL')]:
            result = self.check(target_doc(target('a', [0, 0, 20, 20]), target('b', [x, 0, 20, 20])), expected)
            if expected == 'MODEL_FAIL':
                self.assertTrue(any(c['relation'] == 'circle_to_circle' for c in result['results'][0]['collisions']))

    def test_circle_to_large_target_tangency(self):
        for x, expected in [(20, 'MODEL_PASS'), (Decimal('19.999'), 'MODEL_FAIL')]:
            result = self.check(target_doc(target('a', [0, 0, 16, 16]), target('b', [x, 0, 40, 40])), expected)
            self.assertEqual(result['results'][1]['status'], 'PASS_MODEL_SIZE')
            self.assertEqual(result['results'][1]['spacing'], 'NOT_REQUIRED')

    def test_wide_short_neighbor_not_only_center_distance(self):
        result = self.check(target_doc(target('a', [0, 0, 16, 16]), target('b', [0, 17, 100, 16])), 'MODEL_FAIL')
        self.assertEqual([c['relation'] for c in result['results'][0]['collisions']], ['circle_to_target'])

    def test_negative_coordinates_and_translation(self):
        for shift in [-100, 0, Decimal('20.2')]:
            self.check(target_doc(target('a', [shift, -40, 20, 20]), target('b', [shift + 24, -40, 20, 20])), 'MODEL_PASS')

    def test_size_passing_targets_need_no_spacing(self):
        result = self.check(target_doc(target('a', [0, 0, 24, 24]), target('b', [24, 0, 24, 24])), 'MODEL_PASS')
        self.assertTrue(all(r['spacing'] == 'NOT_REQUIRED' for r in result['results']))

    def test_unknown_or_unsupported_geometry_is_hold(self):
        for change in [{'kind': 'circle_bbox'}, {'limitations': ['clip-path']},
                       {'limitations': ['transformed', 'occluded']}, {'uncertainty': Decimal('.001')}]:
            a = target('a', [0, 0, 48, 48]); a['geometry'].update(change)
            self.check(target_doc(a), 'MODEL_HOLD')

    def test_unknown_neighbor_and_incomplete_inventory(self):
        a, b = target('a', [0, 0, 16, 16]), target('b', [200, 200, 24, 24])
        b['geometry']['kind'] = 'border_box_only'
        result = self.check(target_doc(a, b), 'MODEL_HOLD')
        self.assertEqual(result['results'][0]['unknown_neighbors'], ['b'])
        doc = target_doc(a); doc['targets_complete'] = False
        self.check(doc, 'MODEL_HOLD')

    def test_overlap_is_review_even_same_action(self):
        for action in ['a', 'b']:
            result = self.check(target_doc(target('a', [0, 0, 48, 48]), target('b', [10, 10, 48, 48], action_id=action)), 'MODEL_HOLD')
            self.assertEqual(result['results'][0]['overlap_requires_review'], ['b'])

    def test_valid_looking_exceptions_never_auto_accept(self):
        claims = [exception('inline', {'in_sentence': True}),
                  exception('ua', {'ua_determined': True, 'author_resized': False}),
                  exception('essential', {'essential_reason': 'This spatial relation carries information'}),
                  exception('equivalent', {'target_id': 'large', 'same_page': True})]
        for claim in claims:
            with self.subTest(claim=claim):
                doc = target_doc(target('a', [0, 0, 16, 16], exception=claim),
                                 target('b', [17, 0, 16, 16]), target('large', [100, 100, 40, 40], action_id='a'))
                result = self.check(doc, 'MODEL_FAIL')  # b still fails; exception is not an obstacle eraser.
                self.assertEqual(result['results'][0]['status'], 'HOLD_EXCEPTION_REVIEW')
                self.assertEqual(result['results'][0]['exception'], 'REQUIRES_SUBSTANTIVE_REVIEW')
                self.assertTrue(any(c['other'] == 'a' for c in result['results'][1]['collisions']))

    def test_missing_exception_conditions_hold_not_skip(self):
        claims = [exception('inline', {}), exception('inline', {'in_sentence': False}),
                  exception('inline', {'in_sentence': True}, ''), exception('ua', {'ua_determined': True}),
                  exception('essential', {'essential_reason': ''}), exception('equivalent', {'target_id': 'missing', 'same_page': True})]
        for claim in claims:
            result = layout.inspect(target_doc(target('a', [0, 0, 16, 16], exception=claim), target('b', [17, 0, 16, 16])))
            self.assertEqual(result['results'][0]['status'], 'HOLD_EXCEPTION_REVIEW', result)
            self.assertEqual(result['results'][0]['exception'], 'MISSING_CONDITION_OR_EVIDENCE')

    def test_contradicted_exceptions_are_not_approved(self):
        claims = [exception('inline', {'in_sentence': False, 'constrained_by_non_target_line_height': False}),
                  exception('ua', {'ua_determined': True, 'author_resized': True}),
                  exception('ua', {'author_resized': True}),
                  exception('ua', {'ua_determined': False}),
                  exception('equivalent', {'target_id': 'b', 'same_page': False}),
                  exception('equivalent', {'target_id': 'b', 'same_page': True})]
        for claim in claims:
            result = self.check(target_doc(target('a', [0, 0, 16, 16], exception=claim), target('b', [17, 0, 16, 16])), 'MODEL_FAIL')
            self.assertEqual(result['results'][0]['exception'], 'CONDITIONS_CONTRADICT_CLAIM')

    def test_self_or_cyclic_equivalence_not_approved(self):
        for ref in ['a', 'b']:
            a = target('a', [0, 0, 16, 16], action_id='same', exception=exception('equivalent', {'target_id': ref, 'same_page': True}))
            b = target('b', [17, 0, 16, 16], action_id='same', exception=exception('equivalent', {'target_id': 'a', 'same_page': True}))
            result = self.check(target_doc(a, b), 'MODEL_HOLD')
            self.assertTrue(all(r['exception'] == 'MISSING_CONDITION_OR_EVIDENCE' for r in result['results']))

    def test_malformed_conditions_rejected_even_when_size_passes(self):
        for claim in [exception('inline', {'in_sentence': 'yes'}), exception('ua', {'unknown': True}),
                      exception('equivalent', {'target_id': []}), exception('essential', {'essential_reason': True})]:
            self.check(target_doc(target('a', [0, 0, 24, 24], exception=claim)), 'INPUT_ERROR')

    def test_invalid_coordinates_and_dimensions(self):
        for value in [True, '24', None, float('nan'), float('inf'), Decimal('1e1000000'),
                      Decimal('1e-19'), 10**1000]:
            self.check(target_doc(target('a', [0, 0, value, 24])), 'INPUT_ERROR')
        for value in [0, -1]:
            self.check(target_doc(target('a', [0, 0, value, 24])), 'INPUT_ERROR')
        self.check(target_doc(target('a', [Decimal('0e1000000'), 0, 24, 24])), 'MODEL_PASS')

    def test_duplicate_ids_mixed_context_and_unknown_fields(self):
        self.check(target_doc(target('a', [0, 0, 24, 24]), target('a', [40, 0, 24, 24])), 'INPUT_ERROR')
        for extra in [{'context_id': 'different'}, {'coordinate_space': 'screen-px'}, {'invented': True}]:
            self.check(target_doc(target('a', [0, 0, 24, 24], **extra)), 'INPUT_ERROR')

    def test_evidence_claims_never_certify_runtime(self):
        for kind in layout.EVIDENCE:
            doc = target_doc(target('a', [0, 0, 24, 24])); doc['evidence']['kind'] = kind
            result = self.check(doc, 'MODEL_PASS')
            self.assertFalse(result['browser_executed'])
            self.assertFalse(result['at_executed'])
            self.assertFalse(result['evidence_authenticated'])


class ReflowModelTests(unittest.TestCase):
    def test_nonexcepted_retention_at_boundary(self):
        result = layout.inspect(reflow_doc())
        self.assertEqual(result['status'], 'MODEL_PASS')
        self.assertEqual(result['ui_status'], 'HOLD')
        self.assertEqual(result['order_focus_resize_text'], 'NOT_ASSESSED')

    def test_boundary_and_horizontal_scroll_direction(self):
        for width in [319, 321, 1280]:
            doc = reflow_doc(); doc['context']['css_width'] = width
            self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')
        doc = reflow_doc(); doc['context'].update(scroll_direction='horizontal', css_height=256)
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_PASS')

    def test_no_overflow_does_not_prove_required_action_retained(self):
        doc = reflow_doc(); doc['items'][1]['availability'] = 'missing'
        result = layout.inspect(doc)
        self.assertEqual(result['status'], 'MODEL_FAIL')
        self.assertIn('FAIL_REQUIRED_ITEM_LOST', [r['status'] for r in result['results']])

    def test_declared_missing_item_is_not_hidden_by_empty_evidence(self):
        for ref in ['', '   ']:
            doc = reflow_doc(); doc['items'][1].update(availability='missing', evidence_ref=ref)
            result = layout.inspect(doc)
            self.assertEqual(result['status'], 'MODEL_FAIL')
            row = next(r for r in result['results'] if r['id'] == 'confirm')
            self.assertFalse(row['evidence_ref_present'])

    def test_alternative_route_and_missing_observation(self):
        doc = reflow_doc(); doc['items'][1]['availability'] = 'alternative'
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')
        doc['items'][1]['alternative_route'] = 'Open Options, then Confirm; retain the selected date'
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_PASS')
        doc['items'][1]['evidence_ref'] = ''
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')
        doc['items'].pop()
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')

    def test_page_overflow_not_itself_failure_and_exception_stays_review(self):
        doc = reflow_doc(); doc['page_overflow'] = True
        doc['regions'].append({'id': 'video', 'reflows': False, 'exception':
                              {'kind': 'two_dimensional', 'reason': 'Preserve spatial relation in frame', 'evidence_ref': 'review required'}})
        result = layout.inspect(doc)
        self.assertEqual(result['status'], 'MODEL_HOLD')
        self.assertFalse(any(r['status'].startswith('FAIL') for r in result['results']))

    def test_table_exception_does_not_exempt_adjacent_prose(self):
        doc = reflow_doc(); doc['regions'][0]['reflows'] = False
        doc['regions'].append({'id': 'table', 'reflows': False, 'exception':
                              {'kind': 'two_dimensional', 'reason': 'Cross-column comparison', 'evidence_ref': 'unverified'}})
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_FAIL')

    def test_unknown_or_incomplete_observation_holds(self):
        for field, value in [('inventory_complete', False), ('items', [])]:
            doc = reflow_doc(); doc[field] = value
            self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')
        doc = reflow_doc(); doc['regions'][0]['reflows'] = None
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_HOLD')

    def test_malformed_inventory(self):
        for value in [[], {}, None, 1]:
            doc = reflow_doc(); doc['items'][0]['region_id'] = value
            self.assertEqual(layout.inspect(doc)['status'], 'INPUT_ERROR')
        doc = reflow_doc(); doc['required_ids'].append('confirm')
        self.assertEqual(layout.inspect(doc)['status'], 'INPUT_ERROR')

    def test_different_product_inventory_has_no_booking_assumptions(self):
        doc = reflow_doc(); doc['required_ids'] = ['export']; doc['items'] = [
            {'id': 'export', 'region_id': 'main', 'availability': 'present', 'evidence_ref': 'synthetic editor task'}]
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_PASS')
        doc['items'][0]['availability'] = 'missing'
        self.assertEqual(layout.inspect(doc)['status'], 'MODEL_FAIL')


class LayoutCLITests(unittest.TestCase):
    def run_cli(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'; path.write_bytes(payload)
            result = subprocess.run([sys.executable, str(ROOT / 'checks/layout.py'), str(path)], capture_output=True, text=True)
        self.assertNotIn('Traceback', result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_cli_status_exit_codes(self):
        docs = [(reflow_doc(), 0)]
        bad = reflow_doc(); bad['items'][1]['availability'] = 'missing'; docs.append((bad, 1))
        hold = reflow_doc(); hold['inventory_complete'] = False; docs.append((hold, 3))
        docs.append(({}, 2))
        for doc, code in docs:
            self.assertEqual(self.run_cli(json.dumps(doc).encode())[0], code)

    def test_cli_rejects_malformed_encoding_constants_duplicates_and_depth(self):
        for payload in [b'\xff', b'{', b'{"kind":"targets","kind":"reflow"}', b'{"n":NaN}',
                        ('['*1500+'0'+']'*1500).encode(), ('{"n":'+'9'*5000+'}').encode()]:
            code, result = self.run_cli(payload)
            self.assertEqual(code, 2)
            self.assertEqual(result['status'], 'INPUT_ERROR')

    def test_unrepresentable_decimal_exponents_have_structured_errors(self):
        for value in ['1e99999999999999999999999999999999', '1e-99999999999999999999999999999999', '0e99999999999999999999999999999999']:
            code, result = self.run_cli(('{"n":' + value + '}').encode())
            self.assertEqual(code, 2)
            self.assertEqual(result['status'], 'INPUT_ERROR')

    def test_surrogate_strings_round_trip_as_valid_json_not_raw_stdout_bytes(self):
        for value in ['\ud800', '\udcff']:
            doc = reflow_doc(); doc['context']['id'] = value
            code, result = self.run_cli(json.dumps(doc, ensure_ascii=True).encode('ascii'))
            self.assertEqual(code, 0)
            self.assertEqual(result['context_id'], value)
            self.assertEqual(result['ui_status'], 'HOLD')

    def test_checked_examples_remain_explicitly_synthetic(self):
        for filename in ['booking-reflow-model.json', 'toolbar-target-model.json']:
            doc = json.loads((ROOT / 'examples' / filename).read_text())
            self.assertEqual(doc['evidence']['kind'], 'synthetic_geometry')
            self.assertEqual(layout.inspect(doc)['status'], 'MODEL_PASS')


if __name__ == '__main__':
    unittest.main()
