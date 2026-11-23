"""Frozen deliberately permissive experimental control, not a production baseline.

It only confirms that a token/theming declaration exists. The experiment measures
whether the candidate detects counterexamples missed by this shallow check;
it does not estimate LLM generation quality or an improvement percentage.
"""


def accepts(config):
    return (isinstance(config, dict) and isinstance(config.get('base'), dict)
            and isinstance(config.get('themes'), dict) and bool(config['themes']))
