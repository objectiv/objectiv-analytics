# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import doctest
import os
import sys
import inspect

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.append(os.path.abspath("./_ext"))

project = 'Bach'
copyright = '2021, Objectiv'
author = 'Objectiv B.V.'

doctest_global_setup = f'''
from bach.dataframe import DataFrame
import pandas as pd
try:
    import os
    import sqlalchemy
    DB_PG_TEST_URL = os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
except Exception:
    engine = None
'''

doctest_default_flags = (
    doctest.DONT_ACCEPT_TRUE_FOR_1 | doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL | doctest.NORMALIZE_WHITESPACE
)

ipython_warning_is_error = False
ipython_execlines = [doctest_global_setup]

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',  # generate summaries based on docstrings
    'sphinx.ext.autosummary',  # auto generate autodoc directives
    'sphinx.ext.doctest',  # run examples /tests
    # 'sphinx.ext.intersphinx',       # generate links to external sphinx projects
    'numpydoc',  # use numpy style docs
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    'sphinx.ext.autosectionlabel',
    'sphinx_docusaurus_builder',
    'linkcode',  # generate [source] links to GH
]
#
# intersphinx_mapping = {
#     "dateutil": ("https://dateutil.readthedocs.io/en/latest/", None),
#     "matplotlib": ("https://matplotlib.org/stable/", None),
#     "numpy": ("https://numpy.org/doc/stable/", None),
#     "pandas-gbq": ("https://pandas-gbq.readthedocs.io/en/latest/", None),
#     "pandas": ("https://pandas.pydata.org/docs/", None),
#     "py": ("https://pylib.readthedocs.io/en/latest/", None),
#     "python": ("https://docs.python.org/3/", None),
#     "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
#     "statsmodels": ("https://www.statsmodels.org/devel/", None),
#     "pyarrow": ("https://arrow.apache.org/docs/", None),
# }

# autosummary / autodoc
autosummary_generate = True
autosummary_imported_members = True
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

autoclass_content = 'class'

# TOTALLY breaks toctree generation autodoc_class_signature = 'separated'

# automatically create explicit targets for sections
autosectionlabel_prefix_document = True

# numpydoc
numpydoc_attributes_as_param_list = False
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# resolve URL to GitHub
# part of this code is inspired by https://github.com/pandas-dev/pandas/blob/master/doc/source/conf.py
def linkcode_resolve(domain, info):

    # only handle python files
    if domain != 'py':
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None

    # get filename that contains the code
    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        return None

    # try to determine on what line number the code occurs
    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        lineno = None

    # create linespec so GH can highlight the correct lines
    if lineno:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    # get root of repository
    # we take this file as base: bach/docs/source/conf.py
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    # fn contains the full, absolute local path, so we strip the path to the root of the repo from that
    # to determine the path to the file, relative to the repo's root
    filename = fn[len(root):]

    # NOTE: leaving {linespec} out of the URL for now

    return f"https://github.com/objectiv/objectiv-analytics/blob/main{filename}"


def remove_copyright_string(app, what, name, obj, options, lines):
    if len(lines) > 0 and lines[0] == 'Copyright 2021 Objectiv B.V.':
        del lines[0]


def repair_classmethod_docstring(app, what, name, obj, options, lines):
    # If a property is annotated as a classmethod, there is confusion. Resolve that here
    if isinstance(obj, property) and isinstance(obj.fget, classmethod):
        lines.clear()
        obj_lines = obj.fget.__func__.__doc__
        if obj_lines:
            lines.extend(obj_lines.split("\n"))


def autodoc_skip_member_bach_internal(app, what, name, obj, skip, options):
    # Skip some private API methods & attributes & properties

    # Skip all attributes all together, if they're part of the public interface, they should be properties
    if what == 'attribute':
        return True

    inspect_obj = obj
    # If a property is annotated as a classmethod, there is confusion. Resolve that here
    if isinstance(obj, property) and isinstance(obj.fget, classmethod):
        inspect_obj = obj.fget.__func__

    # Traverse parent class hierarchy to get the topmost implementation with a non-empty docstring
    # This will disregard the type of the member, but that's actually okay, as long as
    klass = getattr(inspect_obj, '__self__', None)
    while not inspect_obj.__doc__ and klass and hasattr(klass, '__base__'):
        klass = klass.__base__
        # Is our method in this base class?
        if inspect_obj.__name__ in getattr(klass, '__dict__', {}):
            # Get the method
            inspect_obj = klass.__dict__[inspect_obj.__name__]
            # Do clean up the object if it's a property accessor or classmethod.
            if isinstance(obj, property):
                inspect_obj = obj.fget
            if isinstance(inspect_obj, classmethod):
                inspect_obj = inspect_obj.__func__

    # We get no options from autosummary whatsoever, so to implement this here:
    # if not autodoc_default_options.get('undoc-members', False) and not inspect_obj.__doc__:
    #     return True

    # We skip all methods with a docstring starting with INTERNAL
    if inspect_obj.__doc__ and inspect_obj.__doc__.strip().startswith('INTERNAL'):
        return True

    return None


def setup(app):
    app.connect("autodoc-process-docstring", remove_copyright_string)
    app.connect("autodoc-process-docstring", repair_classmethod_docstring)
    app.connect("autodoc-skip-member", autodoc_skip_member_bach_internal)
