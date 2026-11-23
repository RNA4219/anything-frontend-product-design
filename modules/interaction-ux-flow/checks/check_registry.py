#!/usr/bin/env python3
"""Check B's registry integrity and evidence references; not a usability judge."""
import argparse
import json
import re
from pathlib import Path

REQUIRED = ('skill_id domain trigger intent required_inputs decision_rules procedure '
            'expected_outputs dependencies exceptions failure_modes verification '
            'source_refs confidence status version').split()
STATUSES = {'DRAFT', 'ACCEPT', 'REVISE', 'HOLD', 'REJECT'}

def validate(root):
    root = Path(root).resolve()
    errors, ids, sources, counts = [], set(), {}, {}
    for path in sorted((root / 'registry/B/sources').glob('*.json')):
        try:
            source = json.loads(path.read_text())
            sid = source['source_id']
            if sid in sources:
                errors.append(f'{path}: duplicate source ID {sid}')
            sources[sid] = source
            if not source.get('url', '').startswith('https://'):
                errors.append(f'{path}: missing source URL')
            if not source.get('section') or not source.get('read_status'):
                errors.append(f'{path}: missing source locator or read status')
        except (ValueError, KeyError) as exc:
            errors.append(f'{path}: invalid source: {exc}')
    paths = sorted((root / 'registry/B/skills').glob('*.json'))
    if not paths:
        errors.append('registry/B/skills: no Instruction Units')
    for path in paths:
        try:
            unit = json.loads(path.read_text())
            absent = [key for key in REQUIRED if key not in unit]
            if absent:
                errors.append(f'{path}: missing fields {absent}')
                continue
            uid = unit['skill_id']
            if uid in ids or not re.fullmatch(r'B-IU-\d{3}', uid):
                errors.append(f'{path}: duplicate or invalid skill ID {uid}')
            ids.add(uid)
            status = unit['status']
            if status not in STATUSES:
                errors.append(f'{uid}: invalid status {status}')
            counts[status] = counts.get(status, 0) + 1
            if unit['domain'] != 'interaction-ux-flow':
                errors.append(f'{uid}: outside session B domain')
            if not re.fullmatch(r'\d+\.\d+\.\d+', unit['version']):
                errors.append(f'{uid}: invalid version')
            for field in ('trigger','required_inputs','decision_rules','procedure','expected_outputs','failure_modes','source_refs'):
                if not isinstance(unit[field], list) or not unit[field]:
                    errors.append(f'{uid}: {field} must be nonempty array')
            refs = unit['source_refs']
            for sid in refs:
                if sid not in sources:
                    errors.append(f'{uid}: unknown source {sid}')
            for rule in unit['decision_rules']:
                if not isinstance(rule, dict) or not all(rule.get(k) for k in ('if','then','basis','source_refs')):
                    errors.append(f'{uid}: rule lacks condition/action/basis/provenance')
                    continue
                if rule['basis'] not in ('source_requirement','source_guidance','campaign_inference'):
                    errors.append(f'{uid}: rule does not distinguish fact and inference')
                if any(sid not in refs for sid in rule['source_refs']):
                    errors.append(f'{uid}: rule cites source outside unit provenance')
            ver = unit['verification']
            if not all(k in ver for k in ('criteria','evidence','limitations')):
                errors.append(f'{uid}: incomplete verification contract')
            if status == 'ACCEPT' and not ver.get('evidence'):
                errors.append(f'{uid}: ACCEPT without evidence')
            for item in ver.get('evidence', []):
                rel = item if isinstance(item, str) else item['path']
                target = (root / rel).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    errors.append(f'{uid}: missing or external evidence {rel}')
            if not all(k in unit['confidence'] for k in ('source_support','transfer','limits')):
                errors.append(f'{uid}: confidence lacks limits')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'{path}: malformed unit: {exc}')
    return {'units': len(paths), 'sources': len(sources), 'statuses': counts, 'errors': errors,
            'limits': 'Checks registry structure and referenced files, not whether prose or empirical claims are true.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
