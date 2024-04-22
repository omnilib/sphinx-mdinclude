# Copyright Amethyst Reese
# Licensed under the MIT License

import platform
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent

from docutils.frontend import get_default_settings
from docutils.parsers.rst import directives, Parser
from docutils.utils import new_document

from ..render import convert
from ..sphinx import MdInclude

TEST_MD = Path(__file__).parent / "test.md"
TEST_RST = Path(__file__).parent / "test.rst"


@dataclass
class FakeConfig:
    no_underscore_emphasis: bool = False
    md_parse_relative_links: bool = False
    md_anonymous_references: bool = False
    md_disable_inline_math: bool = False


@dataclass
class FakeEnv:
    config: FakeConfig = field(default_factory=FakeConfig)


class SmokeTest(unittest.TestCase):
    maxDiff = None

    @unittest.skipIf(
        platform.system() == "Windows",
        "inconsistent column widths on Windows",
    )
    def test_convert(self) -> None:
        content = TEST_MD.read_text()
        expected = TEST_RST.read_text()

        result = convert(content)
        self.assertEqual(expected, result)

    def test_mdinclude_basic(self) -> None:
        content = dedent(
            f"""
            .. mdinclude:: {TEST_MD}

            """
        )
        expected = dedent(
            """\
            <document source="smoke.rst">
                <section ids="title" names="title">
                    <title>
                        Title
                    <section ids="subtitle" names="subtitle">
                        <title>
                            SubTitle
                        <paragraph>
                            <strong>
                                content
            """
        )

        directives.register_directive("mdinclude", MdInclude)
        parser = Parser()
        settings = get_default_settings(Parser)
        settings.env = FakeEnv()
        document = new_document("smoke.rst", settings.copy())
        parser.parse(content, document)

        result = document.pformat()
        self.assertEqual(expected, result[: len(expected)])
