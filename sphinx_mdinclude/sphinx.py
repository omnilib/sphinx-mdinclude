"""
Sphinx extension
"""

import os
import os.path

from docutils import io, nodes, statemachine, utils
from docutils.core import ErrorString
from docutils.parsers import rst
from docutils.utils import SafeString

from .__version__ import __version__
from .legacy import Converter


class MdIncludeParser(rst.Parser, object):
    # Explicitly tell supported formats to sphinx
    supported = ("markdown", "md", "mkd")

    def parse(self, inputstrings, document):
        if isinstance(inputstrings, statemachine.StringList):
            inputstring = "\n".join(inputstrings)
        else:
            inputstring = inputstrings
        config = document.settings.env.config
        converter = Converter(
            no_underscore_emphasis=config.no_underscore_emphasis,
            parse_relative_links=config.md_parse_relative_links,
            anonymous_references=config.md_anonymous_references,
            disable_inline_math=config.md_disable_inline_math,
        )
        super().parse(converter(inputstring), document)


class MdInclude(rst.Directive):
    """Directive class to include markdown in sphinx.

    Load a file and convert it to rst and insert as a node. Currently
    directive-specific options are not implemented.
    """

    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "start-line": int,
        "end-line": int,
    }

    def run(self):
        """Most of this method is from ``docutils.parser.rst.Directive``.

        docutils version: 0.12
        """
        if not self.state.document.settings.file_insertion_enabled:
            raise self.warning('"%s" directive disabled.' % self.name)
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1
        )
        source_dir = os.path.dirname(os.path.abspath(source))
        path = rst.directives.path(self.arguments[0])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        path = nodes.reprunicode(path)

        # get options (currently not use directive-specific options)
        encoding = self.options.get(
            "encoding", self.state.document.settings.input_encoding
        )
        e_handler = self.state.document.settings.input_encoding_error_handler
        tab_width = self.options.get(
            "tab-width", self.state.document.settings.tab_width
        )

        # open the including file
        try:
            self.state.document.settings.record_dependencies.add(path)
            include_file = io.FileInput(
                source_path=path, encoding=encoding, error_handler=e_handler
            )
        except UnicodeEncodeError:
            raise self.severe(
                'Problems with "%s" directive path:\n'
                'Cannot encode input file path "%s" '
                "(wrong locale?)." % (self.name, SafeString(path))
            )
        except IOError as error:
            raise self.severe(
                'Problems with "%s" directive path:\n%s.'
                % (self.name, ErrorString(error))
            )

        # read from the file
        startline = self.options.get("start-line", None)
        endline = self.options.get("end-line", None)
        try:
            if startline or (endline is not None):
                lines = include_file.readlines()
                rawtext = "".join(lines[startline:endline])
            else:
                rawtext = include_file.read()
        except UnicodeError as error:
            raise self.severe(
                'Problem with "%s" directive:\n%s' % (self.name, ErrorString(error))
            )

        config = self.state.document.settings.env.config
        converter = Converter(
            no_underscore_emphasis=config.no_underscore_emphasis,
            parse_relative_links=config.md_parse_relative_links,
            anonymous_references=config.md_anonymous_references,
            disable_inline_math=config.md_disable_inline_math,
        )
        include_lines = statemachine.string2lines(
            converter(rawtext), tab_width, convert_whitespace=True
        )
        self.state_machine.insert_input(include_lines, path)
        return []


def setup(app):
    """When used for sphinx extension."""
    app.add_config_value("no_underscore_emphasis", False, "env")
    app.add_config_value("md_parse_relative_links", False, "env")
    app.add_config_value("md_anonymous_references", False, "env")
    app.add_config_value("md_disable_inline_math", False, "env")
    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MdIncludeParser)
    app.add_directive("mdinclude", MdInclude)
    metadata = dict(
        version=__version__,
        parallel_read_safe=True,
        parallel_write_safe=True,
    )
    return metadata
