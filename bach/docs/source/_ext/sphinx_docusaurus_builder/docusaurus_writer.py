from .depth import Depth
from .doctree2md import Translator, Writer
from docutils import nodes
from pydash import _
from munch import munchify
import os
import yaml
from sphinx.util.docutils import SphinxDirective, directives

frontmatter = {} # holds any frontmatter for the current doc

class DocusaurusTranslator(Translator):
    """Class to translate to Docusaurus-compatible MDX documentation from Sphinx.

    :param Translator: The top-level Sphinx Translator class.

    """
    depth = Depth() # class to keep track of depth in lists or sections
    enumerated_count = {}
    section_depth = 0
    title = None # document title
    visited_title = False # whether title was parsed yet
    current_desc_type = None # the current class/method/property/attribute being parsed (if any)
    parsed_desc_name = False  # whether already parsed a desc name (e.g. to not insert newlines for params)
    autosummary_shown = [] # holds for which class/method an autosummary has already been shown (if any)
    in_signature = False # whether currently processing a signature (e.g. to not insert newlines)
    in_table = False # whether currently processing a table (e.g. to not insert newlines)
    table_entries = []
    table_rows = []
    tables = []
    tbodys = []
    theads = []
    in_reference = False # whether currently processing a reference (e.g. to not insert emphasis or bold)


    def __init__(self, document, builder=None):
        """Instantiates the Translator.
        
        :param document: The document to translate.
        :param builder: The Sphinx Builder object that provides the document.

        """
        Translator.__init__(self, document, builder=builder)
        self.builder = builder
        self.frontmatter = frontmatter


    @property
    def rows(self):
        """Returns rows in a table in the document."""
        rows = []
        if not len(self.tables):
            return rows
        for node in self.tables[len(self.tables) - 1].children:
            if isinstance(node, nodes.row):
                rows.append(node)
            else:
                for subnode in node.children:
                    if isinstance(subnode, nodes.row):
                        rows.append(subnode)
        return rows


    def get_slug(self, docname, doc_frontmatter):
        """Parse the slug used in frontmatter, based on the config.

        :param docname: the current document name/path.
        :param doc_frontmatter: contents set via the frontmatter directive
        
        :returns: a formatted slug.

        """
        
        # any slug set via the frontmatter directive takes preference
        if doc_frontmatter and 'slug' in doc_frontmatter:
            return doc_frontmatter['slug']

        slug = docname

        # Format API reference slugs
        for api_pattern, config in self.builder.api_frontmatter.items():
            if docname.startswith(api_pattern):
                if 'slug_tree_levels' in config:
                    levels = config['slug_tree_levels']
                    # format the part after the last slash
                    index_last_part = docname.rfind('/') + 1
                    last_part = docname[index_last_part:]
                    parts = last_part.split('.')
                    last_part_formatted = '.'.join(parts[-levels:])
                    slug = docname[0:index_last_part] + last_part_formatted

        # add base path and trailing slash
        # TODO: make configurable instead of hardcoded
        slug = '/modeling/' + slug + '/'
        if docname == 'index' or docname[-6:] == "/index":
            # this is an index page, so should just end in '/'
            slug = slug[:-6]
        return slug


    def get_title(self, docname, doc_frontmatter):
        """Parse the title used in frontmatter, based on the config.

        :param docname: the current document name/path.
        :param doc_frontmatter: contents set via the frontmatter directive
        
        :returns: a formatted title.

        """
        
        # any title set via the frontmatter directive takes preference
        if doc_frontmatter and 'title' in doc_frontmatter:
            return doc_frontmatter['title']

        title = self.title
        for api_pattern, config in self.builder.api_frontmatter.items():
            if self.builder.current_docname.startswith(api_pattern):
                if 'title_tree_levels' in config:
                    levels = config['title_tree_levels']
                    parts = self.title.split('.')
                    title = '.'.join(parts[-levels:])
        
        return title


    ################################################################################
    # Parse the doctree: https://docutils.sourceforge.io/docs/ref/doctree.html
    #
    # +--------------------------------------------------------------------+
    # | document  [may begin with a title, subtitle, decoration, docinfo]  |
    # |                             +--------------------------------------+
    # |                             | sections  [each begins with a title] |
    # +-----------------------------+-------------------------+------------+
    # | [body elements:]                                      | (sections) |
    # |         | - literal | - lists  |       | - hyperlink  +------------+
    # |         |   blocks  | - tables |       |   targets    |
    # | para-   | - doctest | - block  | foot- | - sub. defs  |
    # | graphs  |   blocks  |   quotes | notes | - comments   |
    # +---------+-----------+----------+-------+--------------+
    # | [text]+ | [text]    | (body elements)  | [text]       |
    # | (inline +-----------+------------------+--------------+
    # | markup) |
    # +---------+


    def visit_document(self, node):
        """The root of the tree.
        https://docutils.sourceforge.io/docs/ref/doctree.html#document"""
        self.title = getattr(self.builder, 'current_docname')


    def depart_document(self, node):
        """The root of the tree.
        https://docutils.sourceforge.io/docs/ref/doctree.html#document"""

        # write the frontmatter after being done with the doc
        current_doc = self.builder.current_docname
        
        # Format API reference titles
        title = self.title
        for api_pattern, config in self.builder.api_frontmatter.items():
            if current_doc.startswith(api_pattern):
                if 'title_tree_levels' in config:
                    levels = config['title_tree_levels']
                    parts = self.title.split('.')
                    title = '.'.join(parts[-levels:])

        ctx = self.builder.ctx
        doc_frontmatter = self.frontmatter[current_doc] if current_doc in self.frontmatter else None
        variables = munchify({
            'id': _.snake_case(current_doc).replace('_', '-'),
            'title': self.get_title(current_doc, doc_frontmatter),
            'slug': self.get_slug(current_doc, doc_frontmatter),
        })
        if doc_frontmatter and 'position' in doc_frontmatter:
            variables['sidebar_position'] = int(doc_frontmatter['position'])
        variables_yaml = yaml.safe_dump(variables)
        frontmatter_content = '---\n' + variables_yaml + '---\n'
        self.add(frontmatter_content, section='head')

    
    def visit_title(self, node):
        """The title of a document, section, sidebar, table, topic, or generic admonition:
        https://docutils.sourceforge.io/docs/ref/doctree.html#title"""
        if not self.visited_title:
            self.title = node.astext()
            self.visited_title = True
        for x in range(0, self.section_depth):
            self.add('#')
        self.add(' ')


    def visit_raw(self, node):
        """Indicates non-reStructuredText data that is to be passed untouched to the Writer, so won't parse:
        https://docutils.sourceforge.io/docs/ref/doctree.html#raw"""
        self.descend('raw')


    def depart_raw(self, node):
        """Indicates non-reStructuredText data that is to be passed untouched to the Writer, so won't parse:
        https://docutils.sourceforge.io/docs/ref/doctree.html#raw"""
        self.ascend('raw')


    def visit_comment(self, node):
        """Internal comments that should not be shown in the output."""
        # comment blocks generally break the Markdown, so skip it
        raise nodes.SkipNode


    def depart_comment(self, node):
        """Internal comments that should not be shown in the output."""
        # comment blocks generally break the Markdown, so skip it
        raise nodes.SkipNode


    def visit_section(self, node):
        """Main unit of hierarchy: https://docutils.sourceforge.io/docs/ref/doctree.html#section"""
        self.section_depth += 1


    def depart_section(self, node):
        """Main unit of hierarchy: https://docutils.sourceforge.io/docs/ref/doctree.html#section"""
        self.section_depth -= 1

    
    def visit_target(self, node):
        if self.visited_title:
            if node.get('refid'):
                target_id = str(node.get('refid'))
                self.add('<div id="' + target_id + '" className="hidden-anchor"></div>\n\n')


    def depart_target(self, node):
        pass


    def visit_rubric(self, node):
        """An informal heading that doesn't correspond to the document's structure.
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric."""
        # We do parse it as a 3rd level heading though, because it's useful for a ToC on the right.
        self.add('### ')


    def depart_rubric(self, node):
        """An informal heading that doesn't correspond to the document's structure.
        http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric."""
        self.add('\n\n')


    def visit_versionmodified(self, node):
        """Deprecation and compatibility messages. Type will hold something like 'deprecated'"""
        print("Unchecked 'version' directive found in document " + self.builder.current_docname + ":", node) 
        self.add('**%s:** ' % node.attributes['type'].capitalize())


    def depart_versionmodified(self, node):
        """Deprecation and compatibility messages. Type will hold something like 'deprecated'"""
        pass


    def visit_inline(self, node):
        """Generic inline container: https://docutils.sourceforge.io/docs/ref/doctree.html#inline"""
        pass


    def depart_inline(self, node):
        """Generic inline container: https://docutils.sourceforge.io/docs/ref/doctree.html#inline"""
        pass


    def visit_paragraph(self, node):
        """Text and inline elements of a single paragraph.
        https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph"""
        pass


    def depart_paragraph(self, node):
        """Text and inline elements of a single paragraph.
        https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph"""
        # Do not add a newline if processing a table or a list item, because it will break the markup
        if not self.in_table:
            self.ensure_eol()
        if not self.in_table and self.depth.get('list') == 0:
            self.add('\n')


    # A paragraph that could be formatted more compactly; further formatting ignored here.
    # https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph
    visit_compact_paragraph = visit_paragraph


    # A paragraph that could be formatted more compactly; further formatting ignored here.
    # https://docutils.sourceforge.io/docs/ref/doctree.html#paragraph
    depart_compact_paragraph = depart_paragraph


    def visit_reference(self, node):
        """Any reference (aka link), whether external or internal:
        https://docutils.sourceforge.io/docs/ref/doctree.html#reference"""
        # Docusaurus doesn't support MDXv2 yet: https://github.com/facebook/docusaurus/issues/4029
        # so we cannot add an MD-formatted link in a <span> element, as it won't get parsed.
        # therefore, for now, we add these on a newline.

        # do the same for 'any view source' links
        if 'viewcode-link' in node.attributes['classes']:
            self.add('\n&#8203;<span className="view-source">')

        self.in_reference = True
        url = self._refuri2http(node)
        if url is None:
            return

        self.add('[')
        for child in node.children:
            child.walkabout(self)
        self.add(']({})'.format(url))

        if('viewcode-link' in node.attributes['classes']):
            self.add("</span>\n")

        raise nodes.SkipNode


    def depart_reference(self, node):
        """Any reference (aka link), whether external or internal:
        https://docutils.sourceforge.io/docs/ref/doctree.html#reference"""
        self.in_reference = False
        pass


    def visit_title_reference(self, node):
        """A reference in a title.
        https://docutils.sourceforge.io/docs/ref/doctree.html#title-reference"""
        self.add('`')
        for child in node.children:
            child.walkabout(self)
        self.add('`')
        raise nodes.SkipNode


    def depart_title_reference(self, node):
        """A reference in a title.
        https://docutils.sourceforge.io/docs/ref/doctree.html#title-reference"""
        pass


    def visit_enumerated_list(self, node):
        """Contains list_item elements which are uniformly marked with enumerator labels:
        https://docutils.sourceforge.io/docs/ref/doctree.html#enumerated-list"""
        self.depth.descend('list')
        self.depth.descend('enumerated_list')


    def depart_enumerated_list(self, node):
        """Contains list_item elements which are uniformly marked with enumerator labels:
        https://docutils.sourceforge.io/docs/ref/doctree.html#enumerated-list"""
        self.enumerated_count[self.depth.get('list')] = 0
        self.depth.ascend('enumerated_list')
        self.depth.ascend('list')

    
    def visit_bullet_list(self, node):
        """Contains list_item elements which are uniformly marked with bullets:
        https://docutils.sourceforge.io/docs/ref/doctree.html#bullet-list"""
        self.depth.descend('list')
        self.depth.descend('bullet_list')


    def depart_bullet_list(self, node):
        """Contains list_item elements which are uniformly marked with bullets:
        https://docutils.sourceforge.io/docs/ref/doctree.html#bullet-list"""
        self.add('\n')
        self.depth.ascend('bullet_list')
        self.depth.ascend('list')


    def visit_list_item(self, node):
        """Container for the elements of a (bulleted or enumerated) list item:
        https://docutils.sourceforge.io/docs/ref/doctree.html#list-item"""
        self.depth.descend('list_item')
        depth = self.depth.get('list')
        depth_padding = ''.join(['  ' for i in range(depth - 1)])
        marker = '*'
        if node.parent.tagname == 'enumerated_list':
            if depth not in self.enumerated_count:
                self.enumerated_count[depth] = 1
            else:
                self.enumerated_count[depth] = self.enumerated_count[depth] + 1
            marker = str(self.enumerated_count[depth]) + '.'
        self.add(depth_padding + marker + ' ')


    def depart_list_item(self, node):
        """Container for the elements of a (bulleted or enumerated) list item:
        https://docutils.sourceforge.io/docs/ref/doctree.html#list-item"""
        self.depth.ascend('list_item')


    def visit_definition_list(self, node):
        """List of terms and their definitions; used for glossaries, classification, or subtopics: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition-list"""
        # generally already correctly parsed as a list or paragraphs, so passing here
        pass


    def depart_definition_list(self, node):
        """List of terms and their definitions; used for glossaries, classification, or subtopics: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition-list"""
        # generally already correctly parsed as a list or paragraphs, so passing here
        pass


    def visit_definition(self, node):
        """Container for the body elements used to define a term in a definition_list: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition"""
        self.add('\n')
        self.start_level('    ')


    def depart_definition(self, node):
        """Container for the body elements used to define a term in a definition_list: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#definition"""
        self.add('\n')
        self.finish_level()


    ################################################################################
    # Field lists of parameters/return values/exceptions
    #
    # field_list
    #   field
    #       field_name (e.g 'returns/parameters/raises')
    #           field_body (often a bulleted list)    #


    def visit_field_list(self, node):
        """Two-column table-like structures resembling database records (label & data pairs):
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-list
        """
        pass


    def depart_field_list(self, node):
        """Two-column table-like structures resembling database records (label & data pairs):
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-list
        """
        pass


    def visit_field(self, node):
        """A pair of field_name and field_body elements:
        https://docutils.sourceforge.io/docs/ref/doctree.html#field
        """
        self.add('\n')


    def depart_field(self, node):
        """A pair of field_name and field_body elements:
        https://docutils.sourceforge.io/docs/ref/doctree.html#field
        """
        self.add('\n')


    def visit_field_body(self, node):
        """Container for the body of a field: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-body"""
        pass


    def depart_field_body(self, node):
        """Container for the body of a field: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-body"""
        pass


    def visit_field_name(self, node):
        """Analogous to a database field's name, e.g 'returns', 'parameters':
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-name
        """
        self.add('#### ')


    def depart_field_name(self, node):
        """Analogous to a database field's name, e.g 'returns', 'parameters':
        https://docutils.sourceforge.io/docs/ref/doctree.html#field-name
        """
        self.add('\n\n')
        pass


    def visit_label(self, node):
        """Basic label: https://docutils.sourceforge.io/docs/ref/doctree.html#label"""
        print("Unchecked 'label' directive found in document " + self.builder.current_docname + ":", node) 
        self.add('\n')


    def depart_label(self, node):
        """Basic label: https://docutils.sourceforge.io/docs/ref/doctree.html#label"""
        self.add('\n')


    ################################################################################
    # Code blocks

    def visit_literal(self, node):
        """Literal element, e.g. a code variable: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal """
        self.add('`')
        for child in node.children:
            child.walkabout(self)
        self.add('`')
        raise nodes.SkipNode


    def depart_literal(self, node):
        """Literal element, e.g. a code variable: 
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal """
        pass


    def visit_literal_strong(self, node):
        """Literal (e.g. `string`) to make bold."""
        self.add('**`')


    def depart_literal_strong(self, node):
        """Literal (e.g. `string`) to make bold."""
        self.add('`**')


    def visit_literal_emphasis(self, node):
        """Literal (e.g. `string`) to emphasize."""
        # do not add '_' if we're in a reference with a link
        if not self.in_reference:
            self.add('_')


    def depart_literal_emphasis(self, node):
        """Literal (e.g. `string`) to emphasize."""
        # if in a reference with a link, remove the '_' at the end
        if self.in_reference:
            self.add('')
    

    def visit_literal_block(self, node):
        """Block of text where line breaks and whitespace are significant and must be preserved, e.g. code:
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal-block
        
        Has an optional `language` parameter."""
        if (node['language']):
            self.add('```' + node['language'] + '\n')
        else:
            self.add('```\n')
        for child in node.children:
            child.walkabout(self)
        self.add('\n```\n\n')
        raise nodes.SkipNode


    def depart_literal_block(self, node):
        """Block of text where line breaks and whitespace are significant and must be preserved, e.g. code:
        https://docutils.sourceforge.io/docs/ref/doctree.html#literal-block
        
        Has an optional `language` parameter."""
        pass


    ################################################################################
    # Admonitions: https://docusaurus.io/docs/markdown-features/admonitions
    #
    # 
    # :::note
    # :::tip
    # :::info
    # :::caution
    # :::danger


    def visit_note(self, node):
        """Sphinx note directive."""
        self.add(':::note\n\n')


    def depart_note(self, node):
        """Sphinx note directive."""
        self.add('\n:::\n\n')


    def visit_caution(self, node):
        """Sphinx caution directive."""
        self.add(':::caution\n\n')


    def depart_caution(self, node):
        """Sphinx caution directive."""
        self.add('\n:::\n\n')


    def visit_important(self, node):
        """Sphinx important directive."""
        self.add(':::caution important\n\n')


    def depart_important(self, node):
        """Sphinx important directive."""
        self.add('\n:::\n\n')


    def visit_warning(self, node):
        """Sphinx warning directive."""
        self.add(':::warning\n\n')


    def depart_warning(self, node):
        """Sphinx warning directive."""
        self.add('\n:::\n\n')


    def visit_seealso(self, node):
        self.add(':::tip see also\n\n')


    def depart_seealso(self, node):
        self.add('\n:::\n\n')


    ################################################################################
    # Images

    def visit_image(self, node):
        """Images: https://docutils.sourceforge.io/docs/ref/doctree.html#image."""
        print("Unchecked 'image' directive found in document " + self.builder.current_docname + ":", node) 
        uri = node.attributes['uri']
        doc_folder = os.path.dirname(self.builder.current_docname)
        if uri.startswith(doc_folder):
            # drop docname prefix
            uri = uri[len(doc_folder):]
            if uri.startswith('/'):
                uri = '.' + uri
        self.add('\n\n![image](%s)\n\n' % uri)


    def depart_image(self, node):
        """Images: https://docutils.sourceforge.io/docs/ref/doctree.html#image."""
        pass


    ################################################################################
    # Classes/methods/properties/attributes and autosummaries
    # https://www.sphinx-doc.org/en/master/extdev/nodes.html

    def visit_desc(self, node):
        """Container for class and method and property descriptions."""
        self.depth.ascend('desc')
        desctype = node.attributes["desctype"] if "desctype" in node.attributes else None
        self.current_desc_type = desctype
        if desctype in ['class', 'method', 'property', 'attribute']:
            self.add('<div className="' + desctype + '">\n')
        else:
            self.add('<div>\n')
        self.parsed_desc_name = False # whether the name has already been parsed


    def depart_desc(self, node):
        """Container for class and method descriptions."""
        self.depth.descend('desc')
        self.add('\n</div>\n\n')


    def visit_desc_signature(self, node):
        """The main signature (i.e. its name + parameters) of a class/method/property."""
        self.in_signature = True
        # TBD: increase heading levels if description is nested in another one (e.g. in modelhub.ModelHub.aggregate)
        desc_depth = self.depth.get('desc')
        if self.current_desc_type in ['method', 'property', 'attribute']:
            self.add("\n### ")
        else:
            self.add("\n## ")


    def depart_desc_signature(self, node):
        """The main signature (i.e. its name + parameters) of a class/method/property/attribute."""
        self.in_signature = False
        # only close the signature if it's not a property or attribute (which have no params)
        self.add('\n\n')


    def visit_desc_annotation(self, node):
        """Type annotation of the description, e.g 'method', 'class'."""
        self.add('<span className="type-annotation">')
        self.add('<em>')
        if self.parsed_desc_name:
            # already parsed desc name; add newlines so references within the annotation render properly in MD
            self.add('\n\n')


    def depart_desc_annotation(self, node):
        """Type annotation of the description, e.g 'method', 'class'."""
        # if this is not a property or attribute (i.e. a class/method), remove the last element (=")"
        if self.current_desc_type not in ['property', 'attribute']:
            self.get_current_output('body')[-1] = self.get_current_output('body')[-1][:-1]
        if self.parsed_desc_name:
            # already parsed desc name; add newlines so references within the annotation render properly in MD
            self.add('\n\n')
        self.add('</em>')
        self.add('</span> ')


    def visit_desc_addname(self, node):
        """Module preroll for class/method/property/attribute, e.g. 'domain' in 'domain.classname'."""
        if self.current_desc_type in ['method', 'property', 'attribute']:
            # no need to repeat the classdomain
            raise nodes.SkipNode
        else:
            self.add('<span className="additional-name">')


    def depart_desc_addname(self, node):
        """Module preroll for class/method/property/attribute, e.g. 'domain' in 'domain.classname'."""
        if self.current_desc_type in ['method', 'property', 'attribute']:
            # no need to repeat the classdomain
            raise nodes.SkipNode
        else:
            self.add('</span>')


    def visit_desc_name(self, node):
        """Name of the class/method/property/attribute."""
        self.add('<span className="name">')
        # Escape any "__", which is a formatting string for markdown
        if node.rawsource.startswith("__"):
            self.add('\\')


    def depart_desc_name(self, node):
        """Name of the class/method/property/attribute."""
        self.add('</span>\n\n')
        # set that we've processed the desc name, so annotations can start using newlines
        self.parsed_desc_name = True


    def visit_desc_parameterlist(self, node):
        """Method/class parameter list."""
        if self.current_desc_type not in ['property', 'attribute']:
            self.add('<small className="parameter-list">(')


    def depart_desc_parameterlist(self, node):
        """Method/class parameter list."""
        if self.current_desc_type not in ['property', 'attribute']:
            self.add(')</small>')


    def visit_desc_parameter(self, node):
        """Single method/class parameter."""
        self.add('<span className="parameter" id="'+ node[0].astext() + '">')


    def depart_desc_parameter(self, node):
        """Single method/class parameter."""
        self.add('</span>')
        # if there are additional params, include a comma
        if node.next_node(descend=False, siblings=True):
            self.add(', ')
            

    def visit_desc_content(self, node):
        """Description of the class/method/property/attribute."""
        self.add('\n<div className="content">\n\n')
        # leave current_desc_type, so there's no custom signature parsing (e.g. newlines for references)
        self.in_signature = False


    def depart_desc_content(self, node):
        """Description of the class/method/property/attribute."""
        self.add('\n</div>\n\n')


    def visit_autosummary_toc(self, node):
        """Sphinx autosummary with TOC option specified: 
        http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
        # if an autosummary type (table or toc) is not yet shown, show the TOC list
        if self.current_desc_type not in self.autosummary_shown:
            self.autosummary_shown.append(self.current_desc_type)
        else:
            raise nodes.SkipNode


    def depart_autosummary_toc(self, node):
        """Sphinx autosummary with TOC option specified: 
        http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
        self.add("\n\n")


    def visit_autosummary_table(self, node):
        """Sphinx autosummary: http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
        self.table_entries = [] # reset the table_entries, so depart_thead doesn't generate redundant columns
        self.autosummary_shown.append(self.current_desc_type)
        self.add('<div className="table-autosummary">\n\n')
        node.classes="autosummary"
        tgroup = nodes.tgroup(cols=2)
        thead = nodes.thead(classes="autosummary")
        tgroup += thead
        row = nodes.row()
        entry = nodes.entry()
        entry += nodes.inline(text=" ")
        row += entry
        entry = nodes.entry()
        entry += nodes.inline(text=" ")
        row += entry
        thead.append(row)
        node.insert(0, thead)
        self.tables.append(node)


    def depart_autosummary_table(self, node):
        """Sphinx autosummary: http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html."""
        self.add('\n</div>\n\n')


    ################################################################################
    # Tables
    #
    # docutils.nodes.table
    #     docutils.nodes.tgroup [cols=x]
    #       docutils.nodes.colspec
    #
    #       docutils.nodes.thead
    #         docutils.nodes.row
    #         docutils.nodes.entry
    #         docutils.nodes.entry
    #         docutils.nodes.entry
    #
    #       docutils.nodes.tbody
    #         docutils.nodes.row
    #         docutils.nodes.entry

    
    def visit_table(self, node):
        """A data arrangement with rows and columns:
        https://docutils.sourceforge.io/docs/ref/doctree.html#table"""
        self.in_table = True
        self.tables += node


    def depart_table(self, node):
        """A data arrangement with rows and columns:
        https://docutils.sourceforge.io/docs/ref/doctree.html#table"""
        self.in_table = False
        if(len(self.tables) > 0):
            self.tables.pop()
        self.ensure_eol()
        self.add('\n')


    def visit_tabular_col_spec(self, node):
        """Specifications for a column in a table:
        https://docutils.sourceforge.io/docs/ref/doctree.html#colspec"""
        pass


    def depart_tabular_col_spec(self, node):
        """Specifications for a column in a table:
        https://docutils.sourceforge.io/docs/ref/doctree.html#colspec"""
        pass


    def visit_colspec(self, node):
        """Specifications for a column in a table:
        https://docutils.sourceforge.io/docs/ref/doctree.html#colspec"""
        pass


    def depart_colspec(self, node):
        """Specifications for a column in a table:
        https://docutils.sourceforge.io/docs/ref/doctree.html#colspec"""
        pass


    def visit_tgroup(self, node):
        """Table group"""
        self.descend('tgroup')


    def depart_tgroup(self, node):
        """Table group"""
        self.ascend('tgroup')


    def visit_thead(self, node):
        """Table head: https://docutils.sourceforge.io/docs/ref/doctree.html#thead"""
        if not len(self.tables):
            raise nodes.SkipNode
        
        self.theads.append(node)


    def depart_thead(self, node):
        """Table head: https://docutils.sourceforge.io/docs/ref/doctree.html#thead"""
        # end table head with as many "| -- |"s as there are table entries
        for i in range(len(self.table_entries)):
            length = 0
            for row in self.table_rows:
                if len(row.children) > i:
                    entry_length = len(row.children[i].astext())
                    if entry_length > length:
                        length = entry_length
            self.add('| ' + ''.join(_.map(range(length), lambda: '-')) + ' ')
        self.add('|\n')
        self.table_entries = []
        self.theads.pop()


    def visit_tbody(self, node):
        """Table body: https://docutils.sourceforge.io/docs/ref/doctree.html#tbody"""
        if not len(self.tables):
            raise nodes.SkipNode
        self.tbodys.append(node)


    def depart_tbody(self, node):
        """Table body: https://docutils.sourceforge.io/docs/ref/doctree.html#tbody"""
        self.tbodys.pop()


    def visit_row(self, node):
        """Table row: https://docutils.sourceforge.io/docs/ref/doctree.html#row"""
        if not len(self.theads) and not len(self.tbodys):
            raise nodes.SkipNode
        self.table_rows.append(node)


    def depart_row(self, node):
        """Table row: https://docutils.sourceforge.io/docs/ref/doctree.html#row"""
        self.add(' |\n')
        if not len(self.theads):
            self.table_entries = []


    def visit_entry(self, node):
        """Table entry: https://docutils.sourceforge.io/docs/ref/doctree.html#entry"""
        if not len(self.table_rows):
            raise nodes.SkipNode
        self.add("| ")
        self.table_entries.append(node)


    def depart_entry(self, node):
        """Table entry: https://docutils.sourceforge.io/docs/ref/doctree.html#entry"""
        length = 0
        i = len(self.table_entries) - 1
        for row in self.table_rows:
            if len(row.children) > i:
                entry_length = len(row.children[i].astext())
                if entry_length > length:
                    length = entry_length
        padding = ''.join(
            _.map(range(length - len(node.astext())), lambda: ' ')
        )
        self.add(padding + ' ')


    def descend(self, node_name):
        """Keep track of how deep we are in the current node (e.g. list or section)."""
        self.depth.descend(node_name)


    def ascend(self, node_name):
        """Keep track of how deep we are in the current node (e.g. list or section)."""
        self.depth.ascend(node_name)


class FrontMatterPositionDirective(SphinxDirective):
    """Directive to set a specific position in the sidebar for the document in its frontmatter"""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = False


    def run(self):
        docname = self.env.docname
        reference = directives.uri(self.arguments[0])
        frontmatter.setdefault(docname, dict())
        frontmatter[docname]['position'] = reference
        empty_node = nodes.raw()
        return [empty_node]


class FrontMatterSidebarTitleDirective(SphinxDirective):
    """Directive to set a specific title in the sidebar for the document in its frontmatter"""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = False


    def run(self):
        docname = self.env.docname
        title = directives.uri(self.arguments[0])
        frontmatter.setdefault(docname, dict())
        frontmatter[docname]['title'] = title
        empty_node = nodes.raw()
        return [empty_node]


class FrontMatterSlugDirective(SphinxDirective):
    """Directive to set a specific slug for the document in its frontmatter"""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = False


    def run(self):
        docname = self.env.docname
        reference = directives.uri(self.arguments[0])
        frontmatter.setdefault(docname, dict())
        frontmatter[docname]['slug'] = reference
        empty_node = nodes.raw()
        return [empty_node]


class DocusaurusWriter(Writer):
    """Class to write to Docusaurus-compatible MDX documentation from Sphinx.

    :param Writer: A top-level Sphinx Writer.

    """
    directives.register_directive('frontmatterposition', FrontMatterPositionDirective)
    directives.register_directive('frontmattersidebartitle', FrontMatterSidebarTitleDirective)
    directives.register_directive('frontmatterslug', FrontMatterSlugDirective)
    translator_class = DocusaurusTranslator
