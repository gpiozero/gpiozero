#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
import setup as _setup

# Mock out certain modules while building documentation
class Mock(object):
    __all__ = []

    def __init__(self, *args, **kw):
        pass

    def __call__(self, *args, **kw):
        return Mock()

    def __mul__(self, other):
        return Mock()

    def __and__(self, other):
        return Mock()

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        else:
            return Mock()

sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = sys.modules['RPi'].GPIO
sys.modules['RPIO'] = Mock()
sys.modules['RPIO.PWM'] = sys.modules['RPIO'].PWM
sys.modules['pigpio'] = Mock()
sys.modules['w1thermsensor'] = Mock()
sys.modules['spidev'] = Mock()

# -- General configuration ------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.intersphinx']
templates_path = ['_templates']
source_suffix = '.rst'
#source_encoding = 'utf-8-sig'
master_doc = 'index'
project = _setup.__project__.title()
copyright = '2015 %s' % _setup.__author__
version = _setup.__version__
release = _setup.__version__
#language = None
#today_fmt = '%B %d, %Y'
exclude_patterns = ['_build']
#default_role = None
#add_function_parentheses = True
#add_module_names = True
#show_authors = False
pygments_style = 'sphinx'
#modindex_common_prefix = []
#keep_warnings = False

# -- Autodoc configuration ------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Intersphinx configuration --------------------------------------------

intersphinx_mapping = {
    'python': ('http://docs.python.org/3.4', None),
    }

# -- Options for HTML output ----------------------------------------------

if on_rtd:
    html_theme = 'sphinx_rtd_theme'
    #html_theme_options = {}
    #html_sidebars = {}
else:
    html_theme = 'default'
    #html_theme_options = {}
    #html_sidebars = {}
#html_theme_path = []
#html_title = None
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
htmlhelp_basename = '%sdoc' % _setup.__project__

# Hack to make wide tables work properly in RTD
# See https://github.com/snide/sphinx_rtd_theme/issues/117 for details
#def setup(app):
#    app.add_stylesheet('style_override.css')

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    #'preamble': '',
}

latex_documents = [
    (
        'index',                       # source start file
        '%s.tex' % _setup.__project__, # target filename
        '%s Documentation' % project,  # title
        _setup.__author__,             # author
        'manual',                      # documentclass
        ),
]

#latex_logo = None
#latex_use_parts = False
#latex_show_pagerefs = False
#latex_show_urls = False
#latex_appendices = []
#latex_domain_indices = True

# -- Options for manual page output ---------------------------------------

man_pages = []

#man_show_urls = False

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = []

#texinfo_appendices = []
#texinfo_domain_indices = True
#texinfo_show_urls = 'footnote'
#texinfo_no_detailmenu = False
