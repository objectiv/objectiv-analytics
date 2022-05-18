# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
DOCUSAURUSDIR = docusaurus
TARGETDIR			= ../../../objectiv.io/docs/docs/modeling/

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(SOURCEDIR)/bach/api-reference/DataFrame/bach.DataFrame.* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/bach.Series.* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/AbstractDateTime/bach.SeriesAbstractDateTime* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/AbstractNumeric/bach.SeriesAbstractNumeric* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Boolean/bach.SeriesBoolean* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Date/bach.SeriesDate* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Dict/bach.SeriesDict* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Dict/bach.SeriesInt* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Dict/bach.SeriesFloat* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Json/bach.SeriesJson* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Jsonb/bach.SeriesJsonb* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/List/bach.SeriesList* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/String/bach.SeriesString* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Time/bach.SeriesTime* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Timedelta/bach.SeriesTimedelta* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Timestamp/bach.SeriesTimestamp* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/Uuid/bach.SeriesUuid* # not the index
	rm -rf $(SOURCEDIR)/open-model-hub/models/**/modelhub.* # not the index
	rm -rf $(SOURCEDIR)/open-model-hub/api-reference/**/modelhub.* # not the index

	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) 0$(O)

clean-target:
	rm -rf $(TARGETDIR)/**/

copy-target:
	cp -a $(BUILDDIR)/$(DOCUSAURUSDIR)/* $(TARGETDIR)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
