from .docusaurus_writer import DocusaurusWriter, DocusaurusTranslator
from docutils.io import StringOutput
from io import open
from munch import munchify
from os import path
from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import ensuredir, os_path
import datetime
from urllib.parse import quote

logger = logging.getLogger(__name__)

class DocusaurusBuilder(Builder):
    """Class to build Docusaurus-compatible MDX documentation from Sphinx.

    """
    name = 'docusaurus'
    format = 'docusaurus'
    epilog = __('The Docusaurus files are in %(outdir)s.')

    allow_parallel = True
    default_translator_class = DocusaurusTranslator
    current_docname = None # the current doc being processed

    out_suffix = '.mdx' # file extensions for output
    link_suffix = '/' # end of URL, e.g. a trailing slash
    markdown_http_base = '/modeling' # base URL path for all files

    # formatting of frontmatter for the API references
    # first level specifies the document path, e.g. 'models/api-reference'
    # second level specifies how far back the path should show:
    #   * ``title_tree_levels``: e.g. 'models.abc.xyz' with title_tree_levels 2 becomes 'abc.xyz' in the title
    #   * ``slug_tree_levels``: e.g. 'models.abc' with slug_tree_levels 1 becomes 'abc' in the slug
    # TODO: make configurable instead of hardcoded
    api_frontmatter = {
        'open-model-hub/models': {
            'title_tree_levels': 1,
            'slug_tree_levels': 1
        },
        'open-model-hub/api-reference': {
            'title_tree_levels': 1,
            'slug_tree_levels': 1
        },
        'bach/api-reference': {
            'title_tree_levels': 1,
            'slug_tree_levels': 1
        }
    }


    def init(self):
        self.secnumbers = {}


    def get_outdated_docs(self):
        """
        Find documents that are outdated and should be built.

        :returns: generator with each docname that is outdated.

        """
        
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = path.join(self.outdir, docname + self.out_suffix)
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                pass


    def get_target_uri(self, docname: str, typ: str = None) -> str:
        """
        Generate a URI from the docname and config.

        :returns: Formatted URI

        """
        
        return quote(docname) + self.link_suffix


    def prepare_writing(self, docnames):
        """
        Prepares documents for writing. Instantiates the writer and context.

        """
        
        self.writer = DocusaurusWriter(self)
        self.ctx = self.create_context()


    def create_context(self):
        """
        Creates the context for writing documents; currently just with the datetime.

        """

        ctx = munchify({
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        })
        return ctx


    def write_doc(self, docname, doctree):
        """
        Writes a document to the fileystem.

        """

        self.current_docname = docname
        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, os_path(docname) + self.out_suffix)
        ensuredir(path.dirname(outfilename))
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:  # type: ignore
                f.write(self.writer.output)
        except (IOError, OSError) as err:
            logger.warning(__("error writing file %s: %s"), outfilename, err)


    def finish(self):
        pass
