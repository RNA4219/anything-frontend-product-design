#!/usr/bin/env python3
"""Independent counterexamples; exit 1 means candidate defects reproduced."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
MODULE = ROOT / 'modules/ui-engineering-design-system'
spec = importlib.util.spec_from_file_location('reviewed_contracts', MODULE / 'checks/contracts.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
good = json.loads((MODULE / 'examples/component-contracts.json').read_text())
rows = []
for policy in [[], {}, True, 0, None, 'incldue']:
    c = copy.deepcopy(good['components'][2])
    c.update(availability='native-disabled', submit_policy=policy)
    findings = checker.check({'components': [c]})
    rows.append({'submit_policy': policy, 'findings': findings,
                 'defect_reproduced': not findings})
controls = []
for separate in [False, True]:
    c = copy.deepcopy(good['components'][2])
    c.update(availability='native-disabled', separate_serialization=separate)
    controls.append({'separate_serialization': separate, 'findings': checker.check({'components': [c]})})
node = subprocess.run(['node', str(Path(__file__).with_suffix('.mjs'))], text=True, capture_output=True, check=True)
result = {
    'command': 'python3 campaigns/C/rounds/01/critic-probes.py',
    'browser_or_at_executed': False,
    'candidate_declarations_findings': checker.check(good),
    'malformed_submit_policy_probes': rows,
    'valid_controls': controls,
    'node_handler_probes': json.loads(node.stdout),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(1 if any(row['defect_reproduced'] for row in rows) or result['node_handler_probes']['staleBefore']['reproduced'] else 0)
