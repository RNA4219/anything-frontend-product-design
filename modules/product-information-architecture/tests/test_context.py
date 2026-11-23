"""Task-derived counterexamples: same label, different scope; missing observations;
existing vs proposed capabilities; usable replacements and legitimate retirement.
These are contract tests, not measurements of human usability.
"""
import copy
import unittest
from test_validate import validator, screen, route


def case():
    brief = {
        'case_id': 'context-contract', 'visual_intent': {'id': 'unchanged'},
        'roles': [{'id': 'operator', 'label': 'Operator'}],
        'goals': [{'id': 'g', 'role': 'operator', 'outcome': 'Find the relevant record',
                   'priority': 'must', 'needed_information': ['record_id']}],
        'requirements': [{'id': 'q', 'goal_ids': ['g'], 'mandatory': True,
                          'statement': 'Identify the requested record'}],
        'feature_requests': [],
        'evidence': [{'id': 'contract', 'kind': 'requirement', 'statement': 'Same outcome and supported context are specified.',
                      'coverage': 'specified task and role', 'coverage_status': 'verified'},
                     {'id': 'unobserved', 'kind': 'observation', 'statement': 'No events in an opt-in sample.',
                      'coverage': 'unknown excluded population', 'coverage_status': 'unknown'}],
    }
    for fid in ['main', 'legacy']:
        brief['feature_requests'].append({
            'id': fid, 'label': 'Records', 'object': 'record', 'outcome': 'read-record',
            'roles': ['operator'], 'goal_ids': ['g'], 'requirement_ids': ['q'],
            'dependencies': [], 'mandatory': fid == 'main', 'scope': 'own-records',
            'context_constraints': ['mobile'], 'evidence_refs': ['contract'],
            'lifecycle': 'existing', 'availability': 'available',
        })
    features = []
    for source in brief['feature_requests']:
        f = copy.deepcopy(source)
        f.update(disposition='keep', target=None, reason='Preserve the record lookup task',
                 priority='required' if source['mandatory'] else 'medium', priority_basis='Task obligation')
        features.append(f)
    plan = {'schema_version': '1.1', 'case_id': brief['case_id'], 'visual_intent_id': 'unchanged',
            'features': features, 'screens': [screen('s', ['g'], ['main', 'legacy'], ['operator'], ['operator'], ['record_id'])],
            'navigation': [], 'goal_routes': [route('g', 's', 's')], 'unresolved': [], 'decision_notes': []}
    return brief, plan


def retire(plan, status='continued_elsewhere'):
    f = plan['features'][1]
    f.update(disposition='remove', retirement={'need_status': status, 'replacement': 'main' if status == 'continued_elsewhere' else None,
             'legacy_entry_action': 'Explain and link to the surviving lookup', 'data_handling': 'Same records retained',
             'revisit': 'Reopen if a documented role cannot perform its lookup'})
    plan['screens'][0]['feature_ids'] = ['main']
    return f


class ContextContractTests(unittest.TestCase):
    def codes(self, brief, plan):
        return {x['code'] for x in validator.validate(brief, plan)['issues']}

    def test_normal_context_is_not_a_usable_app_claim(self):
        b, p = case()
        r = validator.validate(b, p)
        self.assertEqual(r['status'], 'PASS', r)
        self.assertFalse(r['checks_available']['human_usability'])

    def test_scope_change_is_detected_even_if_output_alias_is_rewritten(self):
        b, p = case()
        b['feature_requests'][1]['scope'] = 'all-records'
        p['features'][1].update(disposition='merge', target='main')
        p['screens'][0]['feature_ids'] = ['main']
        self.assertIn('SCOPE_CHANGED', self.codes(b, p))

    def test_same_scope_alias_can_share_a_canonical_capability(self):
        b, p = case()
        p['features'][1].update(disposition='merge', target='main')
        p['screens'][0]['feature_ids'] = ['main']
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')

    def test_mobile_only_cannot_be_replaced_by_desktop_context(self):
        b, p = case()
        b['feature_requests'][0]['context_constraints'] = ['desktop']
        p['features'][0]['context_constraints'] = ['desktop']
        retire(p)
        self.assertIn('CONTEXT_CHANGED', self.codes(b, p))

    def test_a_current_same_context_replacement_is_allowed(self):
        b, p = case()
        retire(p)
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')

    def test_roadmap_is_not_a_current_replacement(self):
        b, p = case()
        b['feature_requests'][0]['availability'] = 'planned'
        retire(p)
        self.assertIn('REPLACEMENT_NOT_CURRENT', self.codes(b, p))

    def test_partial_replacement_requires_the_specific_outcome(self):
        b, p = case()
        b['feature_requests'][0]['availability'] = 'partial'
        retire(p)
        self.assertIn('PARTIAL_REPLACEMENT', self.codes(b, p))
        p['features'][0]['verified_outcomes'] = ['read-record']
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')

    def test_opt_in_zero_is_not_evidence_of_an_ended_need(self):
        b, p = case()
        f = retire(p, 'ended')
        f['evidence_refs'] = ['unobserved']
        self.assertEqual(validator.validate(b, p)['status'], 'HOLD')
        self.assertIn('RETIREMENT_EVIDENCE', self.codes(b, p))

    def test_explicitly_ended_optional_need_is_not_preserved_forever(self):
        b, p = case()
        retire(p, 'ended')
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')

    def test_unknown_scope_can_be_kept_but_not_used_to_assert_merge_equivalence(self):
        b, p = case()
        for f in b['feature_requests'] + p['features']:
            f['scope'] = 'unknown'
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')
        p['features'][1].update(disposition='merge', target='main')
        p['screens'][0]['feature_ids'] = ['main']
        self.assertEqual(validator.validate(b, p)['status'], 'HOLD')

    def test_new_unpromised_work_can_be_deferred_with_a_revisit_condition(self):
        b, p = case()
        b['feature_requests'][1]['lifecycle'] = 'proposed'
        p['features'][1].update(disposition='defer', revisit='Revisit after the discovery interview')
        p['screens'][0]['feature_ids'] = ['main']
        self.assertEqual(validator.validate(b, p)['status'], 'PASS')
        del p['features'][1]['revisit']
        self.assertIn('REVISIT_MISSING', self.codes(b, p))

    def test_existing_feature_deferral_needs_the_retirement_contract(self):
        b, p = case()
        p['features'][1]['disposition'] = 'defer'
        p['screens'][0]['feature_ids'] = ['main']
        self.assertIn('RETIREMENT_CONTRACT', self.codes(b, p))

    def test_bad_nested_context_or_evidence_does_not_crash(self):
        for field, value in [('scope', {}), ('context_constraints', [{}]), ('evidence_refs', [None])]:
            b, p = case()
            p['features'][0][field] = value
            self.assertEqual(validator.validate(b, p)['status'], 'FAIL')
        b, p = case()
        b['evidence'] = [False]
        self.assertEqual(validator.validate(b, p)['status'], 'FAIL')

    def test_unknown_evidence_id_is_not_silently_accepted(self):
        b, p = case()
        p['features'][1]['evidence_refs'] = ['invented']
        self.assertIn('UNKNOWN_EVIDENCE', self.codes(b, p))

    def test_legacy_contract_advertises_its_limited_check_scope(self):
        b, p = case()
        p['schema_version'] = '1.0'
        self.assertFalse(validator.validate(b, p)['checks_available']['context_and_retirement'])


if __name__ == '__main__':
    unittest.main()
