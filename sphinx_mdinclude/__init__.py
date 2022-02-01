#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown extension for Sphinx
"""

__author__ = "Hiroyuki Takagi <miyako.dev@gmail.com>"
from .__version__ import __version__

from .legacy import convert
from .sphinx import setup
