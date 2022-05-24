# -*- coding: utf-8 -*-
"""Simple Markdown writer for reStructuredText.

See:

* https://daringfireball.net/projects/markdown/syntax
* https://guides.github.com/pdfs/markdown-cheatsheet-online.pdf

**********************
Copyright and Licenses
**********************

nb2plots
========

The nb2plots package, including all examples, code snippets and attached
documentation is covered by the 2-clause BSD license.

    Copyright (c) 2015-2018, Matthew Brett
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    1. Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
    IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

3rd party code and data
=======================

Some code distributed within the nb2plots sources was developed by other
projects. This code is distributed under their respective licenses that are
listed below.

Matplotlib plot extension
-------------------------

The ``nbplots`` module is an edited version of
``matplotlib/lib/matplotlib/sphinxext/plot_directive.py``.

Among the major changes are the following:

* rename of 'plot' directive to 'nbplot';
* rename of 'plot_*' configuration options to 'nbplot_*' equivalent;
* nbplot removes the option to point to Python script file rather than
  using the code in the directive;
* nbplot keeps the namespace across directives in the same page, by default;
* include-source is True by default;
* nbplot can include multiple "parts" that can be selected via the
  "render-parts" and "run-parts" options;
* do not use cached output when rebuilding page to avoid errors from stale
  output;
* fix bug including empty parens when ``nofigs`` not specified (also fixed
  upstream);
* empty ``setup_module`` to avoid breakage of nose doctests;
* fix of plot doctest.

The following license covers the plot directive code:

    LICENSE AGREEMENT FOR MATPLOTLIB 1.2.0
    --------------------------------------

    1. This LICENSE AGREEMENT is between John D. Hunter ("JDH"), and the
    Individual or Organization ("Licensee") accessing and otherwise using
    matplotlib software in source or binary form and its associated
    documentation.

    2. Subject to the terms and conditions of this License Agreement, JDH
    hereby grants Licensee a nonexclusive, royalty-free, world-wide license
    to reproduce, analyze, test, perform and/or display publicly, prepare
    derivative works, distribute, and otherwise use matplotlib 1.2.0
    alone or in any derivative version, provided, however, that JDH's
    License Agreement and JDH's notice of copyright, i.e., "Copyright (c)
    2002-2011 John D. Hunter; All Rights Reserved" are retained in
    matplotlib 1.2.0 alone or in any derivative version prepared by
    Licensee.

    3. In the event Licensee prepares a derivative work that is based on or
    incorporates matplotlib 1.2.0 or any part thereof, and wants to
    make the derivative work available to others as provided herein, then
    Licensee hereby agrees to include in any such work a brief summary of
    the changes made to matplotlib 1.2.0.

    4. JDH is making matplotlib 1.2.0 available to Licensee on an "AS
    IS" basis.  JDH MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
    IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, JDH MAKES NO AND
    DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
    FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB 1.2.0
    WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

    5. JDH SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF MATPLOTLIB
    1.2.0 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR
    LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING
    MATPLOTLIB 1.2.0, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF
    THE POSSIBILITY THEREOF.

    6. This License Agreement will automatically terminate upon a material
    breach of its terms and conditions.

    7. Nothing in this License Agreement shall be deemed to create any
    relationship of agency, partnership, or joint venture between JDH and
    Licensee.  This License Agreement does not grant permission to use JDH
    trademarks or trade name in a trademark sense to endorse or promote
    products or services of Licensee, or any third party.

    8. By copying, installing or otherwise using matplotlib 1.2.0,
    Licensee agrees to be bound by the terms and conditions of this License
    Agreement.

rst2md
------

The files nb2plots/doctree2md.py and scripts/rst2md derive from the
"markdown.py" and "rst2md.py" files from "rst2md" project by Chris Wrench:
https://github.com/cgwrench/rst2md

``rst2md`` has the following license:

     Copyright (c) 2012, C. G. Wrench <c.g.wrench@gmail.com>
     All rights reserved.

     Redistribution and use in source and binary forms, with or without
     modification, are permitted provided that the following conditions are
     met:

     1. Redistributions of source code must retain the above copyright notice,
        this list of conditions and the following disclaimer.
     2. Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.

     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
     IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
     THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
     PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
     CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
     EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
     PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
     PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
     LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
     NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
     SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import unicode_literals

import re
from textwrap import dedent
import posixpath

__docformat__ = 'reStructuredText'

from docutils import frontend, nodes, writers, languages
from collections import OrderedDict


class IndentLevel(object):
    """Class to hold text being written for a certain indentation level.

    For example, all text in list_elements need to be indented.  A list_element
    creates one of these indentation levels, and all text contained in the
    list_element gets written to this IndentLevel.  When we leave the
    list_element, we ``write`` the text with suitable prefixes to the next
    level down, which might be the base of the document (document body) or
    another indentation level, if this is - for example - a nested list.

    In most respects, IndentLevel behaves like a list.
    """
    def __init__(self, base, prefix, first_prefix=None):
        self.base = base  # The list to which we eventually write
        self.prefix = prefix  # Text prepended to lines
        # Text prepended to first list
        self.first_prefix = prefix if first_prefix is None else first_prefix
        # Our own list to which we append before doing a ``write``
        self.content = []


    def append(self, new):
        self.content.append(new)


    def __getitem__(self, index):
        return self.content[index]


    def __len__(self):
        return len(self.content)


    def __bool__(self):
        return len(self) != 0


    def write(self):
        """Add ``self.contents`` with current ``prefix`` and ``first_prefix``

        Add processed ``self.contents`` to ``self.base``.  The first line has
        ``first_prefix`` prepended, further lines have ``prefix`` prepended.

        Empty (all whitespace) lines get written as bare carriage returns, to
        avoid ugly extra whitespace.
        """
        string = ''.join(self.content)
        lines = string.splitlines(True)
        if len(lines) == 0:
            return
        texts = [self.first_prefix + lines[0]]
        for line in lines[1:]:
            if line.strip() == '':  # avoid prefix for empty lines
                texts.append('\n')
            else:
                texts.append(self.prefix + line)
        self.base.append(''.join(texts))


def _make_method(to_add):
    """Make a method that adds `to_add`

    We need this function so that `to_add` is a fresh and unique
    variable at the time the method is defined.
    """
    def method(self, node):
        self.add(to_add)

    return method


def add_pref_suff(pref_suff_map):
    """Decorator adds visit, depart methods for prefix/suffix pairs."""
    def dec(cls):
        # Need _make_method to ensure new variable picked up for each iteration
        # of the loop.  The defined method picks up this new variable in its
        # scope.
        for key, (prefix, suffix) in pref_suff_map.items():
            setattr(cls, 'visit_' + key, _make_method(prefix))
            setattr(cls, 'depart_' + key, _make_method(suffix))
        return cls

    return dec


def add_pass_thru(pass_thrus):
    """Decorator adds explicit pass-through visit and depart methods."""
    def meth(self, node):
        pass

    def dec(cls):
        for element_name in pass_thrus:
            for meth_prefix in ('visit_', 'depart_'):
                meth_name = meth_prefix + element_name
                if hasattr(cls, meth_name):
                    raise ValueError(
                        'method name {} already defined'.format(meth_name)
                    )
                setattr(cls, meth_name, meth)
        return cls

    return dec


# Characters that should be escaped in Markdown
ESCAPE_RE = re.compile(r'([\\*`])')

# Doctree elements for which Markdown element is <prefix><content><suffix>
PREF_SUFF_ELEMENTS = {
    'emphasis': ('*', '*'),  # Could also use ('_', '_')
    'strong': ('**', '**'),  # Could also use ('__', '__')
    'literal': ('`', '`'),
    'subscript': ('<sub>', '</sub>'),
    'superscript': ('<sup>', '</sup>'),
}

# Doctree elements explicitly passed through without extra markup
PASS_THRU_ELEMENTS = (
    'document',
    'container',
    'target',
    'inline',
    'definition_list',
    'definition_list_item',
    'term',
    'field_list',
    'field_list_item',
    'field',
    'field_name',
    'mpl_hint',
    'pending_xref',
    'compound',
    'line',
    'line_block',
)


@add_pass_thru(PASS_THRU_ELEMENTS)
@add_pref_suff(PREF_SUFF_ELEMENTS)
class Translator(nodes.NodeVisitor):

    std_indent = '    '


    def __init__(self, document, builder=None):
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)
        # Not-None here indicates Markdown should use HTTP for internal and
        # download links.
        self.markdown_http_base = (
            builder.markdown_http_base if builder else None
        )
        # Warn only once per writer about unsupported elements
        self._warned = set()
        # Lookup table to get section list from name
        self._lists = OrderedDict((('head', []), ('body', []), ('foot', [])))
        # Reset attributes modified by reading
        self.reset()
        # Attribute shortcuts
        self.head, self.body, self.foot = self._lists.values()


    def reset(self):
        """Initialize object for fresh read."""
        for part in self._lists.values():
            part[:] = []

        # Current section heading level during writing
        self.section_level = 0

        # FIFO list of list prefixes, while writing nested lists.  Each element
        # corresponds to one level of nesting.  Thus ['1. ', '1. ', '* '] would
        # occur when writing items of an unordered list, that is nested within
        # an ordered list, that in turn is nested in another ordered list.
        self.list_prefixes = []

        # FIFO list of indentation levels.  When we are writing a block of text
        # that should be indented, we create a new indentation level.  We only
        # write the text when we leave the indentation level, so we can insert
        # the correct prefix for every line.
        self.indent_levels = []

        # Flag indicating we are processing docinfo items
        self._in_docinfo = False

        # Flag for whether to escape characters
        self._escape_text = True


    def astext(self):
        """Return the final formatted document as a string."""
        parts = [''.join(lines).strip() for lines in self._lists.values()]
        parts = [part + '\n\n' for part in parts if part]
        return ''.join(parts).strip() + '\n'


    def ensure_eol(self):
        """Ensure the last line in current base is terminated by new line."""
        out = self.get_current_output()
        if out and out[-1] and out[-1][-1] != '\n':
            out.append('\n')


    def get_current_output(self, section='body'):
        """Get list or IndentLevel to which we are currently writing."""
        return (
            self.indent_levels[-1]
            if self.indent_levels else self._lists[section]
        )


    def add(self, string, section='body'):
        """Add `string` to `section` or current output.

        Parameters
        ----------
        string : str
            String to add to output document
        section : {'body', 'head', 'foot'}, optional
            Section of document that generated text should be appended to, if
            not already appending to an indent level.  If already appending to
            an indent level, method will ignore `section`.  Use
            :meth:`add_section` to append to a section unconditionally.
        """
        self.get_current_output(section).append(string)


    def add_section(self, string, section='body'):
        """Add `string` to `section` regardless of current output.

        Can be useful when forcing write to header or footer.

        Parameters
        ----------
        string : str
            String to add to output document
        section : {'body', 'head', 'foot'}, optional
            Section of document that generated text should be appended to.
        """
        self._lists[section].append(string)


    def start_level(self, prefix, first_prefix=None, section='body'):
        """Create a new IndentLevel with `prefix` and `first_prefix`"""
        base = (
            self.indent_levels[-1].content
            if self.indent_levels else self._lists[section]
        )
        level = IndentLevel(base, prefix, first_prefix)
        self.indent_levels.append(level)


    def finish_level(self):
        """Remove most recent IndentLevel and write contents."""
        level = self.indent_levels.pop()
        level.write()


    def escape_chars(self, txt):
        """Escape (some) characters with special meaning for Markdown."""
        return ESCAPE_RE.sub(r'\\\1', txt)


    def _refuri2http(self, node):
        """Parse reference URIs to a proper MDX file link."""
        # Replace 'refuri' in reference with HTTP address, if possible
        # None for no possible address
        this_doc = self.builder.current_docname
        url = node.get('refuri')
        optional_anchor = ""

        if not node.get('internal'):
            return url

        if url not in (None, ''):
            # strip off the end starting with '/#', e.g. 'ModelHub/modelhub.ModelHub/#modelhub.ModelHub'
            hash_index = url.rfind('/#')
            optional_anchor = url[hash_index+2:]
            url = url[0:hash_index]
            # strip off the first '../'
            url = url[3:]
            node['refuri'] = url

        # If HTTP page build URL known, make link relative to that.
        if not self.markdown_http_base:
            return node.get("refuri")
        if url in (None, ''):  # Reference to this doc
            url = self.builder.get_target_uri(this_doc)
        else:  # URL is relative to the current docname.
            this_dir = posixpath.dirname(this_doc)
            if this_dir:
                url = posixpath.normpath('{}/{}'.format(this_dir, url))
        # turn each link into a relative file link to the .mdx file
        # first strip any trailing slash, then add a '.mdx' extension
        if url[-1:] == '/':
            url = url[:-1]
        url = url + '.mdx'
        url = '{}/{}'.format(self.markdown_http_base, url)
        if 'refid' in node:
            url += '#' + node['refid']
        elif not 'optional_anchor' == "":
            # Sphinx references (by :ref: or :autosummary:) all generate anchors ('#myanchor') in the refuri.
            # No distinction is made between a useful anchor that points to a section and a redundant one.
            # One pattern exists: if the anchor is already part of the URL, it's nearly certainly redundant.
            # example: 'bach-api-reference' for URL '/modeling/bach/api-reference/index.mdx'
            # example: 'modelhub.Aggregate.frequency' for URL '/modeling/open-model-hub/models/Aggregate/modelhub.Aggregate.frequency.mdx'
            # So here we only add the anchor if it seems useful (not yet part of the URL).
            anchor_is_redundant = optional_anchor.replace("-", "/") in url or optional_anchor.startswith('./')
            if not anchor_is_redundant:
                url += '#' + optional_anchor

        return url


    def visit_Text(self, node):
        """Parses any text to escape (some) characters with special meaning for Markdown."""
        text = node.astext().replace('\r\n', '\n')
        if self._escape_text:
            text = self.escape_chars(text)
        self.add(text)


    def depart_Text(self, node):
        """Parses any text to escape (some) characters with special meaning for Markdown."""
        pass


    def visit_docinfo(self, node):
        """Container for document bibliographic or meta data, e.g. the title & copyright page of a book.
        https://docutils.sourceforge.io/docs/ref/doctree.html#docinfo"""
        self._in_docinfo = True


    def depart_docinfo(self, node):
        """Container for document bibliographic or meta data, e.g. the title & copyright page of a book.
        https://docutils.sourceforge.io/docs/ref/doctree.html#docinfo"""
        self._in_docinfo = False
        

    def process_docinfo_item(self, node):
        """Document bibliographic or meta data, e.g. the title & copyright page of a book.
        https://docutils.sourceforge.io/docs/ref/doctree.html#docinfo"""
        # called explicitly from methods in this class
        self.add_section('% {}\n'.format(node.astext()), section='head')
        raise nodes.SkipNode


    def visit_title(self, node):
        """The title of a document, section, sidebar, table, topic, or generic admonition:
        https://docutils.sourceforge.io/docs/ref/doctree.html#title"""
        self.add((self.section_level + 1) * '#' + ' ')


    def depart_title(self, node):
        """The title of a document, section, sidebar, table, topic, or generic admonition:
        https://docutils.sourceforge.io/docs/ref/doctree.html#title"""
        self.ensure_eol()
        self.add('\n')


    def visit_subtitle(self, node):
        """The subtitle of a document:
        https://docutils.sourceforge.io/docs/ref/doctree.html#subtitle"""
        self.add((self.section_level + 2) * '#' + ' ')


    # The subtitle of a document: https://docutils.sourceforge.io/docs/ref/doctree.html#subtitle
    depart_subtitle = depart_title


    def visit_paragraph(self, node):
        """Text and inline elements of a single paragraph.
        https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph"""
        pass


    def depart_paragraph(self, node):
        """Text and inline elements of a single paragraph.
        https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph"""
        self.ensure_eol()
        self.add('\n')


    # A paragraph that could be formatted more compactly; no further formatting"""
    visit_compact_paragraph = visit_paragraph


    # A paragraph that could be formatted more compactly; no further formatting"""
    depart_compact_paragraph = depart_paragraph


    def visit_section(self, node):
        """Main unit of hierarchy: https://docutils.sourceforge.io/docs/ref/doctree.html#section"""
        self.section_level += 1


    def depart_section(self, node):
        """Main unit of hierarchy: https://docutils.sourceforge.io/docs/ref/doctree.html#section"""
        self.section_level -= 1


    def visit_enumerated_list(self, node):
        """Contains list_item elements which are uniformly marked with enumerator labels:
        https://docutils.sourceforge.io/docs/ref/doctree.html#enumerated-list"""
        self.list_prefixes.append('1. ')


    def depart_enumerated_list(self, node):
        """Contains list_item elements which are uniformly marked with enumerator labels:
        https://docutils.sourceforge.io/docs/ref/doctree.html#enumerated-list"""
        self.list_prefixes.pop()


    def visit_bullet_list(self, node):
        """Contains list_item elements which are uniformly marked with bullets:
        https://docutils.sourceforge.io/docs/ref/doctree.html#bullet-list"""
        self.list_prefixes.append('* ')


    # Contains list_item elements which are uniformly marked with bullets:
    # https://docutils.sourceforge.io/docs/ref/doctree.html#bullet-list
    depart_bullet_list = depart_enumerated_list


    def visit_list_item(self, node):
        """Container for the elements of a (bulleted or enumerated) list item:
        https://docutils.sourceforge.io/docs/ref/doctree.html#list-item"""
        first_prefix = self.list_prefixes[-1]
        prefix = ' ' * len(first_prefix)
        self.start_level(prefix, first_prefix)


    def depart_list_item(self, node):
        """Container for the elements of a (bulleted or enumerated) list item:
        https://docutils.sourceforge.io/docs/ref/doctree.html#list-item"""
        self.finish_level()


    def visit_definition(self, node):
        """Container for the body elements used to define a term in a definition_list: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition"""
        self.add('\n\n')
        self.start_level('    ')


    def depart_definition(self, node):
        """Container for the body elements used to define a term in a definition_list: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition"""
        self.finish_level()


    # Container for the body of a field: https://docutils.sourceforge.io/docs/ref/doctree.html#field-body
    visit_field_body = visit_definition


    # Container for the body of a field: https://docutils.sourceforge.io/docs/ref/doctree.html#field-body
    depart_field_body = depart_definition


    def visit_substitution_definition(self, node):
        """Substition definition: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#substitution-definition"""
        # Drop substitution definitions - the doctree already contains the text
        # with substitutions applied.
        raise nodes.SkipNode


    def visit_transition(self, node):
        """A gap spanning one or more lines, with or without a type ornament such as a row of asterisks. 
        Transitions separate body elements and sections, dividing a section into untitled divisions.
        https://docutils.sourceforge.io/docs/ref/doctree.html#transition"""
        # Simply replace a transition by a horizontal rule.
        # Could use three or more '*', '_' or '-'.
        self.add('\n---\n\n')
        raise nodes.SkipNode


    def visit_download_reference(self, node):
        """Reference to a download."""
        # If not resolving internal links, or there is no filename specified, pass through.
        filename = node.get('filename')
        if None in (self.markdown_http_base, filename):
            return
        target_url = '{}/_downloads/{}'.format(
            self.markdown_http_base, filename
        )
        self.add('[{}]({})'.format(node.astext(), target_url))
        raise nodes.SkipNode


    def depart_download_reference(self, node):
        """Reference to a download."""
        pass


    def visit_only(self, node):
        """Include the content of the directive only if the expression is true.
        https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-only"""
        if node['expr'] == 'markdown':
            self.add(dedent(node.astext()) + '\n')
        raise nodes.SkipNode


    ################################################################################
    # Code


    def visit_literal_block(self, node):
        """Block of text where line breaks and whitespace are significant and must be preserved, e.g. code:
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal-block"""
        self._escape_text = False
        code_type = node['classes'][1] if 'code' in node['classes'] else ''
        if 'language' in node:
            code_type = node['language']
        self.add('```' + code_type + '\n')


    def depart_literal_block(self, node):
        """Block of text where line breaks and whitespace are significant and must be preserved, e.g. code:
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal-block"""
        self._escape_text = True
        self.ensure_eol()
        self.add('```\n\n')


    def visit_doctest_block(self, node):
        """Python-specific variant of literal_block:
        https://docutils.sourceforge.io/docs/ref/doctree.html#doctest-block"""
        self._escape_text = False
        self.add('```python\n')


    # Python-specific variant of literal_block:
    # https://docutils.sourceforge.io/docs/ref/doctree.html#doctest-block
    depart_doctest_block = depart_literal_block


    def visit_block_quote(self, node):
        """Quotations set off from the main text (standalone):
        https://docutils.sourceforge.io/docs/ref/doctree.html#block-quote"""
        self.start_level('> ')


    def depart_block_quote(self, node):
        """Quotations set off from the main text (standalone):
        https://docutils.sourceforge.io/docs/ref/doctree.html#block-quote"""
        self.finish_level()


    def visit_code_links(self, node):
        """Code links."""
        raise nodes.SkipNode


    ################################################################################
    # Math


    def visit_math_block(self, node):
        """A block of text in LaTeX math format that is typeset as mathematical notation (display formula). 
        https://docutils.sourceforge.io/docs/ref/doctree.html#math-block"""
        self._escape_text = False
        self.add('$$\n')


    def depart_math_block(self, node):
        """A block of text in LaTeX math format that is typeset as mathematical notation (display formula). 
        https://docutils.sourceforge.io/docs/ref/doctree.html#math-block"""
        self._escape_text = True
        self.ensure_eol()
        self.add('$$\n\n')


    def visit_displaymath(self, node):
        """Sphinx math blocks become displaymath."""
        self.add('$$\n{}\n$$\n\n'.format(node['latex']))
        raise nodes.SkipNode


    def visit_math(self, node):
        """Text in LaTeX math format that is typeset as mathematical notation (inline formula).
        https://docutils.sourceforge.io/docs/ref/doctree.html#math"""
        # sphinx math node has 'latex' attribute, docutils does not
        if 'latex' in node:  # sphinx math node
            self.add('${}$'.format(node['latex']))
            raise nodes.SkipNode
        # docutils math node
        self._escape_text = False
        self.add('$')


    def depart_math(self, node):
        """Text in LaTeX math format that is typeset as mathematical notation (inline formula).
        https://docutils.sourceforge.io/docs/ref/doctree.html#math"""
        # sphinx node skipped in visit, only docutils gets here
        self._escape_text = True
        self.add('$')


    ################################################################################
    # Nbplot
    #
    def visit_nbplot_container(self, node):
        """Nbplot container."""
        pass

    def depart_nbplot_container(self, node):
        """Nbplot container."""
        pass

    def visit_nbplot_epilogue(self, node):
        """Nbplot epoligue."""
        raise nodes.SkipNode


    def visit_nbplot_not_rendered(self, node):
        """Nbplot not rendered."""
        raise nodes.SkipNode


    ################################################################################
    # Unknown

    def visit_problematic(self, node):
        """Unknown: https://docutils.sourceforge.io/docs/ref/doctree.html#problematic."""
        self.add('\n\n```\n{}\n```\n\n'.format(node.astext()))
        raise nodes.SkipNode


    def visit_system_message(self, node):
        """Unknown: https://docutils.sourceforge.io/docs/ref/doctree.html#system-message."""
        if node['level'] < self.document.reporter.report_level:
            # Level is too low to display
            raise nodes.SkipNode
        line = ', line %s' % node['line'] if node.hasattr('line') else ''
        self.add(
            '```\nSystem Message: {}:{}\n\n{}\n```\n\n'.format(
                node['source'], line, node.astext()
            )
        )
        raise nodes.SkipNode


    def visit_index(self, node):
        """Unknown: Index."""
        # Drop index entries
        raise nodes.SkipNode


    def visit_runrole_reference(self, node):
        """Unknown: runrole reference."""
        raise nodes.SkipNode
        

    def unknown_visit(self, node):
        """Warn once per instance for unsupported nodes.

        Intercept docinfo items if in docinfo block.
        """
        if self._in_docinfo:
            self.process_docinfo_item(node)
            return
        # We really don't know this node type, warn once per node type
        node_type = node.__class__.__name__
        if node_type not in self._warned:
            self.document.reporter.warning(
                'The ' + node_type + ' element not yet supported in Markdown.'
            )
            self._warned.add(node_type)
        raise nodes.SkipNode


class Writer(writers.Writer):
    """Sphinx Markdown writer."""

    supported = ('markdown', )
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    # Add configuration settings for additional Markdown flavours here.
    settings_spec = (
        'Markdown-Specific Options', None, (
            (
                'Extended Markdown syntax.', ['--extended-markdown'], {
                    'default': 0,
                    'action': 'store_true',
                    'validator': frontend.validate_boolean
                }
            ),
            (
                'Strict Markdown syntax. Default: true', ['--strict-markdown'],
                {
                    'default': 1,
                    'action': 'store_true',
                    'validator': frontend.validate_boolean
                }
            ),
        )
    )

    translator_class = Translator

    def __init__(self, builder=None):
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = self.builder.create_translator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
