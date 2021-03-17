#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019-2020 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Thijs Triemstra <info@collab.nl>
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import os
from pathlib import Path
from datetime import datetime
from setuptools.config import read_configuration

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
config = read_configuration(str(Path(__file__).parent / '..' / 'setup.cfg'))
info = config['metadata']

# -- General configuration ------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.intersphinx']
if on_rtd:
    needs_sphinx = '1.4.0'
    extensions.append('sphinx.ext.imgmath')
    imgmath_image_format = 'svg'
    tags.add('rtd')
else:
    extensions.append('sphinx.ext.mathjax')
    mathjax_path = '/usr/share/javascript/mathjax/MathJax.js?config=TeX-AMS_HTML'

templates_path = ['_templates']
source_suffix = '.rst'
#source_encoding = 'utf-8-sig'
master_doc = 'index'
project = info['name']
copyright = '2015-{now:%Y} {info[author]}'.format(now=datetime.now(), info=info)
version = info['version']
#release = None
#language = None
#today_fmt = '%B %d, %Y'
exclude_patterns = ['_build']
highlight_language='python3'
#default_role = None
#add_function_parentheses = True
#add_module_names = True
#show_authors = False
pygments_style = 'sphinx'
#modindex_common_prefix = []
#keep_warnings = False

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
    'python': ('https://docs.python.org/3.7', None),
    'picamera': ('https://picamera.readthedocs.io/en/latest', None),
    'colorzero': ('https://colorzero.readthedocs.io/en/latest', None),
    }

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_title = '{info[name]} {info[version]} Documentation'.format(info=info)
#html_theme_path = []
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
#html_extra_path = []
#html_last_updated_fmt = '%b %d, %Y'
#html_use_smartypants = True
#html_additional_pages = {}
#html_domain_indices = True
#html_use_index = True
#html_split_index = False
#html_show_sourcelink = True
#html_show_sphinx = True
#html_show_copyright = True
#html_use_opensearch = ''
#html_file_suffix = None
htmlhelp_basename = '{info[name]}doc'.format(info=info)

# Hack to make wide tables work properly in RTD
# See https://github.com/snide/sphinx_rtd_theme/issues/117 for details
#def setup(app):
#    app.add_stylesheet('style_override.css')

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
        info['author'],     # author
        'manual',           # documentclass
        True,               # documents ref'd from toctree only
        ),
]

#latex_logo = None
#latex_use_parts = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'
#latex_appendices = []
#latex_domain_indices = True

# -- Options for epub output ----------------------------------------------

epub_basename = project
#epub_theme = 'epub'
#epub_title = html_title
epub_author = info['author']
epub_identifier = 'https://{info[name]}.readthedocs.io/'.format(info=info)
#epub_tocdepth = 3
epub_show_urls = 'no'
#epub_use_index = True

# -- Options for manual page output ---------------------------------------

man_pages = [
    ('cli_pinout',  'pinout',      'GPIO Zero pinout tool',       [info['author']], 1),
    ('remote_gpio', 'remote-gpio', 'GPIO Zero remote GPIO guide', [info['author']], 7),
]

man_show_urls = True

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = []

#texinfo_appendices = []
#texinfo_domain_indices = True
#texinfo_show_urls = 'footnote'
#texinfo_no_detailmenu = False
