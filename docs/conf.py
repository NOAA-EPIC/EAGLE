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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "eagle"
copyright = "2025, eagle contributors"
author = "eagle contributors"

version = "v1.0.0"
release = "Public v1.0.0 Documentation"

numfig = True


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
]

intersphinx_mapping = {
    "uwtools": ("https://uwtools.readthedocs.io/en/stable/", None),
    "anemoi-inference": (
        "https://anemoi.readthedocs.io/projects/inference/en/latest/",
        None,
    ),
    "anemoi-training": (
        "https://anemoi.readthedocs.io/projects/training/en/latest/",
        None,
    ),
    "met": ("https://metplus.readthedocs.io/projects/met/en/latest/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
bibtex_bibfiles: list[str] = []
linkcheck_ignore: list[str] = []
# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "navigation_depth": 8,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css", "eagle_theme_overrides.css"]


# -- Options for EPUB output -------------------------------------------------

epub_show_urls = "footnote"


# -- Options for napoleon extension ------------------------------------------

napoleon_numpy_docstring = False
napoleon_google_docstring = True


# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

add_module_names = False
