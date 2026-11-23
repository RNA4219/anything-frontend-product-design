"""Adversarial registry fixtures: prevent evidence-free acceptance and broken provenance."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('check_registry', Path(__file__).parents[1]/'checks/check_registry.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class RegistryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'registry/B/skills').mkdir(parents=True)
        (self.root/'registry/B/sources').mkdir(parents=True)
        (self.root/'evidence.json').write_text('{}')
        self.source = {'source_id':'B-S1','url':'https://example.org/spec','section':'1','read_status':'read fixture'}
        self.unit = dict(skill_id='B-IU-001',domain='interaction-ux-flow',trigger=['async change'],intent='Confirm result',
            required_inputs=['operation contract'],decision_rules=[{'if':'reply lost','then':'reconcile','basis':'campaign_inference','source_refs':['B-S1']}],
            procedure=['Inspect result'],expected_outputs=['recovery path'],dependencies=[],exceptions=[],failure_modes=['duplicate side effect'],
            verification={'criteria':['truthful result'],'evidence':['evidence.json'],'limitations':['synthetic']},
            source_refs=['B-S1'],confidence={'source_support':'fixture','transfer':'unmeasured','limits':['fixture']},status='ACCEPT',version='1.0.0')
    def write(self, unit=None):
        (self.root/'registry/B/sources/B-S1.json').write_text(json.dumps(self.source))
        (self.root/'registry/B/skills/B-IU-001.json').write_text(json.dumps(unit or self.unit))
        return checker.validate(self.root)
    def test_complete_record(self):
        self.assertEqual(self.write()['errors'], [])
    def test_no_accept_without_evidence(self):
        self.unit['verification']['evidence']=[]
        self.assertTrue(any('ACCEPT without evidence' in x for x in self.write()['errors']))
    def test_missing_evidence_file(self):
        (self.root/'evidence.json').unlink()
        self.assertTrue(any('missing or external evidence' in x for x in self.write()['errors']))
    def test_unknown_source(self):
        self.unit['source_refs']=['missing']
        self.assertTrue(any('unknown source' in x for x in self.write()['errors']))
    def test_rule_without_condition(self):
        self.unit['decision_rules'][0].pop('if')
        self.assertTrue(any('rule lacks condition' in x for x in self.write()['errors']))
    def test_no_fact_inference_conflation(self):
        self.unit['decision_rules'][0]['basis']='proven by intuition'
        self.assertTrue(any('distinguish fact and inference' in x for x in self.write()['errors']))
    def test_duplicate_unit(self):
        self.write()
        (self.root/'registry/B/skills/duplicate.json').write_text(json.dumps(self.unit))
        self.assertTrue(any('duplicate or invalid skill' in x for x in checker.validate(self.root)['errors']))
    def test_external_evidence_not_published(self):
        self.unit['verification']['evidence']=['../private-result.json']
        self.assertTrue(any('external evidence' in x for x in self.write()['errors']))

if __name__ == '__main__':
    unittest.main()
