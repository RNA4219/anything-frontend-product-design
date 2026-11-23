"""Frozen inputs authored by an independent critic before the fixes."""
import json
from pathlib import Path
import unittest
from test_validate import validator


class IndependentRegressions(unittest.TestCase):
    def test_critic_counterexamples_and_controls(self):
        expectations = {
            'ce01_unreachable_capability': ('FAIL', 'ROUTE_CAPABILITY_MISSING'),
            'ce02_planned_merge_replacement': ('HOLD', 'MERGE_NOT_CURRENT'),
            'ce04_mixed_role_screen_leak': ('FAIL', 'FEATURE_ROLE'),
            'control_live_reachable': ('PASS', None),
            'control_current_merge_replacement': ('PASS', None),
        }
        for name, (status, code) in expectations.items():
            with self.subTest(name=name):
                base = Path(__file__).parent / 'independent-fixtures' / name
                r = validator.validate(json.loads((base / 'brief.json').read_text()), json.loads((base / 'plan.json').read_text()))
                self.assertEqual(r['status'], status, r)
                if code:
                    self.assertIn(code, {x['code'] for x in r['issues']})


if __name__ == '__main__':
    unittest.main()
