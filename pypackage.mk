# Generic Makefile for python package providing testing/installation.

# (common version)

.PHONY: docs all develop test
	
all: develop

develop:
	python setup.py develop

docs: 
	make -C docs

coverage_dir=coverage_information
nose=nosetests --with-id
nose_parallel=--processes=16 --process-timeout=300 --process-restartworker
nose_coverage=--with-coverage --cover-html --cover-html-dir $(coverage_dir)  --cover-package=$(package)

test:
	@echo Overview for running tests for package $(package):
	@echo
	@echo - Use 'make test-failed' to redo only failed tests
	@echo - Use 'make test-parallel' to enable parallel testing
	@echo - Use 'make test-coverage' to do coverage testing
	@echo - Use the env. var. NOSE_PARAMS to pass extra arguments.
	@echo
	@echo For example:
	@echo   NOSE_PARAMS='--nologcapture -s -v' make test-failed
	@echo
	@echo
	$(nose) $(package) $(NOSE_PARAMS)


test-stop:
	$(nose) $(package) $(NOSE_PARAMS) -x

test-failed:
	$(nose) $(package) $(NOSE_PARAMS) --failed

test-parallel:
	$(nose) $(package) $(NOSE_PARAMS) $(nose_parallel) 

test-parallel-stop:
	$(nose) $(package) $(NOSE_PARAMS) $(nose_parallel) -x 

test-coverage:
	$(nose) $(package) $(NOSE_PARAMS) $(nose_coverage) 

