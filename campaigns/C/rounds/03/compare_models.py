"""Reproducible authored controls; not a model-generation or usability experiment."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('layout_tests', ROOT / 'modules/ui-engineering-design-system/tests/test_layout.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def cases():
    rows = [('plain-reflow', t.reflow_doc(), 'MODEL_PASS')]
    doc = t.reflow_doc(); doc['items'][1]['availability'] = 'missing'
    rows.append(('hidden-required-action-with-no-overflow', doc, 'MODEL_FAIL'))
    doc = t.reflow_doc(); doc['page_overflow'] = True
    doc['regions'].append({'id': 'video', 'reflows': False, 'exception':
                          {'kind': 'two_dimensional', 'reason': 'Spatial frame', 'evidence_ref': 'claim pending review'}})
    rows.append(('excepted-content-causes-page-overflow', doc, 'MODEL_HOLD'))
    doc = t.reflow_doc(); doc['regions'][0]['reflows'] = False
    rows.append(('nonexcepted-prose-reflow-failure-no-scrollbar', doc, 'MODEL_FAIL'))
    rows.extend([
        ('size-boundary', t.target_doc(t.target('a', [0, 0, 24, 24])), 'MODEL_PASS'),
        ('undersized-spacing-tangent', t.target_doc(t.target('a', [0, 0, 20, 20]), t.target('b', [24, 0, 20, 20])), 'MODEL_PASS'),
        ('undersized-neighbor-intrusion', t.target_doc(t.target('a', [0, 0, 20, 20]), t.target('b', [23.999, 0, 20, 20])), 'MODEL_FAIL'),
        ('wide-short-neighbor', t.target_doc(t.target('a', [0, 0, 16, 16]), t.target('b', [0, 17, 100, 16])), 'MODEL_FAIL'),
        ('overlapping-targets', t.target_doc(t.target('a', [0, 0, 48, 48]), t.target('b', [10, 10, 48, 48])), 'MODEL_HOLD')])
    a = t.target('a', [0, 0, 24, 24]); a['geometry']['kind'] = 'circle_bbox'
    rows.append(('circle-bbox-is-not-filled-rectangle', t.target_doc(a), 'MODEL_HOLD'))
    return rows


def main():
    records = []
    for name, doc, expected in cases():
        naive_pass = not doc['page_overflow'] if doc['kind'] == 'reflow' else all(
            x['geometry']['rect'][2] >= 24 and x['geometry']['rect'][3] >= 24 for x in doc['targets'])
        baseline = 'MODEL_PASS' if naive_pass else 'MODEL_FAIL'
        candidate = t.layout.inspect(doc)
        records.append({'case': name, 'input': doc, 'expected_model_status': expected,
                        'authored_shallow_control': baseline, 'candidate': candidate['status'],
                        'control_matches': baseline == expected, 'candidate_matches': candidate['status'] == expected})
    output = {'scope': 'Synthetic input-model comparison; no generation or browser experiment',
              'controls': ['not page_overflow', 'every bbox width and height >=24'],
              'case_count': len(records), 'control_mismatches': sum(not r['control_matches'] for r in records),
              'candidate_mismatches': sum(not r['candidate_matches'] for r in records), 'records': records}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return int(output['candidate_mismatches'] != 0)


if __name__ == '__main__':
    raise SystemExit(main())
