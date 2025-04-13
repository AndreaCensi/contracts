# PyContracts Testing Guide

This document explains how to run tests for the Python 3 compatible version of PyContracts.

## Test Setup

The testing infrastructure has been updated to use modern pytest and includes a comprehensive test suite for both Python 2 and Python 3 compatibility. We have fully migrated from nose to pytest, with details of the migration process documented in `nose_to_pytest_guide.md`.

### Test Files

The test suite includes:

1. **Core Tests**: Located in `src/contracts/testing/` directory.
   - These are the original tests from the PyContracts library.
   - All tests have been migrated from nose to pytest.
   - Previously using yield-style tests have been converted to parameterized tests.

2. **Python 3 Compatibility Tests**: Located in the `tests/` directory.
   - `test_collections_abc.py`: Tests compatibility with collections.abc module.
   - `test_string_compatibility.py`: Tests string/bytes handling.
   - `test_exception_handling.py`: Tests exception handling compatibility.
   - `test_python312_compatibility.py`: Tests specifically for Python 3.12+ compatibility.
   - `test_pycontracts_py3.py`: A comprehensive test for all Python 3 compatibility features.
   - `test_py_compatibility.py`: Tests for the Python 2/3 compatibility layer.
   - `test_utils.py`: Tests for utility functions with Python 3 compatibility.
   - `test_enabling.py`: Tests for contract enabling/disabling functionality.
   - `test_inspection.py`: Tests for inspection utilities.

### Running Tests

You can run all tests using pytest directly:

```bash
python -m pytest
```

Or run specific test subsets:

```bash
# Run the Python 3.12+ compatibility tests
python -m pytest tests/test_python312_compatibility.py -v

# Run all Python 3 compatibility tests
python -m pytest tests/ -v

# Run specific original tests
python -m pytest src/contracts/testing/test_multiple.py -v
```

To run tests with coverage reporting:

```bash
# Run all tests with coverage
python -m pytest --cov=src.contracts

# Run specific tests with coverage for a specific module
python -m pytest tests/test_py_compatibility.py --cov=src.contracts.py_compatibility
```

## CI/CD Integration

A GitHub Actions workflow is configured in `.github/workflows/python-test.yml` that:

1. Runs tests on multiple Python versions (2.7, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)
2. Runs tests on multiple operating systems (Ubuntu, Windows, macOS)
3. Uploads coverage reports to Codecov

## Testing with Tox

You can also run tests across multiple Python versions locally using tox:

```bash
# Install tox if you don't have it
pip install tox

# Run tests on all available Python versions
tox

# Run tests on a specific Python version
tox -e py312
```

## Test Dependencies

The test suite requires the following dependencies:

- pytest>=7.0.0
- pytest-cov>=6.0.0
- numpy (for array tests)
- six
- future
- decorator
- pyparsing>=3.0.0 (for Python 3 compatibility)

These are listed in `requirements-dev.txt` and can be installed with:

```bash
pip install -r requirements-dev.txt
```

## Migration Tools

We've created a set of tools to help with the migration from nose to pytest. These tools may be useful for other projects migrating from nose to pytest:

- `pytest_migration.py`: Command-line tool for tracking and automating migrations
- `pytest_migration_lib/`: Library with utilities for migration tasks
  - `tracking.py`: Tools for tracking migration progress
  - `automigrate.py`: Tools for automatically converting nose tests

For more information on using these tools, see the `nose_to_pytest_guide.md` file.

## Known Test Issues

1. **Expected Failures**: A small number of tests are marked with `@pytest.mark.xfail` or `@unittest.expectedFailure` because they test functionality that is known to have issues:
   - Tests for contracts with static methods and class methods 
   - String comparison tests in Python 3.12+

2. **NumPy Deprecation Warnings**: Tests using deprecated NumPy functions like `np.float` may show warnings. These have been fixed in the tests that we frequently run.

3. **Python 2.7 Tests**: When running in Python 3.12+, some tests specific to Python 2.7 features might be skipped.