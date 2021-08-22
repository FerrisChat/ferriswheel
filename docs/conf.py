# type: ignore

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))


# -- Project information -----------------------------------------------------

project = 'FerrisWheel'
copyright = '2021 to present, Cryptex'
author = 'Cryptex'

# The full version, including alpha/beta/rc tags
release = '0.0.0'
with open('../ferris/__init__.py', 'r') as f:
    content = f.read()
    try:
        release = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)  # type: ignore
    except AttributeError:
        pass


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_search.extension',
    'attributetable',
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
autodoc_class_signature = 'separated'
autodoc_typehints = 'description'
autodoc_member_order = 'groupwise'

# Add any paths that contain templates here, relative to this directory.
templates_path = []

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |enum| replace:: This is an |enum_link|_.
.. |coroutine_link| replace:: *coroutine*
.. |enum_link| replace:: *enum*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
.. _enum_link: https://docs.python.org/3/library/enum.html#enum.Enum
"""

intersphinx_mapping = {
    'py': ('https://docs.python.org/3', None),
    'aio': ('https://docs.aiohttp.org/en/stable/', None),
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_static_path = ["_static"]
templates_path = ['_templates']

html_favicon = '_static/ferriswheel.svg'
html_logo = '_static/ferriswheel.svg'

html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

html_theme = 'sphinx_material'

html_title = 'FerrisWheel'
html_theme_options = {
    'nav_title': 'FerrisWheel',
    'base_url': 'https://ferriswheel.readthedocs.io/en/latest/',
    'repo_url': 'https://github.com/FerrisChat/ferriswheel',
    'theme_color': '#F74C00',
    'color_primary': 'orange',
    'color_accent': 'deep-orange',
    'repo_name': 'FerrisWheel',
    'touch_icon': '_static/ferriswheel.svg',
    'globaltoc_depth': 3,
    'globaltoc_collapse': False,
    'globaltoc_includehidden': False,
}

# html_theme_options = {
#     'site_url': 'https://ferriswheel.readthedocs.io/en/latest/',
#     'repo_url': 'https://github.com/FerrisChat/ferriswheel',
#     'theme_color': '#F74C00',
#     'color_primary': 'orange',
#     'color_accent': 'deep-orange',
#     'repo_name': 'FerrisWheel',
#     'logo_svg': '_static/ferriswheel.svg',
#     'icon': '_static/ferriswheel.svg',
#     'globaltoc_depth': 3,
#     'globaltoc_collapse': False,
#     'globaltoc_includehidden': False,
#     'palette': [
#         {
#             'media': '(prefers-color-scheme: dark)',
#             'scheme': 'slate',
#             'primary': 'orange',
#             'accent': 'deep orange',
#             'toggle': {
#                 'icon': 'material/lightbulb',
#                 'name': 'Switch to light mode'
#             }
#         },
#         {
#             'media': '(prefers-color-scheme: light)',
#             'scheme': 'default',
#             'primary': 'orange',
#             'accent': 'deep orange',
#             'toggle': {
#                 'icon': 'material/lightbulb-outline',
#                 'name': 'Switch to dark mode'
#                 }
#         }
#     ]
# }


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["./_static"]
