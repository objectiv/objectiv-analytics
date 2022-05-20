"""
Copyright 2022 Objectiv B.V.
"""
from os import path
from codecs import open
from setuptools import setup
from .docusaurus_builder import DocusaurusBuilder

here = path.abspath(path.dirname(__file__))

# use README.md to set a long description for the extension
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# required libraries (https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/)
install_requires = list()
with open(path.join(here, 'requirements.txt'), 'r', encoding='utf-8') as f:
    for line in f.readlines():
        install_requires.append(line)


def setup(app):
    """
    Configure a new builder, writing to Docusaurus-compatible .mdx files.

    :param app: Sphinx instance: 
        https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx
    :returns: dict with metadata specifying version and whether parallel reading/writing can be used
    https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata

    """
    
    # Register a new builder class
    app.add_builder(DocusaurusBuilder)

    return {
        'version': '0.0.1', # identifies the extension version
        'parallel_read_safe': True, # whether parallel reading of source files can be used
        'parallel_write_safe': True, # whether parallel writing of output files can be used
    }
