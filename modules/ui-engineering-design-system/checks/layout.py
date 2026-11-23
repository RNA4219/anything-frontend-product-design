"""Precheck supplied reflow observations and an exact rectangular target model.

This program does not observe a browser, authenticate evidence, or certify WCAG.
All geometric arithmetic uses exact rational values from bounded decimal inputs.
"""
import argparse
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from pathlib import Path
import sys

SCHEMA = 'C-layout-model/1'
EVIDENCE = {'declaration', 'synthetic_geometry', 'supplied_measurement_unverified',
            'browser_observed', 'assistive_technology_observed'}
MAX_ROWS = 500


class InputProblem(ValueError):
    def __init__(self, path, code, message):
        self.issue = {'path': path, 'code': code, 'message': message}
        super().__init__(message)


def problem(path, code, message):
    raise InputProblem(path, code, message)


def fields(obj, required, allowed, path):
    if not isinstance(obj, dict) or any(not isinstance(k, str) for k in obj):
        problem(path, 'OBJECT_REQUIRED', 'Expected a JSON object with string keys')
    if required - obj.keys():
        problem(path, 'MISSING_FIELDS', ', '.join(sorted(required - obj.keys())))
    if obj.keys() - allowed:
        problem(path, 'UNSUPPORTED_FIELDS', ', '.join(sorted(obj.keys() - allowed)))


def text(value, path):
    if not isinstance(value, str) or not value.strip():
        problem(path, 'TEXT_REQUIRED', 'Expected nonempty text')
    return value


def boolean(value, path):
    if type(value) is not bool:
        problem(path, 'BOOLEAN_REQUIRED', 'Expected true or false')
    return value


def number(value, path, positive=False, nonnegative=False):
    if type(value) not in (int, float, Decimal):
        problem(path, 'NUMBER_REQUIRED', 'Expected a numeric value, excluding boolean/string')
    if type(value) is int and value.bit_length() > 64:
        problem(path, 'NUMBER_LIMIT', 'Local coordinate limit: absolute value <= 1e9 CSS px')
    decimal = Decimal(str(value))
    if not decimal.is_finite():
        problem(path, 'NONFINITE_NUMBER', 'Expected a finite numeric value')
    if decimal.copy_abs() > Decimal('1e9') or decimal.as_tuple().exponent < -18:
        problem(path, 'NUMBER_LIMIT', 'Local limit: magnitude <= 1e9 and at most 18 decimal places')
    result = Fraction(decimal) if decimal else Fraction(0)
    if (positive and result <= 0) or (nonnegative and result < 0):
        problem(path, 'NUMBER_RANGE', 'Expected a positive dimension or nonnegative uncertainty')
    return result


def rows(value, path, allow_empty=False):
    if not isinstance(value, list) or len(value) > MAX_ROWS or (not value and not allow_empty):
        problem(path, 'ROW_LIMIT', f'Expected a list of {0 if allow_empty else 1}..{MAX_ROWS} entries')
    return value


def header(doc, specific):
    common = {'schema', 'kind', 'context', 'evidence'}
    fields(doc, common | specific, common | specific, '<root>')
    if doc['schema'] != SCHEMA:
        problem('schema', 'SCHEMA_UNSUPPORTED', SCHEMA)
    context = doc['context']
    fields(context, {'id', 'coordinate_space', 'css_width', 'css_height', 'scroll_direction'},
           {'id', 'coordinate_space', 'css_width', 'css_height', 'scroll_direction'}, 'context')
    text(context['id'], 'context.id')
    if context['coordinate_space'] != 'viewport-css-px':
        problem('context.coordinate_space', 'COORDINATE_SPACE', 'Use one viewport/state in CSS px')
    number(context['css_width'], 'context.css_width', positive=True)
    number(context['css_height'], 'context.css_height', positive=True)
    if context['scroll_direction'] not in ('vertical', 'horizontal'):
        problem('context.scroll_direction', 'SCROLL_DIRECTION', 'Use vertical or horizontal reading scroll direction')
    evidence = doc['evidence']
    fields(evidence, {'kind', 'ref'}, {'kind', 'ref'}, 'evidence')
    if not isinstance(evidence['kind'], str) or evidence['kind'] not in EVIDENCE:
        problem('evidence.kind', 'EVIDENCE_KIND', 'Unknown evidence category')
    text(evidence['ref'], 'evidence.ref')


def report(doc, results, holds=None):
    holds = holds or []
    statuses = [r['status'] for r in results]
    status = ('MODEL_FAIL' if any(s.startswith('FAIL') for s in statuses) else
              'MODEL_HOLD' if holds or any(s.startswith('HOLD') for s in statuses) else 'MODEL_PASS')
    return {'status': status, 'kind': doc['kind'], 'context_id': doc['context']['id'],
            'scope': 'Supplied input model only; evidence contents and completeness are not authenticated',
            'evidence_claim': doc['evidence']['kind'], 'evidence_authenticated': False,
            'ui_status': 'HOLD', 'browser_executed': False, 'at_executed': False,
            'wcag_conformance': 'NOT_ASSESSED', 'holds': holds, 'results': results}


def reflow(doc):
    header(doc, {'inventory_complete', 'required_ids', 'items', 'regions', 'page_overflow'})
    complete = boolean(doc['inventory_complete'], 'inventory_complete')
    boolean(doc['page_overflow'], 'page_overflow')
    holds = [] if complete else ['INVENTORY_INCOMPLETE']
    axis = 'css_width' if doc['context']['scroll_direction'] == 'vertical' else 'css_height'
    boundary = 320 if axis == 'css_width' else 256
    if number(doc['context'][axis], f'context.{axis}') != boundary:
        holds.append(f'BOUNDARY_NOT_OBSERVED:{axis}={boundary}')
    required = rows(doc['required_ids'], 'required_ids')
    for value in required:
        text(value, 'required_ids')
    if len(set(required)) != len(required):
        problem('required_ids', 'DUPLICATE_ID', 'Required IDs must be unique')
    results, regions, items = [], {}, {}
    for region in rows(doc['regions'], 'regions'):
        fields(region, {'id', 'reflows', 'exception'}, {'id', 'reflows', 'exception'}, 'regions[]')
        rid = text(region['id'], 'regions[].id')
        if rid in regions:
            problem(rid, 'DUPLICATE_ID', 'Region IDs must be unique')
        if region['reflows'] is not None:
            boolean(region['reflows'], rid + '.reflows')
        exception = region['exception']
        if exception is not None:
            fields(exception, {'kind', 'reason', 'evidence_ref'}, {'kind', 'reason', 'evidence_ref'}, rid + '.exception')
            if exception['kind'] != 'two_dimensional':
                problem(rid, 'EXCEPTION_KIND', 'Only a region-specific two-dimensional claim is represented')
            if not isinstance(exception['reason'], str) or not isinstance(exception['evidence_ref'], str):
                problem(rid, 'EXCEPTION_SHAPE', 'Reason and evidence reference must be strings')
        if region['reflows'] is True:
            status = 'PASS_REFLOW_RECORDED'
        elif exception:
            status = ('HOLD_EXCEPTION_REVIEW' if exception['reason'].strip() and exception['evidence_ref'].strip()
                      else 'HOLD_EXCEPTION_EVIDENCE')
        elif region['reflows'] is False:
            status = 'FAIL_NONEXCEPTED_REFLOW'
        else:
            status = 'HOLD_REFLOW_UNOBSERVED'
        regions[rid] = region
        results.append({'id': rid, 'subject': 'region', 'status': status,
                        'exception_scope': rid if exception else None})
    for item in rows(doc['items'], 'items', allow_empty=True):
        fields(item, {'id', 'region_id', 'availability', 'evidence_ref'},
               {'id', 'region_id', 'availability', 'evidence_ref', 'alternative_route'}, 'items[]')
        iid = text(item['id'], 'items[].id')
        if iid in items:
            problem(iid, 'DUPLICATE_ID', 'Item IDs must be unique')
        text(item['region_id'], iid + '.region_id')
        if item['region_id'] not in regions:
            problem(iid, 'REGION_MISSING', 'Item must refer to a declared region')
        if item['availability'] not in ('present', 'alternative', 'missing', 'unknown'):
            problem(iid, 'AVAILABILITY', 'Use present, alternative, missing or unknown')
        if not isinstance(item['evidence_ref'], str):
            problem(iid, 'EVIDENCE_REF', 'Evidence reference must be a string')
        if 'alternative_route' in item and not isinstance(item['alternative_route'], str):
            problem(iid, 'ALTERNATIVE_ROUTE', 'Describe the actual alternative route as text')
        items[iid] = item
    for iid in required:
        item = items.get(iid)
        if item is None or item['availability'] == 'unknown':
            status = 'HOLD_ITEM_UNOBSERVED'
        elif item['availability'] == 'missing':
            status = 'FAIL_REQUIRED_ITEM_LOST'
        elif not item['evidence_ref'].strip():
            status = 'HOLD_ITEM_UNOBSERVED'
        elif item['availability'] == 'alternative' and not item.get('alternative_route', '').strip():
            status = 'HOLD_ALTERNATIVE_ROUTE'
        else:
            status = 'PASS_RETENTION_RECORDED'
        results.append({'id': iid, 'subject': 'required_item', 'status': status,
                        'evidence_ref_present': bool(item and item['evidence_ref'].strip())})
    result = report(doc, results, holds)
    result['page_overflow_recorded'] = doc['page_overflow']
    result['page_overflow_is_not_a_verdict'] = True
    result['order_focus_resize_text'] = 'NOT_ASSESSED'
    return result


def rectangle(value, path):
    if not isinstance(value, list) or len(value) != 4:
        problem(path, 'RECTANGLE', 'Expected [x,y,width,height]')
    return tuple(number(v, f'{path}[{i}]', positive=i >= 2) for i, v in enumerate(value))


def overlap(a, b):
    return min(a[0]+a[2], b[0]+b[2]) > max(a[0], b[0]) and min(a[1]+a[3], b[1]+b[3]) > max(a[1], b[1])


def circle_rectangle_distance_squared(center, rect):
    cx, cy = center
    x, y, width, height = rect
    dx, dy = max(x-cx, 0, cx-x-width), max(y-cy, 0, cy-y-height)
    return dx*dx + dy*dy


def exception_conditions(exception, tid):
    kind, conditions = exception['kind'], exception['conditions']
    allowed = {'inline': {'in_sentence', 'constrained_by_non_target_line_height'},
               'ua': {'ua_determined', 'author_resized'},
               'essential': {'essential_reason', 'legal_requirement'},
               'equivalent': {'target_id', 'same_page'}}[kind]
    fields(conditions, set(), allowed, tid + '.exception.conditions')
    for key, value in conditions.items():
        if kind in ('inline', 'ua') or key == 'same_page':
            boolean(value, tid + '.exception.' + key)
        elif key == 'target_id':
            text(value, tid + '.exception.target_id')
        elif not isinstance(value, str):
            problem(tid, 'ESSENTIAL_REASON', 'Describe essential presentation or legal requirement')
    return allowed


def targets(doc):
    header(doc, {'targets_complete', 'targets'})
    complete = boolean(doc['targets_complete'], 'targets_complete')
    parsed, ids = [], set()
    for target in rows(doc['targets'], 'targets'):
        fields(target, {'id', 'action_id', 'geometry', 'exception'},
               {'id', 'action_id', 'geometry', 'exception', 'context_id', 'coordinate_space'}, 'targets[]')
        tid = text(target['id'], 'target.id')
        text(target['action_id'], tid + '.action_id')
        if tid in ids:
            problem(tid, 'DUPLICATE_ID', 'Target IDs must be unique')
        ids.add(tid)
        if target.get('context_id', doc['context']['id']) != doc['context']['id'] or target.get('coordinate_space', 'viewport-css-px') != 'viewport-css-px':
            problem(tid, 'MIXED_CONTEXT', 'Targets must share the same state and coordinate space')
        g = target['geometry']
        fields(g, {'kind', 'rect', 'limitations', 'uncertainty'}, {'kind', 'rect', 'limitations', 'uncertainty'}, tid + '.geometry')
        text(g['kind'], tid + '.geometry.kind')
        if not isinstance(g['limitations'], list) or any(not isinstance(x, str) or not x.strip() for x in g['limitations']):
            problem(tid, 'LIMITATIONS', 'limitations must be a list of nonempty strings')
        rect = rectangle(g['rect'], tid + '.geometry.rect')
        uncertainty = number(g['uncertainty'], tid + '.geometry.uncertainty', nonnegative=True)
        usable = g['kind'] == 'effective_rect' and not g['limitations'] and uncertainty == 0
        exception = target['exception']
        if exception is not None:
            fields(exception, {'kind', 'evidence_ref', 'conditions'}, {'kind', 'evidence_ref', 'conditions'}, tid + '.exception')
            if exception['kind'] not in ('inline', 'equivalent', 'ua', 'essential'):
                problem(tid, 'EXCEPTION_KIND', 'Unknown non-spacing exception')
            if not isinstance(exception['evidence_ref'], str) or not isinstance(exception['conditions'], dict):
                problem(tid, 'EXCEPTION_SHAPE', 'Expected evidence text and condition object')
            exception_conditions(exception, tid)
        parsed.append({'id': tid, 'action_id': target['action_id'], 'rect': rect,
                       'usable': usable, 'exception': exception, 'overlap': []})
    for i, a in enumerate(parsed):
        for b in parsed[i+1:]:
            if a['usable'] and b['usable'] and overlap(a['rect'], b['rect']):
                a['overlap'].append(b['id']); b['overlap'].append(a['id'])
    for target in parsed:
        if target['overlap']:
            target['usable'] = False
        x, y, width, height = target['rect']
        target['center'] = (x + width/2, y + height/2)
        target['size'] = 'PASS' if target['usable'] and width >= 24 and height >= 24 else ('UNDERSIZED' if target['usable'] else 'HOLD')
    result_rows = []
    for target in parsed:
        collisions, unknown = [], []
        if target['size'] == 'UNDERSIZED':
            for other in parsed:
                if target is other:
                    continue
                if not other['usable']:
                    unknown.append(other['id']); continue
                distance = circle_rectangle_distance_squared(target['center'], other['rect'])
                if distance < 144:
                    collisions.append({'other': other['id'], 'relation': 'circle_to_target', 'distance_squared': str(distance)})
                if other['size'] == 'UNDERSIZED':
                    distance = sum((a-b)**2 for a, b in zip(target['center'], other['center']))
                    if distance < 576:
                        collisions.append({'other': other['id'], 'relation': 'circle_to_circle', 'distance_squared': str(distance)})
        if target['size'] == 'PASS':
            status, spacing = 'PASS_MODEL_SIZE', 'NOT_REQUIRED'
        elif target['size'] == 'HOLD':
            status, spacing = 'HOLD_GEOMETRY', 'HOLD'
        elif collisions:
            status, spacing = 'FAIL_MODEL_SPACING', 'FAIL'
        elif unknown or not complete:
            status, spacing = 'HOLD_NEIGHBORS', 'HOLD'
        else:
            status, spacing = 'PASS_MODEL_SPACING', 'PASS'
        result_rows.append({'id': target['id'], 'status': status, 'size': target['size'],
                            'spacing': spacing, 'collisions': collisions,
                            'unknown_neighbors': unknown, 'overlap_requires_review': target['overlap'],
                            'exception': 'UNCLAIMED' if not target['exception'] else 'NOT_NEEDED_BY_MODEL'})
    by_id = {t['id']: t for t in parsed}
    preliminary = {r['id']: r['status'] for r in result_rows}
    for target, row in zip(parsed, result_rows):
        exception = target['exception']
        if not exception or row['status'].startswith('PASS'):
            continue
        kind, conditions = exception['kind'], exception['conditions']
        allowed = exception_conditions(exception, target['id'])
        valid = None
        if kind in ('inline', 'ua'):
            if kind == 'inline':
                valid = True if any(conditions.values()) else (False if allowed <= conditions.keys() else None)
            elif conditions.get('ua_determined') is False or conditions.get('author_resized') is True:
                valid = False
            elif allowed <= conditions.keys():
                valid = True
        elif kind == 'essential':
            valid = True if any(v.strip() for v in conditions.values()) else (False if allowed <= conditions.keys() else None)
        else:
            if 'same_page' in conditions:
                boolean(conditions['same_page'], target['id'] + '.exception.same_page')
            if 'target_id' in conditions:
                text(conditions['target_id'], target['id'] + '.exception.target_id')
            other = by_id.get(conditions.get('target_id'))
            if conditions.get('same_page') is False or (other and other['action_id'] != target['action_id']):
                valid = False
            elif other and other is not target and conditions.get('same_page') is True and preliminary[other['id']].startswith('PASS'):
                valid = True
            # Chained/circular/unproven equivalence is deliberately left for review.
        if valid is False:
            row['exception'] = 'CONDITIONS_CONTRADICT_CLAIM'
        else:
            row['exception'] = ('REQUIRES_SUBSTANTIVE_REVIEW' if valid is True and exception['evidence_ref'].strip()
                                else 'MISSING_CONDITION_OR_EVIDENCE')
            row['status'] = 'HOLD_EXCEPTION_REVIEW'
    return report(doc, result_rows, [] if complete else ['TARGET_INVENTORY_INCOMPLETE'])


def inspect(doc):
    try:
        if not isinstance(doc, dict) or doc.get('kind') not in ('targets', 'reflow'):
            problem('<root>', 'MODEL_KIND', 'Use targets or reflow')
        return targets(doc) if doc['kind'] == 'targets' else reflow(doc)
    except InputProblem as exc:
        return {'status': 'INPUT_ERROR', 'issues': [exc.issue], 'ui_status': 'HOLD',
                'wcag_conformance': 'NOT_ASSESSED', 'browser_executed': False}


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            problem(key, 'DUPLICATE_KEY', 'Duplicate JSON members are unsupported')
        obj[key] = value
    return obj


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    args = parser.parse_args(argv)
    try:
        path = Path(args.input)
        if path.stat().st_size > 2 * 1024 * 1024:
            problem('input', 'FILE_LIMIT', 'Input limit: 2 MiB')
        def reject_constant(value):
            problem('input', 'NONFINITE_NUMBER', 'Non-JSON numeric constants are rejected')
        doc = json.loads(path.read_text(encoding='utf-8'), parse_float=Decimal,
                         parse_constant=reject_constant, object_pairs_hook=unique_pairs)
        result = inspect(doc)
    except (ValueError, OSError, RecursionError, InvalidOperation) as exc:
        issue = exc.issue if isinstance(exc, InputProblem) else {'code': type(exc).__name__, 'message': str(exc)}
        result = {'status': 'INPUT_ERROR', 'issues': [issue], 'ui_status': 'HOLD', 'wcag_conformance': 'NOT_ASSESSED'}
    # ASCII JSON escapes also keep unpaired-surrogate input safe under UTF-8 stdout.
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return {'MODEL_PASS': 0, 'MODEL_FAIL': 1, 'INPUT_ERROR': 2, 'MODEL_HOLD': 3}[result['status']]


if __name__ == '__main__':
    sys.exit(main())
