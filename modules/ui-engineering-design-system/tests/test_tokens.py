"""Token contracts: exact outputs, metamorphic checks and seeded counterexamples."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1]
ROOT = MODULE.parents[1]
spec = importlib.util.spec_from_file_location('c_tokens', MODULE / 'checks/tokens.py')
tokens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokens)


def example():
    return json.loads((MODULE / 'examples/booking-tokens.json').read_text())


def tiny(document, roles=None):
    return {'format': tokens.FORMAT, 'prefix': 'specimen', 'default_theme': 'one',
            'base': document, 'themes': {'one': {}}, 'roles': roles or {'x': 'dimension'}}


def bad_cases():
    cases = {}
    d = example(); d['base']['semantic']['text']['$value'] = '{missing}'
    cases['missing-reference'] = d
    d = example(); d['base']['semantic']['text']['$value'] = '{semantic.surface}'; d['base']['semantic']['surface']['$value'] = '{semantic.text}'
    cases['cycle'] = d
    d = example(); d['base']['semantic']['text']['$type'] = 'dimension'
    cases['type-mismatch'] = d
    d = example(); d['themes']['dark']['semantic'] = {'text': {'$value': '{absent}'}}
    cases['theme-only-missing-reference'] = d
    d = example(); d['base']['semantic']['text'] = {'$ref': '#/palette/ink/$value'}
    cases['unsupported-construct'] = d
    d = example(); d['base']['a-b'] = {'c': {'$type': 'number', '$value': 1}}; d['base']['a'] = {'b-c': {'$type': 'number', '$value': 2}}
    cases['name-collision'] = d
    d = example(); d['roles']['semantic.missing'] = 'color'
    cases['required-role-missing'] = d
    return cases


class TokenContracts(unittest.TestCase):
    def test_booking_theme_values_are_resolved_after_merge(self):
        result = tokens.build(example())
        self.assertEqual(result['status'], 'PASS_SUPPORTED_SCOPE')
        light, dark = (result['themes'][x]['roles'] for x in ('light', 'dark'))
        self.assertEqual(light['semantic.text']['value']['components'], [0.1, 0.1, 0.1])
        self.assertEqual(dark['semantic.text']['value']['components'], [0.95, 0.95, 0.95])
        self.assertEqual(dark['semantic.text']['value_origin'], 'theme:dark')
        self.assertEqual(dark['semantic.text']['definition_origin'], 'base')

    def test_known_invalid_inputs_fail_without_partial_css(self):
        for name, config in bad_cases().items():
            with self.subTest(name=name):
                result = tokens.build(config)
                self.assertEqual(result['status'], 'FAIL')
                self.assertIsNone(result['css'])
                self.assertEqual(result['themes'], {})
                self.assertTrue(all(d.get('path') for d in result['diagnostics']))

    def test_chain_has_exact_type_value_and_provenance(self):
        result = tokens.resolve({'base': {'$type': 'dimension', '$value': {'value': 0.5, 'unit': 'rem'}},
                                 'semantic': {'$value': '{base}'},
                                 'control': {'$type': 'dimension', '$value': '{semantic}'}})
        self.assertEqual(result['control']['type'], 'dimension')
        self.assertEqual(result['control']['value'], {'value': 0.5, 'unit': 'rem'})
        self.assertEqual(result['control']['chain'], ['control', 'semantic', 'base'])

    def test_group_inheritance_and_zero_unit_are_distinct(self):
        self.assertEqual(tokens.resolve({'g': {'$type': 'dimension', 'x': {'$value': {'value': 0, 'unit': 'px'}}}})['g.x']['type'], 'dimension')
        for value in ({'value': 0}, {'value': 0, 'unit': []}):
            with self.subTest(value=value), self.assertRaises(tokens.TokenError):
                tokens.resolve({'x': {'$type': 'dimension', '$value': value}})

    def test_do_not_infer_literal_type(self):
        with self.assertRaises(tokens.TokenError) as context:
            tokens.resolve({'x': {'$value': {'value': 1, 'unit': 'px'}}})
        self.assertEqual(context.exception.diagnostic['code'], 'TYPE_MISSING')

    def test_cycle_error_keeps_reference_route(self):
        with self.assertRaises(tokens.TokenError) as context:
            tokens.resolve({'x': {'$value': '{y}'}, 'y': {'$value': '{z}'}, 'z': {'$value': '{x}'}})
        self.assertEqual(context.exception.diagnostic['chain'], ['x', 'y', 'z', 'x'])

    def test_srgb_alpha_and_dimension_serialization(self):
        config = example()
        config['base']['palette']['ink']['$value']['alpha'] = 0.5
        result = tokens.build(config)
        self.assertIn('--booking-palette-ink: color(srgb 0.1 0.1 0.1 / 0.5);', result['css'])
        self.assertIn('--booking-size-line: 1px;', result['css'])
        self.assertIn('--booking-motion-feedback: 120ms;', result['css'])
        self.assertNotIn('--booking-size-line-value', result['css'])
        self.assertNotIn('var(', result['css'])

    def test_theme_may_repoint_same_role(self):
        config = example()
        config['themes']['dark']['semantic'] = {'text': {'$value': '{palette.boundary}'}}
        result = tokens.build(config)
        self.assertEqual(result['themes']['dark']['roles']['semantic.text']['value']['components'], [0.4, 0.4, 0.4])

    def test_theme_induced_cycle_is_reported_with_theme(self):
        config = example()
        config['themes']['dark']['palette']['paper'] = {'$value': '{semantic.surface}'}
        result = tokens.build(config)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['diagnostics'][0]['theme'], 'dark')
        self.assertEqual(result['diagnostics'][0]['code'], 'REFERENCE_CYCLE')

    def test_json_member_order_does_not_change_css_or_results(self):
        def reverse(value):
            if isinstance(value, dict):
                return {k: reverse(v) for k, v in reversed(list(value.items()))}
            if isinstance(value, list):
                return [reverse(v) for v in value]
            return value
        self.assertEqual(tokens.build(example()), tokens.build(reverse(example())))

    def test_build_does_not_mutate_or_cache_input(self):
        config = example(); before = deepcopy(config)
        first = tokens.build(config)
        self.assertEqual(config, before)
        config['themes']['dark']['palette']['ink']['$value']['components'] = [0.8, 0.8, 0.8]
        second = tokens.build(config)
        self.assertNotEqual(first['css'], second['css'])
        self.assertEqual(first['themes']['light'], second['themes']['light'])

    def test_different_product_role_inventory(self):
        config = tiny({'layout': {'$type': 'dimension', 'gap': {'$value': {'value': 6, 'unit': 'px'}}},
                       'timeline': {'$type': 'duration', '$value': {'value': 0.2, 'unit': 's'}},
                       'ratio': {'$type': 'number', '$value': 1.25}},
                      {'layout.gap': 'dimension', 'timeline': 'duration', 'ratio': 'number'})
        config['prefix'] = 'expense'
        result = tokens.build(config)
        self.assertEqual(result['status'], 'PASS_SUPPORTED_SCOPE')
        self.assertIn('--expense-timeline: 0.2s;', result['css'])
        self.assertEqual(len(result['themes']['one']['roles']), 3)

    def test_no_browser_or_conformance_inference(self):
        result = tokens.build(example())
        self.assertEqual(set(result['visual'].values()), {'NOT_TESTED'})
        self.assertEqual(result['dtcg_conformance'], 'NOT_CLAIMED')

    def test_reject_unknown_output_options_and_group_token_conversion(self):
        config = example(); config['destinations'] = {'light': 'theme.css', 'dark': 'theme.css'}
        self.assertEqual(tokens.build(config)['diagnostics'][0]['kind'], 'UNSUPPORTED')
        for base in ({}, {'nested': {'$type': 'number', '$value': 1}}):
            config = example(); config['base']['x'] = base
            config['themes']['dark']['x'] = {'$type': 'number', '$value': 2}
            self.assertEqual(tokens.build(config)['diagnostics'][0]['code'], 'MERGE_KIND')

    def test_css_cli_is_all_or_nothing_on_validation_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'tokens.json'; target = root / 'tokens.css'
            target.write_text('previous valid build\n')
            source.write_text(json.dumps(bad_cases()['cycle']))
            result = subprocess.run([sys.executable, str(MODULE / 'checks/tokens.py'), str(source), '--css', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(target.read_text(), 'previous valid build\n')
            source.write_text(json.dumps(example()))
            result = subprocess.run([sys.executable, str(MODULE / 'checks/tokens.py'), str(source), '--css', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(), json.loads(result.stdout)['css'])

    def test_duplicate_json_member_is_rejected_before_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'tokens.json'; source.write_text('{"themes": {}, "themes": {"dark": {}}}')
            result = subprocess.run([sys.executable, str(MODULE / 'checks/tokens.py'), str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['diagnostics'][0]['code'], 'DUPLICATE_JSON_KEY')

    def test_recorded_research_training_vectors(self):
        data = json.loads((ROOT / 'research/ui-engineering-design-system/round-02/researcher-1.json').read_text())
        expected = {'valid-explicit': True, 'valid-group-inheritance': True,
                    'valid-alias-inference': True, 'valid-chain': True, 'valid-srgb': True,
                    'missing-reference': False, 'cycle': False, 'type-mismatch': False,
                    'unsupported-property-ref': False, 'unsupported-extension': False,
                    'unsupported-composite': False, 'invalid-zero-no-unit': False}
        found = set()
        for case in data['test_vectors']:
            if case['id'] not in expected:
                continue
            found.add(case['id'])
            with self.subTest(case=case['id']):
                try:
                    tokens.resolve(case['input'])
                    accepted = True
                except tokens.TokenError:
                    accepted = False
                self.assertEqual(accepted, expected[case['id']])
        self.assertEqual(found, set(expected))

    def test_deep_input_and_large_integer_are_bounded_before_copy(self):
        deeply_nested = {'$type': 'number', '$value': 1}
        for _ in range(1200):
            deeply_nested = {'group': deeply_nested}
        result = tokens.build(tiny(deeply_nested))
        self.assertEqual(result['diagnostics'][0]['code'], 'JSON_DEPTH')
        self.assertIsNone(result['css'])
        config = tiny({'x': {'$type': 'number', '$value': 10 ** 5000}}, {'x': 'number'})
        result = tokens.build(config)
        self.assertEqual(result['diagnostics'][0]['code'], 'INTEGER_SIZE')
        self.assertIsNone(result['css'])

    def test_cli_malformed_utf8_and_large_integer_have_json_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'bad.json'
            for raw in (b'\xff\xfe', b'{"huge":' + b'9' * 5001 + b'}'):
                with self.subTest(kind=raw[:10]):
                    source.write_bytes(raw)
                    result = subprocess.run([sys.executable, str(MODULE / 'checks/tokens.py'), str(source)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(json.loads(result.stdout)['status'], 'ERROR_INPUT_OR_OUTPUT')
                    self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
