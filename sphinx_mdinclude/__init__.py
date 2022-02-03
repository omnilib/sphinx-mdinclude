#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown extension for Sphinx
"""

__author__ = "Hiroyuki Takagi <miyako.dev@gmail.com>"
from .__version__ import __version__

from .render import convert, RestMarkdown
from .sphinx import setup

__all__ = [
    "convert",
    "RestMarkdown",
    "setup",
]
