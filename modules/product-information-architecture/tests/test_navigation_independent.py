"""Replay independently authored, mechanically decidable R02 cases."""
import json
from pathlib import Path
import unittest
from test_validate import validator


class IndependentNavigationTests(unittest.TestCase):
    def test_independent_controls_holds_and_errors(self):
        root = Path(__file__).parent / 'independent-navigation-fixtures'
        cases = json.loads((root / 'expectations.json').read_text())['cases']
        for name, expected in cases.items():
            with self.subTest(case=name):
                brief = json.loads((root / name / 'brief.json').read_text())
                plan = json.loads((root / name / 'plan.json').read_text())
                result = validator.validate(brief, plan)
                self.assertEqual(expected, result['status'], result)
