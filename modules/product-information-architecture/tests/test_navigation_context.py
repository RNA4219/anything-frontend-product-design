"""Boundary checks: a string collision is a review cue, not semantic proof."""
import unittest
from test_validate import catalog_case, validator


class NavigationContextTests(unittest.TestCase):
    def test_context_assertion_does_not_silently_waive_a_collision(self):
        brief, plan = catalog_case()
        plan['navigation'][0]['label'] = '詳細'
        plan['navigation'][1]['label'] = '詳細'
        plan['decision_notes'].append('行の文脈で区別できると設計者が考えている。実画面の関連付けは未確認。')
        result = validator.validate(brief, plan)
        self.assertEqual('HOLD', result['status'])
        self.assertEqual('hold', next(x['severity'] for x in result['issues']
                                     if x['code'] == 'AMBIGUOUS_SIBLING_LABEL'))
        # Distinct declared contextual meanings remain structurally valid.
        plan['navigation'][0]['label'] = '候補の比較を開く'
        plan['navigation'][1]['label'] = '選択した講座の詳細を開く'
        self.assertEqual('PASS', validator.validate(brief, plan)['status'])
