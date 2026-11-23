"""Check Session C registry structure and evidence links; no quality certification."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    'skill_id', 'domain', 'trigger', 'intent', 'required_inputs',
    'decision_rules', 'procedure', 'expected_outputs', 'dependencies',
    'exceptions', 'failure_modes', 'verification', 'source_refs',
    'confidence', 'status', 'version',
}
STATES = {'DRAFT', 'ACCEPT', 'REVISE', 'HOLD', 'REJECT'}


def canonical(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), p.query, ''))


def check(root=ROOT):
    errors, units, sources, seen = [], [], {}, set()
    for file in sorted((root / 'registry/C/sources').glob('*.json')):
        try:
            item = json.loads(file.read_text())
            key = canonical(item['url'])
            if key in sources:
                errors.append(f'{file}: duplicate canonical source {key}')
            sources[key] = item['source_id']
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'{file}: malformed source: {exc}')
    for file in sorted((root / 'registry/C/skills').glob('*.json')):
        try:
            item = json.loads(file.read_text())
            units.append(item)
            missing = REQUIRED - item.keys()
            if missing:
                errors.append(f'{file}: missing {sorted(missing)}')
                continue
            sid = item['skill_id']
            if sid != file.stem or not re.fullmatch(r'C-UI-\d{3}', sid) or sid in seen:
                errors.append(f'{file}: invalid or repeated identity')
            seen.add(sid)
            if item['status'] not in STATES:
                errors.append(f'{sid}: unknown status')
            if not re.fullmatch(r'\d+\.\d+\.\d+', item['version']):
                errors.append(f'{sid}: invalid version')
            for field in ('trigger', 'intent', 'domain'):
                if not isinstance(item[field], str) or not item[field].strip():
                    errors.append(f'{sid}: empty {field}')
            for field in ('required_inputs', 'decision_rules', 'procedure', 'expected_outputs',
                          'dependencies', 'exceptions', 'failure_modes', 'source_refs'):
                if not isinstance(item[field], list):
                    errors.append(f'{sid}: {field} must be a list')
            for ref in item['source_refs']:
                if canonical(ref['url']) not in sources:
                    errors.append(f'{sid}: source not registered: {ref["url"]}')
                source_file, pointer = ref['record'].split('#', 1)
                path = (root / source_file).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    errors.append(f'{sid}: missing research record: {source_file}')
                    continue
                selected = json.loads(path.read_text())
                for part in pointer.strip('/').split('/'):
                    part = part.replace('~1', '/').replace('~0', '~')
                    selected = selected[int(part)] if isinstance(selected, list) else selected[part]
                if selected.get('id') != ref['id']:
                    errors.append(f'{sid}: source id and record pointer disagree: {ref["id"]}')
                if canonical(selected.get('canonical_url', selected.get('url', ''))) != canonical(ref['url']):
                    errors.append(f'{sid}: source URL and research record disagree: {ref["id"]}')
            verification = item['verification']
            for evidence in verification.get('evidence', []):
                path = (root / evidence).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    errors.append(f'{sid}: missing/outside evidence: {evidence}')
            if item['status'] == 'ACCEPT':
                if not verification.get('evidence') or not verification.get('accepted_scope'):
                    errors.append(f'{sid}: ACCEPT needs evidence and a bounded accepted_scope')
                if verification.get('status') != 'PASS_SUPPORTED_SCOPE':
                    errors.append(f'{sid}: ACCEPT without matching verified scope')
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(f'{file}: malformed instruction unit: {exc}')
    if not units:
        errors.append('No instruction units')
    return {'status': 'FAIL' if errors else 'PASS_REGISTRY_STRUCTURE',
            'instruction_units': len(units), 'canonical_sources': len(sources),
            'states': {s: sum(u.get('status') == s for u in units) for s in sorted(STATES)},
            'errors': errors,
            'limit': 'Only structure, local evidence existence, and source indexing; not evidence quality or behavior.'}


if __name__ == '__main__':
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(bool(result['errors']))
