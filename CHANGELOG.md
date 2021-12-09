sphinx-mdinclude
================

v0.3.1
------

* Fix argparse for python3.10

```
$ git shortlog -s v0.3.0...v0.3.1
     1	Bas Nijholt
    13	CrossNox
     1	Daniel Caballero
     1	illes
     1	kalvdans
```


v0.3.0
------

* Add support for mermaid code
* Change bump for bump2version

```
$ git shortlog -s v0.2.8...v0.3.0
     1	CrossNox
```


v0.2.8
------

* Fix bug that made multiple inline mathematical expressions fail to render

```
$ git shortlog -s v0.2.5...v0.2.8
     1	CrossNox
```


v0.2.7
------

* Add official python3.9 support
* Fix classifiers

```
$ git shortlog -s v0.2.6...v0.2.7
     2	CrossNox
```


v0.2.6
------

* Fix error for Sphinx3.3.0

```
$ git shortlog -s v0.2.5...v0.2.6
     1	Bas Nijholt
     1	CrossNox
     1	Daniel Caballero
```


v0.2.5
------

* Update repo name in every reference

```
$ git shortlog -s v0.2.4...v0.2.5
     1	CrossNox
```


v0.2.4
------

* Central versioning
* Add bump

```
$ git shortlog -s v0.2.3...v0.2.4
     4	CrossNox
```


v0.2.3
------

* Fix https://github.com/miyakogi/m2r/issues/51
* Change `tox` for `nox`
* Add `pre-commit` hooks and fix styling

```
$ git shortlog -s v0.2.1...v0.2.3
     9	CrossNox
```


v0.2.1
------

* Add `--disable-inline-math` and `m2r_disable_inline_math` sphinx option

```
$ git shortlog -s v0.2.0...v0.2.1
     3	Morgan Willcock
     1	kyluca
     9	miyakogi
```


v0.2.0
------

* Add `start-line` and `end-line` option to `mdinclude` directive
* Add `anonymous_references` option ([#26](https://github.com/miyakogi/m2r/pull/26))

```
$ git shortlog -s v0.1.15...v0.2.0
     3	Jake VanderPlas
    11	miyakogi
```


v0.1.15
-------

* Support Sphinx's doc/ref directives for relative links ([#16](https://github.com/miyakogi/m2r/pull/16))

```
$ git shortlog -s v0.1.14...v0.1.15
     9	Ryan Lane
     7	miyakogi
```


v0.1.14
-------

* Implement markdown link with title

```
$ git shortlog -s v0.1.13...v0.1.14
    11	miyakogi
```


v0.1.13
-------

* Catch up sphinx updates

```
$ git shortlog -s v0.1.12...v0.1.13
     8	miyakogi
```


v0.1.12
-------

* Support multi byte characters for heading

```
$ git shortlog -s v0.1.11...v0.1.12
     6	miyakogi
```


v0.1.11
-------

* Add metadata for sphinx
* Add `convert(src)` function, which is shortcut of `m2r.M2R()(src)`

```
$ git shortlog -s v0.1.10...v0.1.11
    13	miyakogi
```


v0.1.10
-------

* Include CHANGES and test files in source distribution

```
$ git shortlog -s v0.1.9...v0.1.10
     4	miyakogi
```


v0.1.9
------

* Print help when input_file is not specified on command-line

```
$ git shortlog -s v0.1.8...v0.1.9
     5	miyakogi
```


v0.1.8
------

* Update metadata on setup.py

```
$ git shortlog -s v0.1.7...v0.1.8
     6	miyakogi
```


v0.1.7
------

* Fix undefined name error (PR #5).

```
$ git shortlog -s v0.1.6...v0.1.7
     1	Kai Fricke
     1	cclauss
     9	miyakogi
```


v0.1.6
------

* Drop python 3.3 support
* Improve image_link regex (PR #3)

```
$ git shortlog -s v0.1.5...v0.1.6
     1	John W. O'Brien
     1	Nikola Forró
     6	miyakogi
```


v0.1.5
------

* Support multiple backticks in inline code, like: ```backticks (``) in code```

```
$ git shortlog -s v0.1.4...v0.1.5
     6	miyakogi
```


v0.1.4
------

* Support indented directives/reST-comments
* Support role-name after backticks (`` `text`:role: style``)

```
$ git shortlog -s v0.1.3...v0.1.4
     6	miyakogi
```


v0.1.3
------

* Remove extra escaped-spaces ('\ ')
    * before and after normal spaces
    * at the beginning of lines
    * before dots

```
$ git shortlog -s v0.1.2...v0.1.3
     4	miyakogi
```


v0.1.2
------

* Add reST's `::` marker support
* Add options to disable emphasis by underscore (`_` or `__`)

```
$ git shortlog -s v0.1.1...v0.1.2
     9	miyakogi
```


v0.1.1
------

* Fix Bug: when code or link is placed at the end of line, spaces to the next word is disappeared

```
$ git shortlog -s v0.1...v0.1.1
     6	miyakogi
```


v0.1
----

First public release.

```
$ git shortlog -s v0.1
    40	miyakogi
```


