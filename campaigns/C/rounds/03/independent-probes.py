#!/usr/bin/env python3
"""Independent, CLI-only critic probes for SESSION C round 03.

No browser, server, DOM double, candidate import, or candidate tests are used.
Inputs/expectations are authored here; the tested program is only invoked as a
subprocess. An existing result file is never overwritten. Third-party source
text is not embedded. Decimal literals are serialized without float conversion.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROUND = Path(__file__).resolve().parent
ROOT = ROUND.parents[3]
CANDIDATE = ROOT / 'modules/ui-engineering-design-system/checks/layout.py'
SNAPSHOT = ROUND / 'candidate-snapshot.json'
EXIT_CODES = {'MODEL_PASS': 0, 'MODEL_FAIL': 1, 'INPUT_ERROR': 2, 'MODEL_HOLD': 3}
CASES = []


def wire(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return '{' + ','.join(json.dumps(k, ensure_ascii=True) + ':' + wire(v) for k, v in obj.items()) + '}'
    if isinstance(obj, list):
        return '[' + ','.join(wire(v) for v in obj) + ']'
    return json.dumps(obj, ensure_ascii=True, allow_nan=False)


def base(kind):
    return {'schema': 'C-layout-model/1', 'kind': kind,
            'context': {'id': 'independent-report-editor-state', 'coordinate_space': 'viewport-css-px',
                        'css_width': 320, 'css_height': 640, 'scroll_direction': 'vertical'},
            'evidence': {'kind': 'synthetic_geometry', 'ref': 'Independent authored counterexample; no rendered measurements'}}


def target(tid, rect, *, action=None, exception=None, geometry=None):
    g = {'kind': 'effective_rect', 'rect': rect, 'limitations': [], 'uncertainty': 0}
    if geometry:
        g.update(geometry)
    return {'id': tid, 'action_id': action or tid, 'geometry': g, 'exception': exception}


def targets(*values, complete=True):
    d = base('targets')
    d.update(targets_complete=complete, targets=list(values))
    return d


def exception(kind, conditions, evidence='Synthetic exception claim; substantive review not performed'):
    return {'kind': kind, 'conditions': conditions, 'evidence_ref': evidence}


def reflow():
    d = base('reflow')
    d.update(inventory_complete=True, page_overflow=False,
             required_ids=['report-instructions', 'export-report'],
             regions=[{'id': 'prose', 'reflows': True, 'exception': None},
                      {'id': 'actions', 'reflows': True, 'exception': None}],
             items=[{'id': 'report-instructions', 'region_id': 'prose', 'availability': 'present',
                     'evidence_ref': 'Synthetic long instructions retained'},
                    {'id': 'export-report', 'region_id': 'actions', 'availability': 'present',
                     'evidence_ref': 'Synthetic long export label and action retained'}])
    return d


def add(cid, doc, status, *, rows=None, relations=None, issues=None, source='evaluation-plan.md',
        note='', origin='independent_critic', raw=None, allowed_status=None, pad_to=None):
    payload = raw if raw is not None else wire(doc).encode('ascii')
    CASES.append({'id': cid, 'payload': payload, 'pad_to': pad_to,
                  'expect': {'status': status, 'allowed_status': allowed_status, 'rows': rows or {},
                             'relations': relations or {}, 'issue_code': issues},
                  'source': source, 'note': note, 'origin': origin})


def build_cases():
    # Geometry: independently chosen centres, diagonal exact tangencies, all sides,
    # translations, and a long thin rectangle that defeats centre-only checks.
    for width, height, size in [(24, 24, 'PASS'), (Decimal('23.999'), 24, 'UNDERSIZED'),
                                (24, Decimal('23.999'), 'UNDERSIZED'),
                                (Decimal('23.999999999999999999'), 24, 'UNDERSIZED'),
                                (48, Decimal('0.000000000000000001'), 'UNDERSIZED')]:
        add(f'G-size-{width}-{height}', targets(target('a', [-37, -53, width, height])), 'MODEL_PASS',
            rows={'a': {'size': size, 'spacing': 'NOT_REQUIRED' if size == 'PASS' else 'PASS'}},
            note='An isolated undersized target can pass spacing, but must not be rounded into size PASS.')
    for delta, expected in [('18.2', 'MODEL_PASS'), ('18.199999999999999999', 'MODEL_FAIL'),
                            ('18.200000000000000001', 'MODEL_PASS')]:
        add('G-diagonal-circles-' + delta,
            targets(target('a', [-1, -1, 2, 2]), target('b', [Decimal('13.4'), Decimal(delta), 2, 2])), expected,
            relations={'a': ['circle_to_circle'], 'b': ['circle_to_circle']} if expected == 'MODEL_FAIL' else {},
            note='Centres (0,0) and (14.4,19.2) have exact distance 24; perturbation is 1e-18 CSS px.')
    for top, expected in [('9.6', 'MODEL_PASS'), ('9.599999999999999999', 'MODEL_FAIL'),
                          ('9.600000000000000001', 'MODEL_PASS')]:
        add('G-diagonal-circle-rectangle-' + top,
            targets(target('a', [-1, -1, 2, 2]), target('b', [Decimal('7.2'), Decimal(top), 24, 24])), expected,
            rows={'b': {'status': 'PASS_MODEL_SIZE', 'spacing': 'NOT_REQUIRED'}},
            relations={'a': ['circle_to_target']} if expected == 'MODEL_FAIL' else {},
            note='Closest corner (7.2,9.6) lies on radius 12; checks rectangle distance, not its centre.')
    for side, rect in [('left', [-36, -12, 24, 24]), ('right', [12, -12, 24, 24]),
                       ('above', [-12, -36, 24, 24]), ('below', [-12, 12, 24, 24])]:
        add('G-four-side-tangency-' + side, targets(target('a', [-1, -1, 2, 2]), target('b', rect)),
            'MODEL_PASS', rows={'a': {'status': 'PASS_MODEL_SPACING'}})
    add('G-wide-thin-neighbor', targets(target('a', [-1, -1, 2, 2]), target('b', [-10, 9, 100, 2])),
        'MODEL_FAIL', rows={'a': {'status': 'FAIL_MODEL_SPACING'}, 'b': {'status': 'PASS_MODEL_SPACING'}},
        relations={'a': ['circle_to_target']},
        note='Centres are more than 24 apart; a circle still enters the full long thin rectangle.')
    add('G-large-edge-contact', targets(target('a', [0, 0, 24, 24]), target('b', [24, 0, 80, 24])),
        'MODEL_PASS', rows={'a': {'spacing': 'NOT_REQUIRED'}, 'b': {'spacing': 'NOT_REQUIRED'}})
    for shift in [Decimal('-999999999'), Decimal('-17.125'), Decimal('999999900')]:
        add('G-translation-' + str(shift), targets(target('a', [shift, -8, 2, 2]),
                                                   target('b', [shift + 24, -8, 2, 2])), 'MODEL_PASS')
    for kind in ['circle_bbox', 'rotated_rectangle', 'border_box_only']:
        add('G-unsupported-' + kind, targets(target('a', [0, 0, 24, 24], geometry={'kind': kind})),
            'MODEL_HOLD', rows={'a': {'status': 'HOLD_GEOMETRY'}})
    for limitation in ['clip-path', 'occluded', 'transformed', 'multiple-fragments', 'iframe-unresolved']:
        add('G-limitation-' + limitation, targets(target('a', [0, 0, 80, 80], geometry={'limitations': [limitation]})),
            'MODEL_HOLD', rows={'a': {'status': 'HOLD_GEOMETRY'}})
    add('G-uncertainty', targets(target('a', [0, 0, 24, 24], geometry={'uncertainty': Decimal('.000000001')})),
        'MODEL_HOLD')
    add('G-unknown-far-neighbor', targets(target('a', [-1, -1, 2, 2]),
                                       target('unknown', [900, 900, 100, 100], geometry={'kind': 'circle_bbox'})),
        'MODEL_HOLD', rows={'a': {'status': 'HOLD_NEIGHBORS', 'unknown_neighbors': ['unknown']}})
    for same_action in [False, True]:
        add('G-overlap-' + str(same_action), targets(target('a', [0, 0, 48, 48], action='same'),
                                                   target('b', [1, 1, 48, 48], action='same' if same_action else 'other')),
            'MODEL_HOLD', rows={'a': {'status': 'HOLD_GEOMETRY', 'overlap_requires_review': ['b']}})
    for width in [2, 24]:
        add('G-incomplete-' + str(width), targets(target('a', [0, 0, width, 24]), complete=False), 'MODEL_HOLD')

    # Exceptions: the independently authored collision puts a 2x2 target by a
    # size-compliant rectangle, so a wrong HOLD cannot hide behind another FAIL.
    claims = [exception('inline', {'in_sentence': True}),
              exception('inline', {'constrained_by_non_target_line_height': True}),
              exception('ua', {'ua_determined': True, 'author_resized': False}),
              exception('essential', {'legal_requirement': 'Synthetic legal claim only'}),
              exception('equivalent', {'target_id': 'equivalent', 'same_page': True})]
    for idx, claim in enumerate(claims):
        add('E-named-review-' + str(idx), targets(target('a', [-1, -1, 2, 2], exception=claim),
                                                target('obstacle', [10, -12, 24, 24]),
                                                target('equivalent', [100, 100, 24, 24], action='a')),
            'MODEL_HOLD', rows={'a': {'status': 'HOLD_EXCEPTION_REVIEW', 'exception': 'REQUIRES_SUBSTANTIVE_REVIEW'}})
    for idx, claim in enumerate([exception('inline', {'in_sentence': True}, ''),
                                 exception('ua', {'ua_determined': True}),
                                 exception('ua', {'author_resized': False}),
                                 exception('inline', {'in_sentence': False}),
                                 exception('essential', {'essential_reason': ''}),
                                 exception('equivalent', {'same_page': True, 'target_id': 'absent'})]):
        add('E-incomplete-review-' + str(idx), targets(target('a', [-1, -1, 2, 2], exception=claim),
                                                     target('obstacle', [10, -12, 24, 24])),
            'MODEL_HOLD', rows={'a': {'status': 'HOLD_EXCEPTION_REVIEW', 'exception': 'MISSING_CONDITION_OR_EVIDENCE'}})
    for idx, claim in enumerate([exception('ua', {'ua_determined': False, 'author_resized': False}),
                                 exception('ua', {'ua_determined': True, 'author_resized': True}),
                                 exception('inline', {'in_sentence': False, 'constrained_by_non_target_line_height': False}),
                                 exception('essential', {'essential_reason': '', 'legal_requirement': ''}),
                                 exception('equivalent', {'target_id': 'obstacle', 'same_page': True}),
                                 exception('equivalent', {'same_page': False})]):
        add('E-complete-contradiction-' + str(idx), targets(target('a', [-1, -1, 2, 2], exception=claim),
                                                         target('obstacle', [10, -12, 24, 24])),
            'MODEL_FAIL', rows={'a': {'status': 'FAIL_MODEL_SPACING', 'exception': 'CONDITIONS_CONTRADICT_CLAIM'}})
    for key, val in [('author_resized', True), ('ua_determined', False)]:
        add('E-ua-partial-contradiction-' + key,
            targets(target('a', [-1, -1, 2, 2], exception=exception('ua', {key: val})),
                    target('obstacle', [10, -12, 24, 24])),
            'MODEL_FAIL', rows={'a': {'status': 'FAIL_MODEL_SPACING', 'exception': 'CONDITIONS_CONTRADICT_CLAIM'}},
            source='evaluation-plan.md §4; C-S007 SC2.5.8 User Agent Control; C-S033 Exceptions',
            note='One false conjunct suffices to contradict UA-determined AND not-author-resized; the other missing conjunct cannot rescue it.')
    add('E-exception-still-obstacle', targets(target('a', [-1, -1, 2, 2]),
                                             target('excepted', [10, -1, 2, 2], exception=exception('inline', {'in_sentence': True}))),
        'MODEL_FAIL', rows={'a': {'status': 'FAIL_MODEL_SPACING'}, 'excepted': {'status': 'HOLD_EXCEPTION_REVIEW'}},
        relations={'a': ['circle_to_target', 'circle_to_circle']})
    add('E-self-reference', targets(target('a', [-1, -1, 2, 2], exception=exception('equivalent', {'target_id': 'a', 'same_page': True})),
                                    target('obstacle', [10, -12, 24, 24])), 'MODEL_HOLD',
        rows={'a': {'exception': 'MISSING_CONDITION_OR_EVIDENCE'}})
    add('E-three-node-cycle', targets(*[target(tid, [x, -1, 2, 2], action='same',
                                              exception=exception('equivalent', {'target_id': nxt, 'same_page': True}))
                                        for tid, nxt, x in [('a', 'b', -1), ('b', 'c', 8), ('c', 'a', 17)]]),
        'MODEL_HOLD', rows={i: {'status': 'HOLD_EXCEPTION_REVIEW', 'exception': 'MISSING_CONDITION_OR_EVIDENCE'} for i in ['a', 'b', 'c']})
    bad_conditions = [exception('inline', {'in_sentence': 1}), exception('inline', {'in_sentence': 'true'}),
                      exception('ua', {'author_resized': None}), exception('ua', {'ua_determined': []}),
                      exception('ua', {'fake_condition': False}), exception('essential', {'legal_requirement': False}),
                      exception('essential', {'essential_reason': []}), exception('equivalent', {'same_page': 1}),
                      exception('equivalent', {'target_id': []}), exception('equivalent', {'target_id': ''})]
    for idx, claim in enumerate(bad_conditions):
        add('E-malformed-even-size-pass-' + str(idx), targets(target('a', [0, 0, 24, 24], exception=claim)), 'INPUT_ERROR')
    add('E-unneeded-contradiction-not-approved', targets(target('a', [0, 0, 24, 24],
        exception=exception('ua', {'ua_determined': True, 'author_resized': True}))), 'MODEL_PASS',
        rows={'a': {'exception': 'NOT_NEEDED_BY_MODEL'}},
        note='Current local contract permits an unnecessary typed claim; NOT_NEEDED is not exception approval. Semantic diagnostics would help.')

    # Reflow: task retention and local exceptions, independent of page overflow.
    add('R-report-editor-at-boundary', reflow(), 'MODEL_PASS')
    d = reflow(); d['page_overflow'] = True
    add('R-overflow-with-all-reflow-records', d, 'MODEL_PASS', note='Supplied region evidence, not overflow alone, drives this narrow model.')
    d = reflow(); d['regions'][0]['reflows'] = False
    add('R-no-overflow-but-prose-fails', d, 'MODEL_FAIL', rows={'prose': {'status': 'FAIL_NONEXCEPTED_REFLOW'}})
    d = reflow(); d['items'][1]['availability'] = 'missing'
    add('R-no-overflow-but-action-lost', d, 'MODEL_FAIL', rows={'export-report': {'status': 'FAIL_REQUIRED_ITEM_LOST'}})
    for ref in ['', '   ']:
        d = reflow(); d['items'][1].update(availability='missing', evidence_ref=ref)
        add('R-known-loss-empty-ref-' + str(len(ref)), d, 'MODEL_FAIL',
            rows={'export-report': {'status': 'FAIL_REQUIRED_ITEM_LOST'}},
            source='evaluation-plan.md §1; layout-contracts.md MODEL_FAIL precedence',
            note='Explicit missing is a supplied negative observation; a missing reference should be recorded separately, not erase the negative fact.')
    d = reflow(); d['items'][1].update(availability='unknown', evidence_ref='')
    add('R-unknown-action', d, 'MODEL_HOLD')
    d = reflow(); d['items'][1].update(availability='alternative')
    add('R-alternative-route-missing', d, 'MODEL_HOLD', rows={'export-report': {'status': 'HOLD_ALTERNATIVE_ROUTE'}})
    d = reflow(); d['items'][1].update(availability='alternative', alternative_route='Open File, then Export; preserve report filters and title')
    add('R-alternative-route-recorded', d, 'MODEL_PASS')
    d = reflow(); d['items'][1].update(availability='alternative', alternative_route='   ')
    add('R-alternative-route-empty', d, 'MODEL_HOLD')
    table = {'id': 'comparison-table', 'reflows': False, 'exception': {'kind': 'two_dimensional',
             'reason': 'Synthetic row and column comparison requires both axes', 'evidence_ref': 'Synthetic reason requiring review'}}
    d = reflow(); d['regions'].append(copy.deepcopy(table)); d['page_overflow'] = True
    add('R-local-exception-page-overflow', d, 'MODEL_HOLD', rows={'comparison-table': {'status': 'HOLD_EXCEPTION_REVIEW'}})
    d = reflow(); d['regions'].append(copy.deepcopy(table)); d['regions'][0]['reflows'] = False
    add('R-table-exception-does-not-leak', d, 'MODEL_FAIL', rows={'prose': {'status': 'FAIL_NONEXCEPTED_REFLOW'},
                                                              'comparison-table': {'status': 'HOLD_EXCEPTION_REVIEW'}})
    d = reflow(); d['regions'][0].update(reflows=False, exception={'kind': 'two_dimensional', 'reason': '', 'evidence_ref': ''})
    add('R-empty-page-wide-exemption', d, 'MODEL_HOLD', rows={'prose': {'status': 'HOLD_EXCEPTION_EVIDENCE'}})
    d = reflow(); d['regions'][0].update(reflows=False, exception={'kind': 'two_dimensional', 'reason': 'Everything is a table', 'evidence_ref': 'Claim only'})
    add('R-unsupported-page-wide-claim', d, 'MODEL_HOLD', rows={'prose': {'status': 'HOLD_EXCEPTION_REVIEW'}})
    d = reflow(); d['regions'][0]['reflows'] = None
    add('R-unobserved-region', d, 'MODEL_HOLD')
    d = reflow(); d['items'].pop()
    add('R-required-id-has-no-row', d, 'MODEL_HOLD')
    for width in [319, 321, Decimal('319.999999999999999999')]:
        d = reflow(); d['context']['css_width'] = width
        add('R-boundary-width-' + str(width), d, 'MODEL_HOLD')
    for height, expected in [(256, 'MODEL_PASS'), (255, 'MODEL_HOLD'), (257, 'MODEL_HOLD')]:
        d = reflow(); d['context'].update(scroll_direction='horizontal', css_width=1000, css_height=height)
        add('R-horizontal-boundary-' + str(height), d, expected)
    d = reflow(); d['items'][1]['availability'] = 'missing'; d['inventory_complete'] = False; d['context']['css_width'] = 640
    add('R-known-fail-beats-incomplete-and-wrong-boundary', d, 'MODEL_FAIL')
    d = reflow(); d['items'][0]['region_id'] = 'absent'
    add('R-undefined-region', d, 'INPUT_ERROR', issues='REGION_MISSING')

    # Evidence claims never manufacture browser, AT, or conformance execution.
    for kind in ['declaration', 'synthetic_geometry', 'supplied_measurement_unverified', 'browser_observed', 'assistive_technology_observed']:
        for model in ['targets', 'reflow']:
            d = targets(target('a', [0, 0, 24, 24])) if model == 'targets' else reflow()
            d['evidence']['kind'] = kind
            add('P-no-runtime-upgrade-' + model + '-' + kind, d, 'MODEL_PASS')

    # Format, numeric range, malformed data even on otherwise passing inputs.
    for val, label in [(True, 'boolean'), ('24', 'numeric-string'), (None, 'null'), (0, 'zero'), (-1, 'negative'),
                       (Decimal('1e-19'), 'precision-over-limit'), (Decimal('1e10'), 'magnitude-over-limit')]:
        add('I-invalid-width-' + label, targets(target('a', [0, 0, val, 24])), 'INPUT_ERROR')
    d = targets(target('a', [0, 0, 24, 24])); d['targets'][0]['context_id'] = 'different-state'
    add('I-mixed-context', d, 'INPUT_ERROR', issues='MIXED_CONTEXT')
    d = targets(target('a', [0, 0, 24, 24])); d['targets'][0]['coordinate_space'] = 'screen-px'
    add('I-mixed-coordinate-space', d, 'INPUT_ERROR', issues='MIXED_CONTEXT')
    add('I-duplicate-target-id', targets(target('same', [0, 0, 24, 24]), target('same', [50, 0, 24, 24])),
        'INPUT_ERROR', issues='DUPLICATE_ID')
    d = reflow(); d['required_ids'].append('export-report')
    add('I-duplicate-required-id', d, 'INPUT_ERROR', issues='DUPLICATE_ID')
    d = targets(target('a', [0, 0, 24, 24])); d['evidence']['kind'] = []
    add('I-evidence-unhashable-type', d, 'INPUT_ERROR', issues='EVIDENCE_KIND')
    d = targets(target('a', [0, 0, 24, 24])); d['evidence']['ref'] = ''
    add('I-empty-source-reference', d, 'INPUT_ERROR', issues='TEXT_REQUIRED')
    d = targets(target('a', [0, 0, 24, 24])); d['unexpected'] = True
    add('I-unknown-field', d, 'INPUT_ERROR', issues='UNSUPPORTED_FIELDS')
    add('I-over-row-limit', targets(*[target('t' + str(i), [i*25, 0, 24, 24]) for i in range(501)]),
        'INPUT_ERROR', issues='ROW_LIMIT')
    add('I-file-at-limit', targets(target('a', [0, 0, 24, 24])), 'MODEL_PASS', pad_to=2*1024*1024)
    add('I-file-over-limit', targets(target('a', [0, 0, 24, 24])), 'INPUT_ERROR', pad_to=2*1024*1024+1, issues='FILE_LIMIT')
    add('I-duplicate-json-key', None, 'INPUT_ERROR', raw=b'{"kind":"targets","kind":"reflow"}', issues='DUPLICATE_KEY')
    add('I-non-json-nan', None, 'INPUT_ERROR', raw=b'{"coordinate":NaN}', issues='NONFINITE_NUMBER')
    add('I-invalid-utf8', None, 'INPUT_ERROR', raw=b'\xff')
    add('I-deep-json', None, 'INPUT_ERROR', raw=('['*1200+'0'+']'*1200).encode('ascii'))
    for textval, name in [('1e99999999999999999999999999999999', 'huge-positive-exponent'),
                          ('1e-99999999999999999999999999999999', 'huge-negative-exponent'),
                          ('0e99999999999999999999999999999999', 'zero-huge-exponent')]:
        raw = wire(targets(target('a', [0, 0, 24, 24]))).replace('"rect":[0,0,24,24]', '"rect":[0,0,'+textval+',24]').encode('ascii')
        add('I-' + name, None, 'INPUT_ERROR', raw=raw, origin='parent_discovery_independently_reproduced',
            note='Parent communicated the decimal.InvalidOperation family before this execution; excluded from independent-discovery count.')
    for surrogate, name in [('\ud800', 'high'), ('\udcff', 'low')]:
        d = targets(target('a', [0, 0, 24, 24])); d['context']['id'] = surrogate
        add('I-lone-surrogate-' + name, d, None, allowed_status=['MODEL_PASS', 'INPUT_ERROR'],
            source='evaluation-plan.md §3; layout-contracts.md CLI output/exit-code contract',
            note='Either reject unsupported Unicode with structured INPUT_ERROR or serialize it safely; a crash or non-UTF-8 output is not acceptable.')


def evaluate(case):
    payload = case['payload']
    if case['pad_to']:
        payload = b' ' * (case['pad_to'] - len(payload)) + payload
    with tempfile.NamedTemporaryFile(prefix='critic-input-', suffix='.json', dir=ROUND) as temp:
        temp.write(payload); temp.flush()
        completed = subprocess.run([sys.executable, '-B', str(CANDIDATE), temp.name],
                                   cwd=ROOT, capture_output=True, timeout=30)
    stdout = completed.stdout.decode('utf-8', errors='replace')
    stderr = completed.stderr.decode('utf-8', errors='replace')
    errors = []
    try:
        completed.stdout.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        errors.append('CLI output is not valid UTF-8')
    try:
        actual = json.loads(stdout)
    except (ValueError, TypeError):
        actual = None
        errors.append('CLI did not return a JSON result')
    if 'Traceback' in stderr:
        errors.append('Unhandled traceback')
    e = case['expect']
    if actual is not None:
        status = actual.get('status')
        if e['status'] is not None and status != e['status']:
            errors.append(f"status expected {e['status']}, got {status}")
        if e['allowed_status'] is not None and status not in e['allowed_status']:
            errors.append(f"status outside allowed alternatives {e['allowed_status']}: {status}")
        if completed.returncode != EXIT_CODES.get(status):
            errors.append(f'exit/status mismatch: {completed.returncode}/{status}')
        if actual.get('ui_status') != 'HOLD' or actual.get('wcag_conformance') != 'NOT_ASSESSED':
            errors.append('Input model incorrectly upgraded UI/conformance')
        if status != 'INPUT_ERROR':
            for name in ['browser_executed', 'at_executed', 'evidence_authenticated']:
                if actual.get(name) is not False:
                    errors.append(f'{name} must remain false')
        indexed = {r['id']: r for r in actual.get('results', [])}
        for tid, fields in e['rows'].items():
            for key, expected in fields.items():
                got = indexed.get(tid, {}).get(key)
                if got != expected:
                    errors.append(f'{tid}.{key}: expected {expected!r}, got {got!r}')
        for tid, expected in e['relations'].items():
            got = sorted({r['relation'] for r in indexed.get(tid, {}).get('collisions', [])})
            if got != sorted(expected):
                errors.append(f'{tid}.collision relations: expected {expected}, got {got}')
        if e['issue_code'] and e['issue_code'] not in [r.get('code') for r in actual.get('issues', [])]:
            errors.append('Expected issue code absent: ' + e['issue_code'])
    record = {k: case[k] for k in ['id', 'expect', 'source', 'note', 'origin']}
    try:
        record['input_json'] = case['payload'].decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        record['input_hex'] = case['payload'].hex()
    if case['pad_to']:
        record['input_recipe'] = {'prefix_ascii_spaces_to_total_bytes': case['pad_to']}
    record.update(input_sha256=hashlib.sha256(payload).hexdigest(), input_bytes=len(payload),
                  actual=actual, stdout=stdout, stderr=stderr, returncode=completed.returncode,
                  passed=not errors, discrepancies=errors,
                  reproduction_command=f'python3 campaigns/C/rounds/03/independent-probes.py --case {case["id"]} --stdout')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', dest='cases')
    parser.add_argument('--output', default='initial-results.json')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('--allow-revised', action='store_true')
    args = parser.parse_args()
    build_cases()
    selected = [c for c in CASES if not args.cases or c['id'] in args.cases]
    if args.cases and set(args.cases) - {c['id'] for c in CASES}:
        parser.error('Unknown case id')
    snapshot = json.loads(SNAPSHOT.read_text())
    paths = list(snapshot['sha256']) + [
        'modules/ui-engineering-design-system/examples/booking-reflow-model.json',
        'modules/ui-engineering-design-system/examples/toolbar-target-model.json',
        'registry/C/skills/C-UI-008.json', 'registry/C/skills/C-UI-009.json']
    before = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    matches = all(before[p] == expected for p, expected in snapshot['sha256'].items())
    if not matches and not args.allow_revised:
        parser.error('Candidate differs from frozen snapshot; use --allow-revised only for a separately recorded correction recheck')
    output = ROUND / args.output
    if not args.stdout and (output.parent != ROUND or output.exists()):
        parser.error('Output must be a new file in this round directory; initial results are immutable')
    records = [evaluate(case) for case in selected]
    after = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    out = {'critic': 'SESSION C round03 independent critic task; same underlying model family, separate task',
           'executed_at': datetime.now(timezone.utc).isoformat(),
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'candidate_snapshot_sha256': hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
           'candidate_matches_frozen': matches, 'files_unchanged_during_probes': before == after,
           'candidate_sha256_before': before, 'candidate_sha256_after': after,
           'browser_executed': False, 'at_executed': False, 'dom_double_executed': False,
           'existing_candidate_tests_executed': False,
           'summary': {'executed': len(records), 'passed': sum(r['passed'] for r in records),
                       'failed': sum(not r['passed'] for r in records),
                       'independently_authored_cases': sum(r['origin'] == 'independent_critic' for r in records),
                       'parent_discovery_reproductions': sum(r['origin'] != 'independent_critic' for r in records)},
           'results': records}
    rendered = json.dumps(out, ensure_ascii=True, indent=2) + '\n'
    if args.stdout:
        print(rendered, end='')
    else:
        with output.open('x', encoding='utf-8') as f:
            f.write(rendered)
        print(json.dumps({'output': str(output), 'summary': out['summary'],
                          'failed_cases': [r['id'] for r in records if not r['passed']]}, ensure_ascii=False))
    return 1 if out['summary']['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
