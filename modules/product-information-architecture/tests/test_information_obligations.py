"""Information obligations follow an offered task, not its roadmap priority.

These contract cases are independent of generated design-arm outputs. The shared
enabler control prevents inferring task delivery from a single kept capability.
"""
import copy
import unittest
from test_context import case
from test_validate import screen, validator


def offered(priority):
    brief, plan = case()
    brief['goals'][0]['priority'] = priority
    brief['requirements'][0]['mandatory'] = priority == 'must'
    brief['feature_requests'][0]['mandatory'] = priority == 'must'
    return brief, plan


class InformationObligationTests(unittest.TestCase):
    def test_priority_does_not_hide_needed_information_for_a_declared_route(self):
        for priority in ['must', 'should', 'could']:
            with self.subTest(priority=priority):
                b, p = offered(priority)
                p['screens'][0]['information'][0]['visibility'] = 'secondary'
                r = validator.validate(b, p)
                self.assertEqual('FAIL', r['status'], r)
                self.assertIn('HIDDEN_DECISION_INFORMATION', {x['code'] for x in r['issues']})

    def test_priority_does_not_allow_the_capability_to_be_elsewhere(self):
        for priority in ['must', 'should', 'could']:
            with self.subTest(priority=priority):
                b, p = offered(priority)
                p['screens'][0]['feature_ids'] = []
                p['screens'].append(screen('isolated', ['g'], ['main', 'legacy'],
                                           ['operator'], [], ['record_id']))
                r = validator.validate(b, p)
                self.assertEqual('FAIL', r['status'], r)
                self.assertIn('ROUTE_CAPABILITY_MISSING', {x['code'] for x in r['issues']})

    def test_visible_declared_tasks_pass_across_priorities(self):
        for priority in ['must', 'should', 'could']:
            with self.subTest(priority=priority):
                b, p = offered(priority)
                self.assertEqual('PASS', validator.validate(b, p)['status'])

    def test_deferred_optional_proposals_have_no_screen_obligation(self):
        b, p = offered('could')
        for source in b['feature_requests']:
            source.update(lifecycle='proposed', availability='planned')
        for f in p['features']:
            f.update(disposition='defer', reason='Optional proposal is not offered.',
                     revisit='Review after the requested main service is defined.')
        p['screens'], p['goal_routes'] = [], []
        p['decision_notes'].append('The optional goal is deferred; this plan does not offer its task.')
        self.assertEqual('PASS', validator.validate(b, p)['status'])

    def test_shared_enabler_does_not_offer_a_deferred_optional_goal(self):
        for priority in ['should', 'could']:
            with self.subTest(priority=priority):
                b, p = offered('must')
                b['goals'].append({'id':'g_optional', 'role':'operator', 'outcome':'Export a record',
                                  'priority':priority, 'needed_information':['export_scope']})
                b['requirements'].append({'id':'q_optional', 'goal_ids':['g_optional'],
                                          'mandatory':False, 'statement':'Optional proposed export'})
                for f in [b['feature_requests'][0], p['features'][0]]:
                    f['goal_ids'].append('g_optional')
                extra = copy.deepcopy(b['feature_requests'][1])
                extra.update(id='export', outcome='export-record', goal_ids=['g_optional'],
                             requirement_ids=['q_optional'], dependencies=['main'],
                             lifecycle='proposed', availability='planned', mandatory=False)
                b['feature_requests'].append(extra)
                f = copy.deepcopy(extra)
                f.update(disposition='defer', target=None, reason='Optional export is not offered.',
                         priority='low', priority_basis='Requested later', revisit='When export is commissioned')
                p['features'].append(f)
                p['decision_notes'].append('main supports the current lookup and a future export; only lookup is offered.')
                self.assertEqual('PASS', validator.validate(b, p)['status'])
