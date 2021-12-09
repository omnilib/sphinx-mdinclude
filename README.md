sphinx-mdinclude
================

Sphinx extension for including or writing pages in Markdown format.

[![version](https://img.shields.io/pypi/v/sphinx-mdinclude.svg)](https://pypi.python.org/pypi/sphinx-mdinclude)
[![documentation](https://img.shields.io/badge/docs-latest-success)](https://sphinx-mdinclude.readthedocs.io)
[![changelog](https://img.shields.io/badge/change-log-blue)](https://sphinx-mdinclude.readthedocs.io)
[![license](https://img.shields.io/pypi/l/sphinx-mdinclude.svg)](https://github.com/jreese/sphinx-mdinclude/blob/main/LICENSE)


sphinx-mdinclude is a simple Sphinx extension that enables including Markdown documents
from within reStructuredText. It provides the `.. mdinclude::` directive, and
automatically converts the content of Markdown documents to reStructuredText format.

sphinx-mdinclude is a fork of [m2r](https://github.com/miyakogi/m2r) and
[m2r2](https://github.com/crossnox/m2r2), focused only on providing a Sphinx extension.

## Features

* Basic markdown and some extensions (see below)
    * inline/block-level raw html
    * fenced-code block
    * tables
    * footnotes (``[^1]``)
* Inline- and Block-level rst markups
    * single- and multi-line directives (`.. directive::`)
    * inline-roles (``:code:`print(1)` ...``)
    * ref-link (``see `ref`_``)
    * footnotes (``[#fn]_``)
    * math extension inspired by [recommonmark](https://recommonmark.readthedocs.io/en/latest/index.html)
* Sphinx extension
    * add markdown support for sphinx
    * ``mdinclude`` directive to include markdown from md or rst files
    * option to parse relative links into ref and doc directives (``m2r_parse_relative_links``)
    * option to render ``mermaid`` blocks as graphs with [sphinxcontrib.mermaid](https://sphinxcontrib-mermaid-demo.readthedocs.io/en/latest/index.html`) (``m2r_use_mermaid``, default: auto)
      * auto means that m2r2 will check if `sphinxcontrib.mermaid` has been added to the extensions list

## Restrictions

* In the rst's directives, markdown is not available. Please write in rst.
* Column alignment of tables is not supported. (rst does not support this feature)
* Heading with overline-and-underline is not supported.
  * Heading with underline is OK
* Rst heading marks are currently hard-coded and unchangeable.
  * H1: `=`, H2: `-`, H3: `^`, H4: `~`, H5: `"`, H6: `#`

## Installation

Python 3.6 or newer is required.

```
pip install sphinx-mdinclude
```

## Usage

In your Sphinx `conf.py`, add the following lines:

```python
extensions = [
    ...,
    'sphinx_mdinclude',
]
```

Markdown files with the `.md` extension will be loaded and used by Sphinx, similar to
any other `.rst` files.

To include Markdown files within other files, use the `.. mdinclude:: <filename>`
directive. This applies the conversion from Markdown to reStructuredText format.

## License

`sphinx-mdinclude` is copyright Hiroyuki Takagi, CrossNox, and [John Reese][],
and licensed under the MIT license. I am providing code in this repository to you
under an open source license. This is my personal repository; the license you receive
to my code is from me and not from my employer. See the [LICENSE][] file for details.

[John Reese]: https://jreese.sh
[LICENSE]: https://github.com/jreese/sphinx-mdinclude/blob/main/LICENSE
