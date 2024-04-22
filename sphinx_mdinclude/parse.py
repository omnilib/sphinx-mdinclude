from typing import Any, Dict, Match, Tuple

from mistune import BlockParser, InlineParser
from mistune.core import BlockState, InlineState
from mistune.helpers import HTML_ATTRIBUTES, HTML_TAGNAME


State = Dict[str, Any]
Token = Dict[str, Any]
Element = Tuple[str, ...]


class RestBlockParser(BlockParser):
    SPECIFICATION = BlockParser.SPECIFICATION.copy()
    SPECIFICATION.update(
        {
            "directive": r"(?ms:^(?P<directive_1> *\.\..*?)\n(?=\S))",
            "oneline_directive": r"(?ms:^(?P<directive_2> *\.\..*?)$)",
            "rest_code_block": r"(?m:^::\s*$)",
        }
    )

    DEFAULT_RULES = BlockParser.DEFAULT_RULES + (  # type: ignore[has-type]
        "directive",
        "oneline_directive",
        "rest_code_block",
    )

    def parse_directive(self, m: Match[str], state: BlockState) -> int:
        state.append_token({"type": "directive", "raw": m.group("directive_1")})
        return m.end()

    def parse_oneline_directive(self, m: Match[str], state: BlockState) -> int:
        # reuse directive output
        state.append_token({"type": "directive", "raw": m.group("directive_2")})
        # $ does not count '\n'
        return m.end() + 1

    def parse_rest_code_block(self, m: Match[str], state: BlockState) -> int:
        state.append_token({"type": "rest_code_block", "text": ""})
        # $ does not count '\n'
        return m.end() + 1


class RestInlineParser(InlineParser):
    # make inline_html span open/contents/close instead of just a single tag
    INLINE_HTML = (
        r"(?<!\\)<" + HTML_TAGNAME + HTML_ATTRIBUTES + r"\s*>"  # open tag
        r"(.*)"
        r"(?<!\\)</" + HTML_TAGNAME + r"\s*>|"  # close tag
        r"(?<!\\)<" + HTML_TAGNAME + HTML_ATTRIBUTES + r"\s*/>|"  # open/close tag
        r"(?<!\\)<\?[\s\S]+?\?>|"
        r"(?<!\\)<![A-Z][\s\S]+?>|"  # doctype
        r"(?<!\\)<!\[CDATA[\s\S]+?\]\]>"  # cdata
    )

    SPECIFICATION = InlineParser.SPECIFICATION.copy()
    SPECIFICATION.update(
        {
            "inline_html": INLINE_HTML,
            "inline_math": r"`\$(?P<math_1>.*?)\$`",
            "rest_role": r":.*?:`.*?`|`[^`]+`:.*?:",
            "rest_link": r"`[^`]*?`_",
            "eol_literal_marker": r"(?P<eol_space>\s+)?::\s*$",
        }
    )

    # Order is important: need these rules to be checked before the
    # default rules
    DEFAULT_RULES = (
        "inline_math",
        "rest_role",
        "rest_link",
        "eol_literal_marker",
    ) + InlineParser.DEFAULT_RULES  # type: ignore[has-type]

    def parse_rest_role(self, m: Match[str], state: InlineState) -> int:
        """Pass through rest role."""
        state.append_token({"type": "rest_role", "raw": m.group(0)})
        return m.end()

    def parse_rest_link(self, m: Match[str], state: InlineState) -> int:
        """Pass through rest link."""
        state.append_token({"type": "rest_link", "raw": m.group(0)})
        return m.end()

    def parse_inline_math(self, m: Match[str], state: InlineState) -> int:
        """Pass through inline math."""
        state.append_token({"type": "inline_math", "raw": m.group("math_1")})
        return m.end()

    def parse_eol_literal_marker(self, m: Match[str], state: InlineState) -> int:
        """Pass through rest link."""
        marker = ":" if m.group("eol_space") is None else ""
        state.append_token({"type": "eol_literal_marker", "raw": marker})
        # $ does not count '\n'
        return m.end() + 1
