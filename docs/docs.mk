# A makefile for building documentation in python projects,
# with Github pages support.
#
# 2012-03-04: website is not phony; misc increments
# 

webdir=website
source=source
autogen=source/api


.PHONY: all upload compile only-upload generate epydoc generate generate-custom clean clean-custom
	

# also change this in epydoc.cfg
webgit=git --git-dir $(webdir)/.git --work-tree=$(webdir)/ 

all: upload


# 
# compile-website: $(webdir) epydoc generate
# 	PYTHONPATH=`pwd`:$(PYTHONPATH) sphinx-build -E -n -a -b html $(source) $(webdir)

clean-custom:
	# This can be overridden by user
	
generate-custom:
	# This can be overridden by user

generate: generate-custom
	sphinx-autogen -o $(autogen) $(source)/*.rst
	sphinx-apidoc  -o $(autogen) ../src
	 
compile: $(webdir) generate 
	PYTHONPATH=`pwd`:$(PYTHONPATH) sphinx-build -E -n -a -b html $(source) $(webdir)
	
recompile: $(webdir) 
		PYTHONPATH=`pwd`:$(PYTHONPATH) sphinx-build -E -n -a -b html $(source) $(webdir)
	
	
$(webdir):
	@echo Checking out the website repository.
	git clone $(github_repo) $@
	@echo Switching to gh-pages branch.
	$(webgit) checkout origin/gh-pages -b gh-pages
	@echo Deleting master branch.
	$(webgit) branch -D master

upload: compile
	$(MAKE) only-upload
	
only-upload: 
	./gitadd.zsh $(webdir)
	$(webgit) push

clean: clean-custom
	rm -rf $(autogen)/
	rm -rf $(webdir)/
	
epydoc:
	epydoc --config epydoc.cfg --introspect-only -v --exclude-introspect=$(package).unittests --debug

.SECONDARY: