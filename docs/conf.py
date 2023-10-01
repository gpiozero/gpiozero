#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Thijs Triemstra <info@collab.nl>
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import os
import configparser
from pathlib import Path
from datetime import datetime
from setuptools.config import read_configuration

on_rtd = os.environ.get('READTHEDOCS', '').lower() == 'true'
config = configparser.ConfigParser()
config.read([Path(__file__).parent / '..' / 'setup.cfg'])
info = config['metadata']

# -- Project information -----------------------------------------------------

project = info['name']
author = info['author']
copyright = f'2015-{datetime.now():%Y} {author}'
release = info['version']
version = release

# -- General configuration ------------------------------------------------

needs_sphinx = '4.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.imgmath',
]
if on_rtd:
    tags.add('rtd')

root_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build']
highlight_language = 'python3'
pygments_style = 'sphinx'

# -- Autodoc configuration ------------------------------------------------

autodoc_member_order = 'groupwise'
autodoc_mock_imports = [
    'RPi',
    'lgpio',
    'RPIO',
    'pigpio',
    'w1thermsensor',
    'spidev',
    'colorzero',
]

# -- Intersphinx configuration --------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.9', None),
    'picamera': ('https://picamera.readthedocs.io/en/latest', None),
    'colorzero': ('https://colorzero.readthedocs.io/en/latest', None),
}

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_title = f'{project} {version} Documentation'
html_static_path = ['_static']
manpages_url = 'https://manpages.debian.org/bookworm/{page}.{section}.en.html'

# -- Options for LaTeX output ---------------------------------------------

latex_engine = 'xelatex'

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'preamble': r'\def\thempfootnote{\arabic{mpfootnote}}', # workaround sphinx issue #2530
}

latex_documents = [
    (
        'index',            # source start file
        project + '.tex',   # target filename
        html_title,         # title
        author,             # author
        'manual',           # documentclass
        True,               # documents ref'd from toctree only
    ),
]

latex_show_pagerefs = True
latex_show_urls = 'footnote'

# -- Options for epub output ----------------------------------------------

epub_basename = project
epub_author = author
epub_identifier = f'https://{info["name"]}.readthedocs.io/'
epub_show_urls = 'no'

# -- Options for manual page output ---------------------------------------

man_pages = [
    ('cli_pinout',  'pinout',      'GPIO Zero pinout tool',       [info['author']], 1),
    ('cli_pintest', 'pintest',     'GPIO Zero pintest tool',      [info['author']], 1),
    ('remote_gpio', 'remote-gpio', 'GPIO Zero remote GPIO guide', [info['author']], 7),
    ('cli_env',     'gpiozero-env', 'GPIO Zero environment vars', [info['author']], 7),
]

man_show_urls = True

# -- Options for linkcheck builder ----------------------------------------

linkcheck_retries = 3
linkcheck_workers = 20
linkcheck_anchors = True
