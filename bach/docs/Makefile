# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
DOCUSAURUSDIR = docusaurus
DOCSTARGETDIR = ../../../objectiv.io/docs/docs/

# Don't allow modelhub to check online whether a newer version is available while generating docs
export OBJECTIV_VERSION_CHECK_DISABLE = true

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(SOURCEDIR)/bach/api-reference/DataFrame/bach.DataFrame.* # not the index
	rm -rf $(SOURCEDIR)/bach/api-reference/Series/bach.Series.* # not the index
	# Delete all .rst files under $(SOURCEDIR)/bach/api-reference/Series, except for files called index.rst
	find $(SOURCEDIR)/bach/api-reference/Series/ -type f -name '*.rst' -not -name index.rst -delete
	rm -rf $(SOURCEDIR)/open-model-hub/models/**/modelhub.* # not the index
	rm -rf $(SOURCEDIR)/open-model-hub/api-reference/**/modelhub.* # not the index

	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) 0$(O)

clean-target:
	rm -rf $(DOCSTARGETDIR)modeling/*

copy-target:
	cp -a $(BUILDDIR)/$(DOCUSAURUSDIR)/* $(DOCSTARGETDIR)modeling/

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
