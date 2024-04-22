import re
import textwrap
from functools import partial
from importlib import import_module
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from docutils.utils import column_width
from mistune import Markdown
from mistune.core import BaseRenderer, BlockState
from mistune.plugins import _plugins

from .parse import RestBlockParser, RestInlineParser

CACHED_MODULES: Dict[str, Any] = {}
DEFAULT_PLUGINS = ["strikethrough", "footnotes", "table"]

PROLOG = """\
.. role:: raw-html-md(raw)
   :format: html

"""


class RestRenderer(BaseRenderer):
    _include_raw_html = False
    indent = " " * 3
    list_marker = "{#__rest_list_mark__#}"
    hmarks = {
        1: "=",
        2: "-",
        3: "^",
        4: "~",
        5: '"',
        6: "#",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._indent_block = partial(textwrap.indent, prefix=self.indent)
        super().__init__(*args, **kwargs)

    def render_token(self, token: Dict[str, Any], state: BlockState) -> str:
        # based on mistune 3.0.2, mistune/renderers/html.py
        func: Callable[..., str] = self._get_method(token["type"])
        attrs = token.get("attrs")
        style = token.get("style")

        if "raw" in token:
            text = token["raw"]
        elif "children" in token:
            text = self.render_tokens(token["children"], state)
        else:
            if attrs:
                return func(**attrs)
            else:
                return func()

        # We have to special-case block_code, as it needs to know the
        # style as well to determine whether to add a blank line at the
        # end (so as to retain the original behaviour)
        if token["type"] == "block_code":
            if attrs:
                return func(text, style=style, **attrs)
            else:
                return func(text, style=style)

        if attrs:
            return func(text, **attrs)
        else:
            return func(text)

    def finalize(self, data: Iterable[str]) -> str:
        return "".join(data)

    def _raw_html(self, html: str) -> str:
        self._include_raw_html = True
        return r":raw-html-md:`{}`".format(html)

    def block_code(self, code: str, style: str, info: Optional[str] = None) -> str:
        if info == "math":
            first_line = "\n.. math::\n\n"
        elif info:
            first_line = "\n.. code-block:: {}\n\n".format(info)
        else:
            # first_line = "\n::\n\n"
            first_line = "\n.. code-block::\n\n"
        newline = "\n" if style == "indent" else ""
        return first_line + self._indent_block(code + newline)

    def block_quote(self, text: str) -> str:
        # text includes some empty line
        return "\n..\n\n{}\n\n".format(self._indent_block(text.strip("\n")))

    def block_text(self, text: str) -> str:
        return text

    def block_html(self, html: str) -> str:
        """Rendering block level pure html content.

        :param html: text content of the html snippet.
        """
        return "\n\n.. raw:: html\n\n" + self._indent_block(html) + "\n"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        """Rendering header/heading tags like ``<h1>`` ``<h2>``.

        :param text: rendered text content for the header.
        :param level: a number for the header level, for example: 1.
        :param attrs: other attributes of the header.
        """
        return "\n{0}\n{1}\n".format(text, self.hmarks[level] * column_width(text))

    def thematic_break(self) -> str:
        """Rendering method for ``<hr>`` tag."""
        return "\n----\n"

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        """Rendering list tags like ``<ul>`` and ``<ol>``.

        :param text: body contents of the list.
        :param ordered: whether this list is ordered or not.
        :param attrs: other attributes of the list.
        """
        mark = "#. " if ordered else "* "
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line and not line.startswith(self.list_marker):
                lines[i] = " " * len(mark) + line
        result = "\n{}\n".format("\n".join(lines)).replace(self.list_marker, mark)
        return result

    def list_item(self, text: str) -> str:
        """Rendering list item snippet. Like ``<li>``."""
        return "\n" + self.list_marker + text

    def paragraph(self, text: str) -> str:
        """Rendering paragraph tags. Like ``<p>``."""
        return "\n" + text + "\n"

    def table(self, body: str) -> str:
        """Rendering table element. Wrap header and body in it.

        :param header: header part of the table.
        :param body: body part of the table.
        """
        table = "\n.. list-table::\n"
        table = table + self._indent_block(body) + "\n"
        return table

    def table_head(self, text: str) -> str:
        return ":header-rows: 1\n\n" + self.table_row(text)

    def table_body(self, text: str) -> str:
        return text

    def table_row(self, content: str) -> str:
        """Rendering a table row. Like ``<tr>``.

        :param content: content of current table row.
        """
        contents = content.splitlines()
        if not contents:
            return ""
        clist = ["* " + contents[0]]
        if len(contents) > 1:
            for c in contents[1:]:
                clist.append("  " + c)
        return "\n".join(clist) + "\n"

    def table_cell(self, content: str, align: None = None, head: bool = False) -> str:
        """Rendering a table cell. Like ``<th>`` ``<td>``.

        :param content: content of current table cell.
        :param align: align of current table cell.
        :param head: whether this is header or not.
        """
        return "- " + content + "\n"

    def double_emphasis(self, text: str) -> str:
        """Rendering **strong** text.

        :param text: text content for emphasis.
        """
        return r"**{}**".format(text)

    def emphasis(self, text: str) -> str:
        """Rendering *emphasis* text.

        :param text: text content for emphasis.
        """
        return r"*{}*".format(text)

    def strong(self, text: str) -> str:
        return r"**{}**".format(text)

    def codespan(self, text: str) -> str:
        """Rendering inline `code` text.

        :param text: text content for inline code.
        """
        cannot_inline = "``" in text or text[0] in [" ", "`"] or text[-1] in [" ", "`"]
        if cannot_inline:
            # actually, docutils split spaces in literal
            return self._raw_html(
                '<code class="docutils literal">'
                '<span class="pre">{}</span>'
                "</code>".format(text.replace("`", "&#96;"))
            )
        else:
            return r"``{}``".format(text)

    def linebreak(self) -> str:
        """Rendering line break like ``<br>``."""
        return " " + self._raw_html("<br />") + "\n"

    def softbreak(self) -> str:
        """Rendering soft line break."""
        return "\n"

    def strikethrough(self, text: str) -> str:
        """Rendering ~~strikethrough~~ text.

        :param text: text content for strikethrough.
        """
        return self._raw_html("<del>{}</del>".format(text))

    def text(self, text: str) -> str:
        """Rendering unformatted text.

        :param text: text content.
        """
        return text

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        """Rendering a given link with content and title.

        :param text: text content for description.
        :param url: URL for ``<a>`` tag.
        :param title: title content for `title` attribute.
        """
        if text.startswith("\n.. image::"):
            text = re.sub(r":target: (.*)\n", f":target: {url}\n", text)
            return text

        underscore = "_"
        if title:
            return self._raw_html(
                '<a href="{url}" title="{title}">{text}</a>'.format(
                    url=url, title=title, text=text
                )
            )
        if url.startswith("#"):
            target = url[1:]
            return r":ref:`{text} <{target}>`".format(target=target, text=text)

        return r"`{text} <{target}>`{underscore}".format(
            target=url, text=text, underscore=underscore
        )

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        """Rendering a image with title and text.

        :param text: alt text of the image.
        :param url: source link of the image.
        :param title: title text of the image.
        """
        # rst does not support title option
        # and I couldn't find title attribute in HTML standard
        return "\n".join(
            [
                "",
                ".. image:: {}".format(url),
                "   :target: {}".format(url),
                "   :alt: {}".format(text),
                "",
            ]
        )

    def image_link(self, url: str, target: str, alt: str) -> str:
        return "\n".join(
            [
                "",
                ".. image:: {}".format(url),
                "   :target: {}".format(target),
                "   :alt: {}".format(alt),
                "",
            ]
        )

    def inline_html(self, html: str) -> str:
        """Rendering span level pure html content.

        :param html: text content of the html snippet.
        """
        return self._raw_html(html)

    def newline(self) -> str:
        """Rendering newline element."""
        return ""

    def footnote_ref(self, key: str, index: int) -> str:
        """Rendering the ref anchor of a footnote.

        :param key: identity key for the footnote.
        :param index: the index count of current footnote.
        """
        return r"[#fn-{}]_".format(key)

    def footnote_item(self, text: str, key: str, index: int) -> str:
        """Rendering a footnote item.

        :param key: identity key for the footnote.
        :param text: text content of the footnote.
        """
        return ".. [#fn-{0}] {1}\n".format(key, text.strip())

    def footnotes(self, text: str) -> str:
        """Wrapper for all footnotes.

        :param text: contents of all footnotes.
        """
        if text:
            return "\n\n" + text
        else:
            return ""

    """Below outputs are for rst."""

    def rest_role(self, raw: str) -> str:
        return raw

    def rest_link(self, raw: str) -> str:
        return raw

    def inline_math(self, raw: str) -> str:
        """Extension of recommonmark."""
        return r":math:`{}`".format(raw)

    def eol_literal_marker(self, raw: str) -> str:
        """Extension of recommonmark."""
        return raw

    def directive(self, text: str) -> str:
        return "\n" + text

    def rest_code_block(self, text: str) -> str:
        return "\n\n"

    def blank_line(self) -> str:
        return ""


class RestMarkdown(Markdown):
    def __init__(
        self,
        renderer: Optional[BaseRenderer] = None,
        block: Optional[RestBlockParser] = None,
        inline: Optional[RestInlineParser] = None,
        plugins: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> None:
        renderer = renderer or RestRenderer()
        block = block or RestBlockParser()
        inline = inline or RestInlineParser()
        plugins_str = plugins or [_plugins[p] for p in DEFAULT_PLUGINS]
        plugins = []
        for plugin_str in plugins_str:
            if plugin_str in CACHED_MODULES:
                plugins.append(CACHED_MODULES[plugin_str])
            else:
                if isinstance(plugin_str, str):
                    module_path, func_name = plugin_str.rsplit(".", 1)
                    module = import_module(module_path)
                    plugin = getattr(module, func_name)
                else:
                    # Presumably a function has been passed
                    plugin = plugin_str
                CACHED_MODULES[plugin_str] = plugin
                plugins.append(plugin)

        super().__init__(renderer, block=block, inline=inline, plugins=plugins)

    def parse(
        self,
        text: str,
        state: Optional[BlockState] = None,
    ) -> Tuple[str, Optional[BlockState]]:
        output, state = super().parse(text)
        output = self.post_process(output)

        return output, state

    def post_process(self, text: str) -> str:
        if self.renderer._include_raw_html:
            return PROLOG + text
        else:
            return text


def convert(text: str, **kwargs: Any) -> str:
    return str(RestMarkdown(**kwargs)(text))
