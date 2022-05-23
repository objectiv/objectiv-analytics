"""Add external links to module code in Python object descriptions.

  Near copy of https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/linkcode.py 
  Adjustments made to .mdx files for Docusaurus.

"""

from typing import Any, Dict, Set

from docutils import nodes
from docutils.nodes import Node

import sphinx
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.locale import _


class LinkcodeError(SphinxError):
    category = "linkcode error"


def doctree_read(app: Sphinx, doctree: Node) -> None:
    env = app.builder.env

    resolve_target = getattr(env.config, 'linkcode_resolve', None)
    if not callable(env.config.linkcode_resolve):
        raise LinkcodeError(
            "Function `linkcode_resolve` is not given in conf.py")

    domain_keys = {
        'py': ['module', 'fullname'],
        'c': ['names'],
        'cpp': ['names'],
        'js': ['object', 'fullname'],
    }

    for objnode in list(doctree.findall(addnodes.desc)):
        domain = objnode.get('domain')
        uris: Set[str] = set()
        for signature_node in objnode:
            if not isinstance(signature_node, addnodes.desc_signature):
                continue

            # Convert signature_node to a specified format
            info = {}
            for key in domain_keys.get(domain, []):
                value = signature_node.get(key)
                if not value:
                    value = ''
                info[key] = value
            if not info:
                continue

            # Call user code to resolve the link
            uri = resolve_target(domain, info)
            if not uri:
                # no source
                continue

            if uri in uris or not uri:
                # only one link per name, please
                continue
            uris.add(uri)

            ##################################################################################
            # Only changes below
            reference = nodes.reference(internal=False, refuri=uri, classes=['viewcode-link'])
            reference += nodes.inline(text='[source]')
            onlynode = addnodes.only(expr='docusaurus')
            onlynode += reference
            signature_node.replace_self([signature_node, onlynode]) 
            ##################################################################################


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('doctree-read', doctree_read)
    app.add_config_value('linkcode_resolve', None, '')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
