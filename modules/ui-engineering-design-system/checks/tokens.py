"""Bounded DTCG 2025.10-inspired token compiler, not a conforming DTCG consumer.

Stdlib only. Pure build() returns all themes or diagnostics with no CSS.
The project wrapper and supported subset are specified in references/token-contracts.md.
"""
import argparse
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

FORMAT = 'C-token-subset/1'
TYPES = {'color', 'dimension', 'duration', 'number'}
SEGMENT = re.compile(r'[A-Za-z0-9_-]+\Z')
IDENTIFIER = re.compile(r'[A-Za-z][A-Za-z0-9_-]*\Z')
ALIAS = re.compile(r'\{([A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*)\}\Z')
LIMITS = {'group_depth': 32, 'tokens_per_theme': 10000, 'alias_depth': 256,
          'json_depth': 64, 'json_nodes': 250000, 'integer_bits': 1024}
VISUAL = {k: 'NOT_TESTED' for k in (
    'rendered_contrast', 'forced_colors', 'nested_themes', 'browser_support',
    'assistive_technology', 'wcag_conformance')}


class TokenError(ValueError):
    def __init__(self, kind, code, path, message, chain=None):
        super().__init__(message)
        self.diagnostic = {'kind': kind, 'code': code, 'path': path or '<root>',
                           'message': message}
        if chain is not None:
            self.diagnostic['chain'] = chain


def fail(kind, code, path, message, chain=None):
    raise TokenError(kind, code, path, message, chain)


def finite(value):
    return type(value) in (int, float) and (type(value) is int or math.isfinite(value))


def resources(value):
    """Bound the JSON-shaped input iteratively, before recursive copies/traversals."""
    stack, count = [(value, 0, '<root>')], 0
    while stack:
        node, depth, path = stack.pop()
        count += 1
        if depth > LIMITS['json_depth']:
            fail('LIMIT', 'JSON_DEPTH', path, f'JSON nesting limit: {LIMITS["json_depth"]}')
        if count > LIMITS['json_nodes']:
            fail('LIMIT', 'JSON_NODES', path, f'JSON node limit: {LIMITS["json_nodes"]}')
        if type(node) is int and node.bit_length() > LIMITS['integer_bits']:
            fail('LIMIT', 'INTEGER_SIZE', path, f'Integer magnitude limit: {LIMITS["integer_bits"]} bits')
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str):
                    fail('INVALID', 'JSON_KEY', path, 'JSON object keys must be strings')
                stack.append((child, depth + 1, path + '/' + key))
        elif isinstance(node, list):
            stack.extend((child, depth + 1, path + '/' + str(i)) for i, child in enumerate(node))
        elif not isinstance(node, (str, int, float, bool, type(None))):
            fail('INVALID', 'JSON_TYPE', path, 'Only JSON value types are supported')


def typename(value, path):
    if not isinstance(value, str):
        fail('INVALID', 'TYPE_SHAPE', path, '$type must be a string')
    if value not in TYPES:
        fail('UNSUPPORTED', 'TYPE_UNSUPPORTED', path, f'Unsupported type: {value}')
    return value


def segment(value, path):
    if not isinstance(value, str) or not value or any(c in value for c in '.{}') or value.startswith('$'):
        fail('INVALID', 'TOKEN_NAME', path, 'Empty or reserved token/group name')
    if not SEGMENT.fullmatch(value):
        fail('UNSUPPORTED', 'NAME_SUBSET', path, 'This CSS name mapping supports ASCII letters, digits, underscore, hyphen only')


def reject_value_constructs(value, path):
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or key.startswith('$'):
                fail('UNSUPPORTED', 'VALUE_CONSTRUCT', path, 'Property references and semantic extension objects are unsupported')
            reject_value_constructs(child, path)
    elif isinstance(value, list):
        for child in value:
            reject_value_constructs(child, path)


def flatten(document):
    tokens = {}

    def walk(node, parts=(), inherited=None):
        path = '.'.join(parts)
        if len(parts) > LIMITS['group_depth']:
            fail('LIMIT', 'GROUP_DEPTH', path, f'Group depth limit: {LIMITS["group_depth"]}')
        if not isinstance(node, dict):
            fail('INVALID', 'NODE_SHAPE', path, 'Every token/group must be an object')
        for key in node:
            if not isinstance(key, str):
                fail('INVALID', 'KEY_SHAPE', path, 'Keys must be strings')
            if key.startswith('$') and key not in {'$value', '$type', '$description'}:
                fail('UNSUPPORTED', 'NODE_CONSTRUCT', path, f'{key} is not implemented; this is not a DTCG-invalidity judgment')
        if '$description' in node and not isinstance(node['$description'], str):
            fail('INVALID', 'DESCRIPTION_SHAPE', path, '$description must be a string')
        declared = typename(node['$type'], path) if '$type' in node else None
        if '$value' in node:
            if not parts:
                fail('INVALID', 'ROOT_SHAPE', path, 'Document root must contain named tokens/groups')
            if any(not key.startswith('$') for key in node):
                fail('UNSUPPORTED', 'TOKEN_EXTRA_FIELDS', path, 'Only $value, $type and $description are supported on tokens')
            reject_value_constructs(node['$value'], path)
            tokens[path] = {'raw': deepcopy(node['$value']), 'declared_type': declared,
                            'inherited_type': inherited}
            if len(tokens) > LIMITS['tokens_per_theme']:
                fail('LIMIT', 'TOKEN_COUNT', path, f'Token limit: {LIMITS["tokens_per_theme"]}')
        else:
            for key in sorted(k for k in node if not k.startswith('$')):
                segment(key, path)
                walk(node[key], parts + (key,), declared or inherited)

    walk(document)
    if not tokens:
        fail('CONTRACT', 'NO_TOKENS', '', 'This build contract requires at least one token')
    return tokens


def validate_value(kind, value, path):
    if kind == 'number':
        if not finite(value):
            fail('INVALID', 'NUMBER_VALUE', path, 'Expected a finite JSON number, excluding boolean')
    elif kind in {'dimension', 'duration'}:
        units = {'px', 'rem'} if kind == 'dimension' else {'ms', 's'}
        if not isinstance(value, dict) or set(value) != {'value', 'unit'}:
            fail('INVALID', 'MEASURE_SHAPE', path, 'Expected exactly {value, unit}, including unit at zero')
        if not finite(value['value']) or not isinstance(value['unit'], str) or value['unit'] not in units:
            fail('INVALID', 'MEASURE_VALUE', path, f'Expected finite number and unit in {sorted(units)}')
    elif kind == 'color':
        if not isinstance(value, dict) or not {'colorSpace', 'components'} <= value.keys():
            fail('INVALID', 'COLOR_SHAPE', path, 'Expected a structured color value')
        if set(value) - {'colorSpace', 'components', 'alpha', 'hex'}:
            fail('UNSUPPORTED', 'COLOR_FIELDS', path, 'Additional color fields are unsupported')
        if not isinstance(value['colorSpace'], str):
            fail('INVALID', 'COLOR_SPACE_SHAPE', path, 'colorSpace must be a string')
        if value['colorSpace'] != 'srgb':
            fail('UNSUPPORTED', 'COLOR_SPACE', path, 'Only numeric sRGB is supported')
        components = value['components']
        if not isinstance(components, list) or len(components) != 3:
            fail('INVALID', 'COLOR_COMPONENTS', path, 'Expected exactly three components')
        if any(v == 'none' for v in components):
            fail('UNSUPPORTED', 'COLOR_NONE', path, 'The valid none keyword is outside this subset')
        if any(not finite(v) or not 0 <= v <= 1 for v in components):
            fail('INVALID', 'COLOR_RANGE', path, 'sRGB components must be numeric in [0,1]')
        alpha = value.get('alpha', 1)
        if not finite(alpha) or not 0 <= alpha <= 1:
            fail('INVALID', 'COLOR_ALPHA', path, 'alpha must be numeric in [0,1]')
        if 'hex' in value and (not isinstance(value['hex'], str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value['hex'])):
            fail('INVALID', 'COLOR_HEX', path, 'Optional fallback hex must have six digits')
    return deepcopy(value)


def resolve(document, origins=None):
    resources(document)
    tokens = flatten(document)
    resolved, visiting = {}, []
    origins = origins or {}

    def visit(path):
        if path in resolved:
            return resolved[path]
        if path in visiting:
            fail('INVALID', 'REFERENCE_CYCLE', path, 'Cyclic token reference', visiting + [path])
        if path not in tokens:
            fail('INVALID', 'REFERENCE_MISSING', path, 'Reference must target a complete existing token', visiting + [path])
        if len(visiting) >= LIMITS['alias_depth']:
            fail('LIMIT', 'ALIAS_DEPTH', path, f'Alias depth limit: {LIMITS["alias_depth"]}', visiting + [path])
        visiting.append(path)
        token = tokens[path]
        raw, explicit, parent = token['raw'], token['declared_type'], token['inherited_type']
        match = ALIAS.fullmatch(raw) if isinstance(raw, str) else None
        target = None
        if match:
            target = match.group(1)
            other = visit(target)
            if explicit is not None and explicit != other['type']:
                fail('INVALID', 'ALIAS_TYPE', path, 'Declared alias type differs from resolved target', visiting + [target])
            if explicit is None and parent is not None and parent != other['type']:
                fail('CONTRACT', 'AMBIGUOUS_ALIAS_TYPE', path, 'Conflicting parent/target types require explicit $type under this local policy', visiting + [target])
            effective, value = explicit or other['type'], deepcopy(other['value'])
            chain, value_origin = [path] + other['chain'], other['value_origin']
        else:
            if isinstance(raw, str) and ('var(' in raw or 'calc(' in raw or ('{' in raw and not raw.startswith('{'))):
                fail('UNSUPPORTED', 'EXPRESSION', path, 'Runtime CSS expressions and interpolated aliases are unsupported')
            if isinstance(raw, str) and ('{' in raw or '}' in raw):
                fail('INVALID', 'ALIAS_SYNTAX', path, 'Expected an exact whole-token {path} alias')
            effective = explicit or parent
            if effective is None:
                fail('INVALID', 'TYPE_MISSING', path, 'Do not infer a type from the value shape')
            value = validate_value(effective, raw, path)
            chain, value_origin = [path], origins.get(path, 'base')
        if len(chain) > LIMITS['alias_depth']:
            fail('LIMIT', 'ALIAS_DEPTH', path, f'Alias chain limit: {LIMITS["alias_depth"]}', chain)
        result = {'type': effective, 'value': value, 'declared_type': explicit,
                  'inherited_type': parent, 'alias_target': target, 'chain': chain,
                  'definition_origin': origins.get(path, 'base'), 'value_origin': value_origin}
        visiting.pop()
        resolved[path] = result
        return result

    for path in sorted(tokens):
        visit(path)
    return {path: resolved[path] for path in sorted(resolved)}


def merge(base, override, replaced, parts=(), existing=True):
    path = '.'.join(parts)
    if not isinstance(base, dict) or not isinstance(override, dict):
        fail('CONTRACT', 'MERGE_SHAPE', path, 'Groups and overrides must be objects')
    base_token, patch_token = '$value' in base, '$value' in override
    if base_token or patch_token:
        if base_token != patch_token and existing:
            fail('CONTRACT', 'MERGE_KIND', path, 'Token/group replacement or partial-token patch is unsupported')
        replaced.add(path)
        return deepcopy(override)
    result = deepcopy(base)
    for key, value in override.items():
        if key.startswith('$'):
            result[key] = deepcopy(value)
        else:
            result[key] = merge(result.get(key, {}), value, replaced, parts + (key,), key in result)
    return result


def number_text(value):
    if value == 0:
        return '0'
    if type(value) is int or value.is_integer():
        return str(int(value))
    return repr(value)


def serialize(token):
    kind, value = token['type'], token['value']
    if kind == 'number':
        return number_text(value)
    if kind in {'dimension', 'duration'}:
        return number_text(value['value']) + value['unit']
    components = ' '.join(number_text(x) for x in value['components'])
    return f'color(srgb {components} / {number_text(value.get("alpha", 1))})'


def build(config):
    """Return a complete build result. Any theme error suppresses the CSS bundle."""
    diagnostics, result = [], {}
    try:
        resources(config)
        fields = {'format', 'prefix', 'default_theme', 'base', 'themes', 'roles'}
        if not isinstance(config, dict) or not fields <= config.keys():
            fail('CONTRACT', 'CONFIG_SHAPE', '', f'Required wrapper fields: {sorted(fields)}')
        if config.keys() - fields:
            fail('UNSUPPORTED', 'CONFIG_FIELDS', '', 'Extra wrapper fields, export filters and multiple destinations are unsupported')
        if config['format'] != FORMAT:
            fail('UNSUPPORTED', 'FORMAT', '', f'Expected project wrapper {FORMAT}')
        if not isinstance(config['prefix'], str) or not IDENTIFIER.fullmatch(config['prefix']):
            fail('CONTRACT', 'PREFIX', '', 'prefix must be a safe ASCII identifier beginning with a letter')
        themes, roles = config['themes'], config['roles']
        if not isinstance(themes, dict) or not themes:
            fail('CONTRACT', 'THEMES', '', 'Declare at least one theme')
        if not isinstance(config['default_theme'], str) or config['default_theme'] not in themes:
            fail('CONTRACT', 'DEFAULT_THEME', '', 'default_theme must name a declared theme')
        if not isinstance(roles, dict) or not roles:
            fail('CONTRACT', 'ROLES', '', 'Supply product-owned required role paths and types')
        for role, kind in roles.items():
            if not isinstance(role, str) or not role or any(not SEGMENT.fullmatch(p) for p in role.split('.')):
                fail('CONTRACT', 'ROLE_PATH', str(role), 'Role paths use the supported path syntax')
            typename(kind, role)
        for theme in themes:
            if not isinstance(theme, str) or not IDENTIFIER.fullmatch(theme):
                fail('CONTRACT', 'THEME_ID', str(theme), 'Theme IDs must map safely and injectively to generated selectors')
        names = {}
        for theme in sorted(themes):
            try:
                replaced = set()
                document = merge(config['base'], themes[theme], replaced)
                tokens = resolve(document, {p: f'theme:{theme}' for p in replaced})
                for role, kind in roles.items():
                    if role not in tokens:
                        fail('CONTRACT', 'ROLE_MISSING', role, 'Required role missing after theme merge')
                    if tokens[role]['type'] != kind:
                        fail('CONTRACT', 'ROLE_TYPE', role, 'Required role has an incompatible effective type')
                for path in tokens:
                    name = '--' + config['prefix'] + '-' + path.replace('.', '-')
                    if name in names and names[name] != path:
                        fail('CONTRACT', 'CSS_NAME_COLLISION', path, f'{name} also represents {names[name]}')
                    names[name] = path
                    tokens[path]['css_name'] = name
                result[theme] = {'tokens': tokens, 'roles': {p: tokens[p] for p in sorted(roles)}}
            except TokenError as exc:
                diagnostics.append(dict(exc.diagnostic, theme=theme))
        if not diagnostics:
            blocks = []
            order = [config['default_theme']] + sorted(set(themes) - {config['default_theme']})
            for theme in order:
                selector = f'[data-theme="{theme}"]'
                if theme == config['default_theme']:
                    selector = ':root,\n' + selector
                lines = [f'  {t["css_name"]}: {serialize(t)};' for t in result[theme]['tokens'].values()]
                blocks.append(selector + ' {\n' + '\n'.join(lines) + '\n}')
            css = '/* C-token-subset/1: resolved literals; rendering unverified. */\n' + '\n\n'.join(blocks) + '\n'
        else:
            css = None
    except TokenError as exc:
        diagnostics.append(exc.diagnostic)
        css = None
    return {'status': 'FAIL' if diagnostics else 'PASS_SUPPORTED_SCOPE',
            'scope': 'bounded token graph, theme role and literal CSS serialization only',
            'format': FORMAT, 'dtcg_conformance': 'NOT_CLAIMED', 'limits': LIMITS,
            'diagnostics': diagnostics, 'themes': result if not diagnostics else {},
            'css': css, 'visual': dict(VISUAL)}


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            fail('INVALID', 'DUPLICATE_JSON_KEY', key, 'Duplicate JSON member would create an implicit overwrite')
        obj[key] = value
    return obj


def load(path):
    def reject_constant(value):
        fail('INVALID', 'JSON_NUMBER', '', f'Non-JSON numeric constant: {value}')
    def integer(value):
        if len(value.lstrip('-')) > 309:
            fail('LIMIT', 'INTEGER_SIZE', '', f'Integer magnitude limit: {LIMITS["integer_bits"]} bits')
        number = int(value)
        if number.bit_length() > LIMITS['integer_bits']:
            fail('LIMIT', 'INTEGER_SIZE', '', f'Integer magnitude limit: {LIMITS["integer_bits"]} bits')
        return number
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_pairs,
                      parse_constant=reject_constant, parse_int=integer)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--css', help='Atomically replace this single CSS file only after all checks pass')
    args = parser.parse_args(argv)
    try:
        report = build(load(args.input))
        if args.css and report['status'] == 'PASS_SUPPORTED_SCOPE':
            target = Path(args.css)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=target.parent, delete=False) as stream:
                    temporary = stream.name
                    stream.write(report['css'])
                os.replace(temporary, target)
            finally:
                if temporary and os.path.exists(temporary):
                    os.unlink(temporary)
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if report['diagnostics'] else 0
    except (OSError, ValueError, RecursionError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, TokenError) else {'kind': 'IO_OR_PARSE', 'code': type(exc).__name__, 'message': str(exc)}
        print(json.dumps({'status': 'ERROR_INPUT_OR_OUTPUT', 'diagnostics': [diagnostic], 'css': None}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
