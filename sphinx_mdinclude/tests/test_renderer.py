#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Tuple
from unittest import skip, TestCase

from docutils import io
from docutils.core import Publisher

from ..render import convert, PROLOG


class RendererTestBase(TestCase):
    def conv(self, src: str, **kwargs: Any) -> str:
        out = convert(src, **kwargs)
        self.check_rst(out)
        return out

    def conv_no_check(self, src: str, **kwargs: Any) -> str:
        out = convert(src, **kwargs)
        return out

    def check_rst(self, rst: str) -> Tuple[str, Publisher]:
        pub = Publisher(
            reader=None,
            parser=None,
            writer=None,
            settings=None,
            source_class=io.StringInput,
            destination_class=io.StringOutput,
        )
        pub.set_components(
            reader_name="standalone",
            parser_name="restructuredtext",
            writer_name="pseudoxml",
        )
        pub.process_programmatic_settings(
            settings_spec=None,
            settings_overrides={"output_encoding": "unicode"},
            config_section=None,
        )
        pub.set_source(rst, source_path=None)
        pub.set_destination(destination=None, destination_path=None)
        output = pub.publish(enable_exit_status=False)
        self.assertLess(pub.document.reporter.max_level, 0)
        return output, pub


class TestBasic(RendererTestBase):
    def test_fail_rst(self) -> None:
        with self.assertRaises(AssertionError):
            # This check should be failed and report warning
            self.check_rst("```")

    def test_simple_paragraph(self) -> None:
        src = "this is a sentence.\n"
        out = self.conv(src)
        self.assertEqual(out, "\n" + src)

    def test_multiline_paragraph(self) -> None:
        src = "\n".join(
            [
                "first sentence.",
                "second sentence.",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_multi_paragraph(self) -> None:
        src = "\n".join(
            [
                "first paragraph.",
                "",
                "second paragraph.",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_hr(self) -> None:
        src = "a\n\n---\n\nb"
        out = self.conv(src)
        self.assertEqual(out, "\na\n\n----\n\nb\n")

    def test_linebreak(self) -> None:
        src = "abc def  \nghi"
        out = self.conv(src)
        self.assertEqual(
            out,
            PROLOG + "\nabc def :raw-html-md:`<br />`\nghi" + "\n",
        )


class TestInlineMarkdown(RendererTestBase):
    def test_inline_code(self) -> None:
        src = "`a`"
        out = self.conv(src)
        self.assertEqual(out.replace("\n", ""), "``a``")

    def test_inline_code_with_backticks(self) -> None:
        src = "```a``a```"
        out = self.conv(src)
        self.assertEqual(
            out.strip(),
            ".. role:: raw-html-md(raw)\n"
            "   :format: html\n\n\n"
            ':raw-html-md:`<code class="docutils literal">'
            '<span class="pre">a&#96;&#96;a</span></code>`',
        )

    def test_inline_code_with_opening_space(self) -> None:
        src = "`` `a`:role:``"
        out = self.conv(src)
        self.assertEqual(
            out.strip(),
            ".. role:: raw-html-md(raw)\n"
            "   :format: html\n\n\n"
            ':raw-html-md:`<code class="docutils literal">'
            '<span class="pre"> &#96;a&#96;:role:</span></code>`',
        )

    def test_inline_code_with_closing_space(self) -> None:
        src = "``:role:`a` ``"
        out = self.conv(src)
        self.assertEqual(
            out.strip(),
            ".. role:: raw-html-md(raw)\n"
            "   :format: html\n\n\n"
            ':raw-html-md:`<code class="docutils literal">'
            '<span class="pre">:role:&#96;a&#96; </span></code>`',
        )

    def test_inline_code_with_opening_and_closing_space(self) -> None:
        src = "`` a ``"
        out = self.conv(src)
        self.assertEqual(out, "\n``a``\n")

    def test_inline_code_with_opening_and_closing_space_and_backtick(self) -> None:
        src = "`` `a` ``"
        out = self.conv(src)
        self.assertEqual(
            out.strip(),
            ".. role:: raw-html-md(raw)\n"
            "   :format: html\n\n\n"
            ':raw-html-md:`<code class="docutils literal">'
            '<span class="pre">&#96;a&#96;</span></code>`',
        )

    def test_strikethrough(self) -> None:
        src = "~~a~~"
        self.conv(src)

    def test_emphasis(self) -> None:
        src = "*a*"
        out = self.conv(src)
        self.assertEqual(out.replace("\n", ""), "*a*")

    def test_emphasis_(self) -> None:
        src = "_a_"
        out = self.conv(src)
        self.assertEqual(out.replace("\n", ""), "*a*")

    def test_double_emphasis(self) -> None:
        src = "**a**"
        out = self.conv(src)
        self.assertEqual(out.replace("\n", ""), "**a**")

    def test_double_emphasis__(self) -> None:
        src = "__a__"
        out = self.conv(src)
        self.assertEqual(out.replace("\n", ""), "**a**")

    def test_not_an_autolink(self) -> None:
        src = "link to http://example.com/ in sentence."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_link(self) -> None:
        src = "this is a [link](http://example.com/)."
        out = self.conv(src)
        self.assertEqual(out, "\nthis is a `link <http://example.com/>`_.\n")

    def test_anchor(self) -> None:
        src = "this is an [anchor link](#anchor)."
        out = self.conv_no_check(src)
        self.assertEqual(out, "\nthis is an :ref:`anchor link <anchor>`.\n")

    def test_autolink(self) -> None:
        src = "link <http://example.com>"
        out = self.conv(src)
        self.assertEqual(out, "\nlink `http://example.com <http://example.com>`_\n")

    def test_link_title(self) -> None:
        src = 'this is a [link](http://example.com/ "example").'
        out = self.conv(src)
        self.assertEqual(
            out,
            ".. role:: raw-html-md(raw)\n"
            "   :format: html\n\n\n"
            "this is a :raw-html-md:"
            '`<a href="http://example.com/" title="example">link</a>`.\n',
        )

    def test_image_link(self) -> None:
        src = "[![Alt Text](image_taget_url)](link_target_url)"
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n\n.. image:: image_taget_url\n"
            "   :target: link_target_url\n   :alt: Alt Text\n\n",
        )

    def test_rest_role(self) -> None:
        src = "a :code:`some code` inline."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_rest_role2(self) -> None:
        src = "a `some code`:code: inline."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_rest_link(self) -> None:
        src = "a `RefLink <http://example.com>`_ here."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_rest_link_and_role(self) -> None:
        src = "a :code:`a` and `RefLink <http://example.com>`_ here."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_rest_link_and_role2(self) -> None:
        src = "a `a`:code: and `RefLink <http://example.com>`_ here."
        out = self.conv(src)
        self.assertEqual(out, "\n" + src + "\n")

    def test_rest_role_incomplete(self) -> None:
        src = "a co:`de` and `RefLink <http://example.com>`_ here."
        out = self.conv(src)
        self.assertEqual(
            out,
            "\na co:``de`` and `RefLink <http://example.com>`_ here.\n",
        )

    def test_rest_role_incomplete2(self) -> None:
        src = "a `RefLink <http://example.com>`_ and co:`de` here."
        out = self.conv(src)
        self.assertEqual(
            out,
            "\na `RefLink <http://example.com>`_ and co:``de`` here.\n",
        )

    def test_rest_role_with_code(self) -> None:
        src = "a `code` and :code:`rest` here."
        out = self.conv(src)
        self.assertEqual(out, "\na ``code`` and :code:`rest` here.\n")

    def test_rest2_role_with_code(self) -> None:
        src = "a `code` and `rest`:code: here."
        out = self.conv(src)
        self.assertEqual(out, "\na ``code`` and `rest`:code: here.\n")

    def test_code_with_rest_role(self) -> None:
        src = "a :code:`rest` and `code` here."
        out = self.conv(src)
        self.assertEqual(out, "\na :code:`rest` and ``code`` here.\n")

    def test_code_with_rest_role2(self) -> None:
        src = "a `rest`:code: and `code` here."
        out = self.conv(src)
        self.assertEqual(out, "\na `rest`:code: and ``code`` here.\n")

    def test_rest_link_with_code(self) -> None:
        src = "a `RefLink <a>`_ and `code` here."
        out = self.conv(src)
        self.assertEqual(out, "\na `RefLink <a>`_ and ``code`` here.\n")

    def test_code_with_rest_link(self) -> None:
        src = "a `code` and `RefLink <a>`_ here."
        out = self.conv(src)
        self.assertEqual(out, "\na ``code`` and `RefLink <a>`_ here.\n")

    def test_inline_math(self) -> None:
        src = "this is `$E = mc^2$` inline math."
        out = self.conv(src)
        self.assertEqual(out, "\nthis is :math:`E = mc^2` inline math.\n")

    def test_inline_html(self) -> None:
        src = "this is <s>html</s>."
        out = self.conv(src)
        self.assertEqual(out, PROLOG + "\nthis is :raw-html-md:`<s>html</s>`.\n")

    def test_block_html(self) -> None:
        src = "<h1>title</h1>"
        out = self.conv(src)
        self.assertEqual(out, "\n\n.. raw:: html\n\n   <h1>title</h1>\n\n")


class TestBlockQuote(RendererTestBase):
    def test_block_quote(self) -> None:
        src = "> q1\n> q2"
        out = self.conv(src)
        self.assertEqual(out, "\n..\n\n   q1\n   q2\n\n")

    def test_block_quote_nested(self) -> None:
        src = "> q1\n> > q2"
        out = self.conv(src)
        # one extra empty line is inserted, but still valid rst anyway
        self.assertEqual(out, "\n..\n\n   q1\n\n   ..\n\n      q2\n\n")

    @skip("markdown does not support dedent in block quote")
    def test_block_quote_nested_2(self) -> None:
        src = "> q1\n> > q2\n> q3"
        out = self.conv(src)
        self.assertEqual(out, "\n..\n\n   q1\n\n   ..\n      q2\n\n   q3\n\n")


class TestCodeBlock(RendererTestBase):
    def test_plain_code_block(self) -> None:
        src = "\n".join(
            [
                "```",
                "pip install sphinx",
                "```",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n.. code-block::\n\n   pip install sphinx\n")

    def test_plain_code_block_tilda(self) -> None:
        src = "\n".join(
            [
                "~~~",
                "pip install sphinx",
                "~~~",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n.. code-block::\n\n   pip install sphinx\n")

    def test_code_block_math(self) -> None:
        src = "\n".join(
            [
                "```math",
                "E = mc^2",
                "```",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n.. math::\n\n   E = mc^2\n")

    def test_plain_code_block_indent(self) -> None:
        src = "\n".join(
            [
                "```",
                "pip install sphinx",
                "    new line",
                "```",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n.. code-block::\n\n   pip install sphinx\n       new line\n",
        )

    def test_python_code_block(self) -> None:
        src = "\n".join(
            [
                "```python",
                "print(1)",
                "```",
            ]
        )
        out = self.conv(src)
        self.assertEqual(out, "\n.. code-block:: python\n\n   print(1)\n")

    def test_python_code_block_indent(self) -> None:
        src = "\n".join(
            [
                "```python",
                "def a(i):",
                "    print(i)",
                "```",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n.. code-block:: python\n\n   def a(i):\n       print(i)\n",
        )


class TestImage(RendererTestBase):
    def test_image(self) -> None:
        src = "![alt text](a.png)"
        out = self.conv(src)
        # first and last newline is inserted by paragraph
        self.assertEqual(
            out,
            "\n\n.. image:: a.png\n   :target: a.png\n   :alt: alt text\n\n",
        )

    def test_image_title(self) -> None:
        src = '![alt text](a.png "title")'
        self.conv(src)
        # title is not supported now


class TestHeading(RendererTestBase):
    def test_heading(self) -> None:
        src = "# head 1"
        out = self.conv(src)
        self.assertEqual(out, "\nhead 1\n" + "=" * 6 + "\n")

    def test_heading_multibyte(self) -> None:
        src = "# マルチバイト文字\n"
        out = self.conv(src)
        self.assertEqual(out, "\nマルチバイト文字\n" + "=" * 16 + "\n")


class TestList(RendererTestBase):
    def test_ul(self) -> None:
        src = "* list"
        out = self.conv(src)
        self.assertEqual(out, "\n\n* list\n")

    def test_ol(self) -> None:
        src = "1. list"
        out = self.conv(src)
        self.assertEqual(out, "\n\n#. list\n")

    def test_nested_ul(self) -> None:
        src = "\n".join(
            [
                "* list 1",
                "* list 2",
                "  * list 2.1",
                "  * list 2.2",
                "* list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n\n* list 1\n"
            "* list 2\n\n"
            "  * list 2.1\n"
            "  * list 2.2\n\n"
            "* list 3\n",
        )

    def test_nested_ul_2(self) -> None:
        src = "\n".join(
            [
                "* list 1",
                "* list 2",
                "  * list 2.1",
                "  * list 2.2",
                "    * list 2.2.1",
                "    * list 2.2.2",
                "* list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n\n* list 1\n"
            "* list 2\n\n"
            "  * list 2.1\n"
            "  * list 2.2\n\n"
            "    * list 2.2.1\n"
            "    * list 2.2.2\n\n"
            "* list 3\n",
        )

    def test_nested_ol(self) -> None:
        src = "\n".join(
            [
                "1. list 1",
                "1. list 2",
                "    1. list 2.1",
                "    1. list 2.2",
                "1. list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n\n#. list 1\n"
            "#. list 2\n"
            "\n"
            "   #. list 2.1\n"
            "   #. list 2.2\n"
            "\n"
            "#. list 3\n",
        )

    def test_nested_ol_2(self) -> None:
        src = "\n".join(
            [
                "1. list 1",
                "1. list 2",
                "    1. list 2.1",
                "    1. list 2.2",
                "        1. list 2.2.1",
                "        1. list 2.2.2",
                "1. list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "\n\n#. list 1",
                    "#. list 2",
                    "",
                    "   #. list 2.1",
                    "   #. list 2.2",
                    "",
                    "      #. list 2.2.1",
                    "      #. list 2.2.2",
                    "",
                    "#. list 3\n",
                ]
            ),
        )

    def test_nested_mixed_1(self) -> None:
        src = "\n".join(
            [
                "1. list 1",
                "2. list 2",
                "   * list 2.1",
                "   * list 2.2",
                "     1. list 2.2.1",
                "     2. list 2.2.2",
                "7. list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "\n\n#. list 1",
                    "#. list 2",
                    "",
                    "   * list 2.1",
                    "   * list 2.2",
                    "",
                    "     #. list 2.2.1",
                    "     #. list 2.2.2",
                    "",
                    "#. list 3\n",
                ]
            ),
        )

    def test_nested_multiline_1(self) -> None:
        src = "\n".join(
            [
                "* list 1",
                "  list 1 cont",
                "* list 2",
                "  list 2 cont",
                "  * list 2.1",
                "    list 2.1 cont",
                "  * list 2.2",
                "    list 2.2 cont",
                "    * list 2.2.1",
                "    * list 2.2.2",
                "* list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "\n",
                    "* list 1",
                    "  list 1 cont",
                    "* list 2",
                    "  list 2 cont",
                    "",
                    "  * list 2.1",
                    "    list 2.1 cont",
                    "  * list 2.2",
                    "    list 2.2 cont",
                    "",
                    "    * list 2.2.1",
                    "    * list 2.2.2",
                    "",
                    "* list 3\n",
                ]
            ),
        )

    def test_nested_multiline_2(self) -> None:
        src = "\n".join(
            [
                "1. list 1",
                "   list 1 cont",
                "1. list 2",
                "   list 2 cont",
                "   1. list 2.1",
                "      list 2.1 cont",
                "   1. list 2.2",
                "      list 2.2 cont",
                "      1. list 2.2.1",
                "      1. list 2.2.2",
                "1. list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "\n",
                    "#. list 1",
                    "   list 1 cont",
                    "#. list 2",
                    "   list 2 cont",
                    "",
                    "   #. list 2.1",
                    "      list 2.1 cont",
                    "   #. list 2.2",
                    "      list 2.2 cont",
                    "",
                    "      #. list 2.2.1",
                    "      #. list 2.2.2",
                    "",
                    "#. list 3\n",
                ]
            ),
        )

    def test_nested_multiline_3(self) -> None:
        src = "\n".join(
            [
                "1. list 1",
                "   list 1 cont",
                "1. list 2",
                "   list 2 cont",
                "   * list 2.1",
                "     list 2.1 cont",
                "   * list 2.2",
                "     list 2.2 cont",
                "     1. list 2.2.1",
                "     1. list 2.2.2",
                "1. list 3",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "\n",
                    "#. list 1",
                    "   list 1 cont",
                    "#. list 2",
                    "   list 2 cont",
                    "",
                    "   * list 2.1",
                    "     list 2.1 cont",
                    "   * list 2.2",
                    "     list 2.2 cont",
                    "",
                    "     #. list 2.2.1",
                    "     #. list 2.2.2",
                    "",
                    "#. list 3\n",
                ]
            ),
        )


class TestComplexText(RendererTestBase):
    def test_code(self) -> None:
        src = """
some sentence
```python
print(1)
```
some sentence

# title
```python
print(1)
```
---
end
"""
        self.conv(src)


class TestTable(RendererTestBase):
    def test_table(self) -> None:
        src = """h1 | h2 | h3\n--- | --- | ---\n1 | 2 | 3\n4 | 5 | 6"""
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "",
                    ".. list-table::",
                    "   :header-rows: 1",
                    "",
                    "   * - h1",
                    "     - h2",
                    "     - h3",
                    "   * - 1",
                    "     - 2",
                    "     - 3",
                    "   * - 4",
                    "     - 5",
                    "     - 6",
                    "",
                    "",
                ]
            ),
        )


class TestFootNote(RendererTestBase):
    def test_footnote(self) -> None:
        src = "\n".join(
            [
                "This is a[^1] footnote[^2] ref[^ref] with rst [#a]_.",
                "",
                "[^1]: note 1",
                "[^2]: note 2",
                "[^ref]: note ref",
                ".. [#a] note rst",
            ]
        )
        out = self.conv(src)
        self.assertEqual(
            out,
            "\n".join(
                [
                    "",
                    "This is a[#fn-1]_ "
                    "footnote[#fn-2]_ ref[#fn-REF]_ with rst [#a]_.",
                    "",
                    ".. [#a] note rst",  # one empty line inserted...
                    "",
                    ".. [#fn-1] note 1",
                    ".. [#fn-2] note 2",
                    ".. [#fn-REF] note ref",
                    "",
                ]
            ),
        )

    def test_sphinx_ref(self) -> None:
        src = "This is a sphinx [ref]_ global ref.\n\n.. [ref] ref text"
        out = self.conv(src)
        self.assertEqual(out, "\n" + src)


class TestDirective(RendererTestBase):
    def test_comment_oneline(self) -> None:
        src = ".. a"
        out = self.conv(src)
        self.assertEqual(out, "\n.. a")

    @skip("not sure why this should work")
    def test_comment_indented(self) -> None:
        src = "    .. a"
        out = self.conv(src)
        self.assertEqual(out, "\n    .. a")

    def test_comment_newline(self) -> None:
        src = "..\n\n   comment\n\nnewline"
        out = self.conv(src)
        self.assertEqual(out, "\n..\n\n   comment\n\nnewline\n")

    def test_comment_multiline(self) -> None:
        comment = (
            ".. this is comment.\n"
            "   this is also comment.\n"
            "\n"
            "\n"
            "    comment may include empty line.\n"
            "\n\n"
        )
        src = comment + "`eoc`"
        out = self.conv(src)
        self.assertEqual(out, "\n" + comment + "``eoc``\n")


class TestRestCode(RendererTestBase):
    def test_rest_code_block_empty(self) -> None:
        src = "\n\n::\n\n"
        out = self.conv(src)
        self.assertEqual(out, "\n\n")

    def test_eol_marker(self) -> None:
        src = "a::\n\n    code\n"
        out = self.conv(src)
        self.assertEqual(out, "\na:\n\n.. code-block::\n\n   code\n")

    def test_eol_marker_remove(self) -> None:
        src = "a ::\n\n    code\n"
        out = self.conv(src)
        self.assertEqual(out, "\na\n\n.. code-block::\n\n   code\n")
