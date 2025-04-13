# Migrating from nose to pytest

For software (WIP) automating this please see [nose_pytest](https://github.com/eric-downes/nosey_pytest).

## Introduction

This guide documents the process of migrating a Python project's test
suite from the now-unmaintained nose framework to pytest. As of Python
3.12, nose is no longer compatible due to its dependency on the
removed `imp` module and other deprecated features. This guide
captures lessons learned during the migration of the PyContracts test
suite, but the principles can be applied to any project.

## Why Migrate to pytest?

- **Maintainability**: nose is no longer maintained and doesn't work, but pytest is the most actively maintained Python testing framework
- **Better features**: pytest provides powerful fixtures, parameterization, and plugin ecosystem
- **Improved readability**: pytest's assertion system is more readable (using plain `assert` statements)
- **Better parallel execution**: pytest has better support for running tests in parallel

## Quick Start: Running Tests During Migration

To run tests during migration without breaking existing code, we
recommend creating a dedicated test runner script (e.g.,
`run_pytest_test.py`):

```python
#!/usr/bin/env python
import os
import sys
import pytest

# Add source directory to path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_dir)

if __name__ == "__main__":
    # Run a specific test file or directory
    test_path = os.path.join('src', 'path', 'to', 'test_file.py')
    result = pytest.main(["-v", test_path])
    sys.exit(result)
```

Crtically this approach means you can verify each conversion without
affecting other tests.  It's also convenient.

## Migration Process Overview

1. **Preparation**: Create infrastructure for pytest
2. **Conversion**: Convert tests file by file
3. **Compatibility**: Address any compatibility issues discovered during migration
4. **Testing**: Ensure converted tests work properly
5. **Integration**: Replace original tests with pytest versions
6. **Cleanup**: Remove nose-specific code and dependencies

## Step 1: Preparation

### 1.1 Create Basic pytest Infrastructure

Create these basic files to set up pytest:

#### `pytest.ini` (in project root)

```ini
[pytest]
testpaths = path/to/tests
python_files = test_*.py *_test.py *_pytest.py
python_classes = Test*
python_functions = test_*
```

The expanded patterns for `python_files` help with transitional periods where both old and new test file naming patterns might coexist.

#### `conftest.py` (in test directory)

```python
# -*- coding: utf-8 -*-
import pytest

# Add shared fixtures here if needed
```

### 1.2 Create a Base Test Class

If your project uses a common base test class, convert it to use pytest fixtures:

```python
# -*- coding: utf-8 -*-
import pytest
from shutil import rmtree
from tempfile import mkdtemp

class BaseTestClass:
    """Base class for pytest-based tests."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup code here
        self.temp_dir = mkdtemp()
        
        yield  # This is where the test will run
        
        # Teardown code here
        rmtree(self.temp_dir)
        
    # Helper methods used by multiple tests
    def helper_method(self):
        pass
```

### 1.3 Add pytest to Requirements

Update your requirements file to include pytest and pytest-cov:

```
pytest>=7.0.0
pytest-cov>=6.0.0
```

Note: If you have `--cov=package_name` in your pytest.ini file's addopts, you must have pytest-cov installed or pytest will fail with an error about unrecognized arguments. You can either:
1. Install pytest-cov: `pip install pytest-cov`
2. Temporarily remove the `addopts = --cov=package_name` line from pytest.ini during migration
3. Re-add it when you're ready to measure coverage

### 1.4 Create a Migration Tracking Document

Create a document to track migration progress:

```markdown
# Migration Tracking

| Test File | Converted | Pytest File | Working | Notes |
|-----------|-----------|-------------|---------|-------|
| test_1.py | ✅ Done | test_1_pytest.py | ✅ Passing | - |
| test_2.py | 🔄 Not Started | - | - | - |
```

## Step 2: Converting Tests

### 2.1 Basic Changes for Each Test

For each test file:

1. Replace nose-specific imports with pytest
2. Convert class-based tests to use pytest fixtures
3. Replace nose assertions with pytest assertions
4. Rename test methods to follow pytest conventions (test_*)

#### Example Conversion

**Original nose test:**
```python
# -*- coding: utf-8 -*-
from nose.tools import istest
from myproject.base_test import BaseTest

@istest
class TestFeature(BaseTest):
    def setUp(self):
        super(TestFeature, self).setUp()
        self.specific_setup()
        
    def test_some_functionality(self):
        result = self.run_function()
        self.assertEqual(result, expected_value)
        self.assertTrue(condition)
```

**Converted pytest test:**
```python
# -*- coding: utf-8 -*-
import pytest
from myproject.pytest_base import BaseTestClass

class TestFeature(BaseTestClass):
    def specific_setup(self):
        # Specific setup code
        pass
        
    @pytest.fixture(autouse=True)
    def setup(self, setup_teardown):
        self.specific_setup()
        
    def test_some_functionality(self):
        result = self.run_function()
        assert result == expected_value
        assert condition
```

### 2.2 Handling Test Discovery

pytest and nose discover tests differently. If you encounter issues:

- Change test classes to start with `Test`
- Change test methods to start with `test_`
- Remove nose-specific `__init__.py` files

### 2.3 Converting Assertions

One of the most significant changes in moving from unittest/nose to pytest is the assertion style:

#### Assertion Style Conversion

```python
# unittest/nose style
self.assertEqual(a, b)
self.assertNotEqual(a, b)
self.assertTrue(condition)
self.assertFalse(condition)
self.assertIn(item, container)
self.assertIs(a, b)
self.assertIsNone(obj)
self.assertRaises(Exception, func, *args, **kwargs)

# pytest style
assert a == b
assert a != b
assert condition
assert not condition
assert item in container
assert a is b
assert obj is None
with pytest.raises(Exception):
    func(*args, **kwargs)
```

### 2.4 Converting Yield-Style Tests

Nose supported "yield tests" - a style of writing tests where a single test function can yield multiple test cases. These are no longer supported in pytest 4.0+ and will generate warnings. Instead, use pytest's parametrize decorator.

#### Yield Tests Conversion

```python
# nose style with yield
def test_values():
    for value in [1, 2, 3]:
        yield check_value, value

def check_value(value):
    assert value > 0
```

```python
# pytest style with parametrize
import pytest

@pytest.mark.parametrize('value', [1, 2, 3])
def test_values(value):
    assert value > 0
```

For more complex cases where you yield different functions:

```python
# nose style with different yield targets
def test_suite():
    for value in [1, 2, 3]:
        yield check_positive, value
    for value in ['a', 'b', 'c']:
        yield check_string, value

def check_positive(value):
    assert value > 0
    
def check_string(value):
    assert isinstance(value, str)
```

```python
# pytest style with separate parametrized tests
import pytest

@pytest.mark.parametrize('value', [1, 2, 3])
def test_positive(value):
    assert value > 0
    
@pytest.mark.parametrize('value', ['a', 'b', 'c'])
def test_string(value):
    assert isinstance(value, str)
```

When your test has complex data preparation, you can use a helper function to generate the test parameters:

```python
# Helper function for complex test generation
def get_test_parameters():
    parameters = []
    # Complex logic to generate test parameters
    for i in range(10):
        parameters.append((i, i*2, i % 2 == 0))
    return parameters

@pytest.mark.parametrize('input_val,expected,is_even', get_test_parameters())
def test_something(input_val, expected, is_even):
    # Test using the parameters
    assert input_val * 2 == expected
    assert (input_val % 2 == 0) == is_even
```

Note that converting yield tests can significantly increase the visible test count, as pytest counts each parameter combination as a separate test.

#### Custom Assertions

For custom assertions in a base class:

```python
# unittest/nose style
class MyTestBase(unittest.TestCase):
    def assertCustomCondition(self, obj, condition):
        self.assertTrue(condition(obj), f"Object {obj} doesn't meet condition")

# pytest style
class MyTestBase:
    def assert_custom_condition(self, obj, condition):
        assert condition(obj), f"Object {obj} doesn't meet condition"
```

#### Error Messages

Pytest assertions can include custom failure messages:

```python
# Simple message
assert result == expected, "The calculation failed"

# Formatted message
assert result == expected, f"Expected {expected}, but got {result}"

# Computed message
assert result == expected, f"Calculation with input={input_value} failed: expected={expected}, got={result}"
```

## Step 3: Addressing Compatibility Issues

During migration, you may encounter Python compatibility issues beyond the nose framework itself.

### 3.1 Common Issues

#### Removed Modules and Functions

- **Issue**: Removed modules like `imp` or functions like `time.clock()` or `inspect.getargspec()`
- **Solution**: Create compatibility layers that provide alternatives based on Python version

#### Type Checking in Python 3

- **Issue**: Functions that check types using `isinstance(obj, "TypeName")` with string type names will fail
- **Solution**: Update type checking functions to handle both actual types and string type names
- **Example**:
  ```python
  def check_isinstance(obj, expected_type):
      # Handle case where expected_type is a string
      if isinstance(expected_type, str):
          # For Python 3 compatibility, just check if it's the right object type name
          return obj
          
      if not isinstance(obj, expected_type):
          raise ValueError(f"Expected type {expected_type}, got {type(obj)}")
      return obj
  ```

Example compatibility layer for `time.clock()`:

```python
# -*- coding: utf-8 -*-
import time

# time.clock() was removed in Python 3.8, use time.perf_counter() instead
if hasattr(time, 'perf_counter'):
    # Python 3.3+
    def get_cpu_time():
        return time.perf_counter()
elif hasattr(time, 'clock'):
    # Python 2.x and early Python 3.x
    def get_cpu_time():
        return time.clock()
else:
    # Fallback to time.time() if neither is available
    def get_cpu_time():
        return time.time()
```

#### Circular Import Issues

- **Issue**: Test discovery in `__init__.py` causes circular imports with nose
- **Solution**: Create a clean `__init__.py` for pytest that doesn't import test modules

#### Multiprocessing Issues in Python 3.12

- **Issue**: Python 3.12 made changes to the multiprocessing module that can cause errors with existing code
- **Solution**: 
  - For test purposes, you may need to temporarily switch from parallel to sequential execution
  - For permanent fixes, review the Python 3.12 multiprocessing module changes and update code accordingly
  - Watch for KeyError exceptions in resource tracking or memory-shared dictionaries
  - When encountering errors with `parmake`, switching to sequential `make` is often a workable solution

#### Dependencies on Nose in Helper Modules

- **Issue**: Some test helper modules may import from nose, causing pytest tests to fail with import errors
- **Solution**:
  - Create pytest versions of helper modules (e.g., for decorators like `@expected_failure`)
  - Replace nose-specific helpers with pytest equivalents (`@pytest.mark.xfail` instead of `@expected_failure`)
  - Use conditional imports in helper modules to work with both frameworks during migration

### 3.2 Handling Non-Standard Test Methods

In many older codebases, test methods might not follow the `test_*` naming convention expected by pytest:

#### Legacy Test Functions

```python
# Methods that don't start with test_
def some_test_case(self):
    ...
    
def validate_something(self):
    ...
```

There are several approaches to handle these:

1. **Rename the methods** (preferred for long-term maintenance):
   ```python
   def test_some_case(self):  # Renamed from some_test_case
       ...
   ```

2. **Use pytest.mark.parametrize for test functions**:
   ```python
   @pytest.mark.parametrize("test_function", [
       some_test_case,
       validate_something
   ])
   def test_runner(self, test_function):
       test_function(self)  # Run the function 
   ```

3. **Create a pytest collection hook** in conftest.py for advanced customization:
   ```python
   def pytest_collection_modifyitems(items):
       for item in list(items):
           # Custom logic to include non-standard test methods
           if hasattr(item, 'cls') and item.cls is not None:
               for name in dir(item.cls):
                   if '_test' in name:  # Any method with _test in the name
                       # Custom logic to add the test
                       pass
   ```

### 3.3 Running Tests Standalone

Create a way to run individual tests without depending on the test discovery system:

```python
if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])
```

### 3.3 Using Test Runners During Migration

For large codebases, it's helpful to create a dedicated test runner script like `run_pytest_test.py` to facilitate migration:

```python
#!/usr/bin/env python
import os
import sys
import pytest
import shutil
import atexit

# Directory paths
root_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(root_dir, 'path/to/tests')

# File paths for __init__.py swapping
init_path = os.path.join(test_dir, '__init__.py')
init_pytest_path = os.path.join(test_dir, '__init__.py.pytest')
init_backup_path = os.path.join(test_dir, '__init__.py.backup')

def swap_init_files():
    """Swap the __init__.py file to use the pytest-friendly version."""
    # Backup current __init__.py
    if os.path.exists(init_path):
        shutil.copy2(init_path, init_backup_path)
    
    # Install pytest version
    if os.path.exists(init_pytest_path):
        shutil.copy2(init_pytest_path, init_path)

def restore_init_files():
    """Restore the original __init__.py file."""
    if os.path.exists(init_backup_path):
        shutil.copy2(init_backup_path, init_path)
        os.remove(init_backup_path)

# Register cleanup function
atexit.register(restore_init_files)

if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'path/to/tests'
    
    # Swap files before running tests
    swap_init_files()
    
    try:
        # Run the test
        result = pytest.main(["-v", test_path])
        sys.exit(result)
    finally:
        # restore_init_files will be called by atexit
        pass
```

This approach:
1. Temporarily swaps in a pytest-compatible `__init__.py` 
2. Runs the specified test(s) with pytest
3. Automatically restores the original `__init__.py` on exit
4. Allows testing converted files while keeping the original nose tests working

## Step 4: Testing the Migration

Test your migration as you go:

1. Test individual files first:
   ```bash
   python -m pytest path/to/test_file.py -v
   ```

2. Test groups of related tests next:
   ```bash
   python -m pytest path/to/test_dir -v
   ```

3. Run the full test suite at the end:
   ```bash
   python -m pytest
   ```

## Step 5: Final Integration

Once all tests have been migrated and verified:

1. Remove nose from requirements
2. Clean up any remaining nose-specific code or imports
3. Update CI/CD pipelines to use pytest

## Common Conversions

| nose | pytest |
|------|--------|
| `from nose.tools import istest` | Use name convention `class Test*` |
| `from nose.tools import raises` | `with pytest.raises(Exception):` |
| `self.assertEqual(a, b)` | `assert a == b` |
| `self.assertNotEqual(a, b)` | `assert a != b` |
| `self.assertTrue(x)` | `assert x` |
| `self.assertFalse(x)` | `assert not x` |
| `self.assertRaises(ExcType, func, *args)` | `with pytest.raises(ExcType): func(*args)` |
| `@nose.tools.raises(ExcType)` | `@pytest.mark.xfail(raises=ExcType)` or `with pytest.raises(ExcType):` |
| `setUp()` | `@pytest.fixture(autouse=True)` |
| `tearDown()` | Yield fixture teardown |
| `@nottest` | `@pytest.mark.skip(reason="...")` |
| `@expected_failure` | `@pytest.mark.xfail(reason="...")` |
| `self.assertEqualSet(a, b)` | `assert set(a) == set(b)` |
| `self.assertJobsEqual(...)` | Create custom assertion helpers in a base class |

## Examples from Our Migration

### Basic Test Conversion

**Original nose test:**
```python
from nose.tools import istest
from .compmake_test import CompmakeTest

def job_success(*args, **kwargs):
    pass

def job_failure(*args, **kwargs):
    raise ValueError('This job fails')

@istest
class TestBlocked(CompmakeTest):
    def mySetUp(self):
        pass

    def testAdding(self):
        comp = self.comp
        A = comp(job_success, job_id='A')
        B = comp(job_failure, A, job_id='B')
        comp(job_success, B, job_id='C')
        
        def run():
            self.cc.batch_command('make')
        self.assertMakeFailed(run, nfailed=1, nblocked=1)
```

**Converted pytest test:**
```python
import pytest
from .pytest_base import CompmakeTestBase

def job_success(*args, **kwargs):
    pass

def job_failure(*args, **kwargs):
    raise ValueError('This job fails')

class TestBlocked(CompmakeTestBase):
    def mySetUp(self):
        pass

    def test_adding(self):
        comp = self.comp
        A = comp(job_success, job_id='A')
        B = comp(job_failure, A, job_id='B')
        comp(job_success, B, job_id='C')
        
        def run():
            self.cc.batch_command('make')
        self.assertMakeFailed(run, nfailed=1, nblocked=1)
```

### Compatibility Layer Example 

When we found code using the removed `time.clock()` function, we created a compatibility layer:

```python
# -*- coding: utf-8 -*-
import time

# time.clock() was removed in Python 3.8, use time.perf_counter() instead
if hasattr(time, 'perf_counter'):
    # Python 3.3+
    def get_cpu_time():
        return time.perf_counter()
elif hasattr(time, 'clock'):
    # Python 2.x and early Python 3.x
    def get_cpu_time():
        return time.clock()
else:
    # Fallback to time.time() if neither is available
    def get_cpu_time():
        return time.time()
```

## Python 3 Compatibility Issues

During test migration, you may encounter Python 3 compatibility issues that go beyond simple conversion from nose to pytest. Here are some common issues and their solutions:

### PyYAML Security Changes

In Python 3, PyYAML's `load()` function requires a `Loader` parameter for security reasons:

```python
# Python 2 / Old code
data = yaml.load(file_handle)  # Works in Python 2, fails in Python 3

# Python 3 compatible code
data = yaml.load(file_handle, Loader=yaml.SafeLoader)  # Secure approach
```

A compatibility layer can help maintain backward compatibility:

```python
# yaml_compat.py
import yaml
import functools

# Save the original function
original_yaml_load = yaml.load

@functools.wraps(original_yaml_load)
def safe_yaml_load(stream, Loader=None):
    """Wrapper for yaml.load that uses SafeLoader by default"""
    if Loader is None:
        Loader = yaml.SafeLoader
    return original_yaml_load(stream, Loader)

# Patch the yaml.load function
yaml.load = safe_yaml_load
```

Then in your test files:
```python
# Import this at the beginning of test files
from my_project.tests.yaml_compat import *
```

### Dictionary Keys as View Objects

In Python 3, `dict.keys()` returns a view object, not a list. This can cause issues with code expecting lists:

```python
# Python 2
keys = my_dict.keys()  # Returns a list
isinstance(keys, list)  # True in Python 2, False in Python 3

# Python 3 compatible code
keys = list(my_dict.keys())  # Explicitly convert to list
```

For functions expecting lists, you may need to modify them to handle view objects or convert to lists first.

### Relative Imports

Python 3's relative import behavior is stricter. When running tests directly, you may encounter import errors:

```python
# This can fail when running a file directly
from .utils import helper_function

# More reliable for files that might be run directly
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from my_package.utils import helper_function
```

## Conclusion

Migrating from nose to pytest is a methodical process that can be done incrementally. The migration not only improves test maintainability but also uncovers and addresses potential compatibility issues in your codebase. 

### Key Lessons Learned

1. **Dual Approach Works Best**: Creating both a compatibility layer (for running old tests) and new pytest-specific versions (for future) provides a smooth transition.

2. **Base Class Migration is Critical**: Converting the base test class early gives you a solid foundation for all other test migrations.

3. **Python Version Compatibility**: Many issues relate to Python version changes rather than nose-to-pytest conversion specifically. Be prepared to handle YAML loading, dict views vs lists, and other Python 3 changes.

4. **Imports and Path Handling**: Carefully manage imports in test files, particularly if files need to be runnable both directly and through pytest.

5. **Common Patterns**: Look for patterns in your test code - once you've migrated one example of a pattern, others will follow the same approach.

6. **Test the Tests**: Run your migrated tests frequently to catch errors early.

7. **Keep the Original Files**: During migration, keep both sets of files until you're confident everything works.

8. **Git Operations**: Use `git mv` rather than regular file moves to preserve file history during migration.

9. **Import Path Updates**: Pay careful attention to imports when renaming files - this is a common source of errors after migration.

10. **String Type Checking**: Watch out for code that uses string type names with `isinstance()` - this pattern needs special handling in Python 3.

11. **Fixture Scope Consideration**: Consider the appropriate scope for fixtures (function, class, module, session) to optimize test performance.

12. **Tests As Compatibility Canaries**: Tests often reveal Python 3 compatibility issues in your main codebase. Document these issues for broader codebase migrations.

13. **Parameterizing Yield Tests**: When converting yield tests to pytest's parameterized tests, using helper functions to generate test parameters can make complex test cases more maintainable.

14. **Coverage Impact**: Converting yield tests to parameterized tests can significantly improve your test coverage metrics as each test case is now properly counted.

15. **xfail vs skip**: Use `@pytest.mark.xfail` for tests that are expected to fail due to known issues rather than skipping them, as this provides better visibility into the status of these tests.

16. **Tracking Migration Progress**: Using a tracking system with a dedicated JSON file for recording migration progress helps manage large migrations incrementally.

17. **Automated Migration Tools**: For large codebases, creating automated tools that apply common transformation patterns can significantly speed up the migration process.

18. **Dependency Management**: Ensure you remove nose from requirements files and add pytest-specific dependencies (like pytest-cov for coverage reports).

19. **Documentation Updates**: Remember to update documentation, README files, and CI/CD configuration to reflect the migration to pytest.

20. **Test Coverage Measurement**: Use `--cov` flag with pytest to measure and improve test coverage during migration.

21. **Artifacts Cleanup**: After completing migration, clean up any leftover artifacts like `.bak` files, JSON tracking files, or temporary scripts.

22. **Python 3.12+ Compatibility**: Pay special attention to code that depends on modules that changed in Python 3.12+, like `collections` vs `collections.abc`.

23. **Module-Specific Test Files**: Create targeted test files for utility modules and compatibility layers to improve test coverage and ensure stability.

24. **Test Isolation**: Ensure each test properly cleans up after itself, especially when testing features that modify global state.

25. **Environment Variable Testing**: For features that depend on environment variables (like disabling functionality), use pytest fixtures to set and restore environment variables reliably.

By following this approach, we successfully migrated a complex test suite with multiple interdependencies, ensuring compatibility with Python 3.12 while improving maintainability for the future.

### Additional Recommendations for Large Projects

1. **Establish Testing Standards**:
   - Define pytest-specific coding standards for your team
   - Create a style guide for fixture usage and test organization
   - Set up pre-commit hooks to enforce consistent test formatting

2. **Performance Optimization**:
   - Consider using pytest-xdist for parallel test execution
   - Use pytest-cov to ensure adequate test coverage
   - Profile slow tests and optimize them with better fixtures

3. **CI/CD Integration**:
   - Update CI/CD pipelines to use pytest's XML output for better reporting
   - Configure test result visualization in your CI environment
   - Set up automated test failure notifications

### Managing Test Coverage During Migration

When migrating from nose to pytest, you may notice significant changes in your coverage metrics. This is especially true when converting yield tests to parameterized tests. Here are some tips for managing test coverage during migration:

1. **Establish a Baseline**: Before starting the migration, run coverage on your existing nose tests to establish a baseline.

2. **Track Coverage Changes**: As you migrate tests, compare coverage reports to ensure you're not losing coverage.

3. **Understand Coverage Reporting Differences**: 
   - pytest-cov and nose-cov may calculate coverage differently
   - Parameterized tests often improve coverage metrics as each parameter combination is counted separately
   - Xfailed tests may be treated differently in coverage calculations

4. **Address Coverage Gaps**: If the migration reveals coverage gaps, this is an opportunity to add tests for previously uncovered code.

### Migration Tooling

Creating specialized tools can significantly streamline the migration process, especially for large codebases:

1. **Progress Tracking Tool**: 
   ```python
   # Simple tool to track migration progress
   class MigrationTracker:
       def __init__(self, tracking_file):
           self.tracking_file = tracking_file
           self.data = self._load_data()
           
       def _load_data(self):
           # Load migration status from JSON file
           # Return default data if file doesn't exist
           
       def mark_migrated(self, file_path):
           # Update status for a migrated file
           
       def get_status(self):
           # Return current migration status
   ```

2. **Automated Transformation Tool**:
   ```python
   # Tool to automatically apply common transformations
   def apply_transformations(file_path, transformations):
       with open(file_path, 'r') as f:
           content = f.read()
           
       for pattern, replacement in transformations:
           content = re.sub(pattern, replacement, content)
           
       with open(file_path, 'w') as f:
           f.write(content)
   ```

3. **Test Runner Script**:
   ```python
   #!/usr/bin/env python
   # Script to run tests during migration
   import pytest
   import sys
   
   if __name__ == "__main__":
       test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/"
       sys.exit(pytest.main(["-xvs", test_path]))
   ```

These tools can be customized to fit your project's specific needs and can make a large migration more manageable.

### Handling False Positives in Migration Tracking

When tracking migration progress, you may encounter situations where your tracking system shows tests still using nose, but your automated scanning tools don't find any nose dependencies. This can happen because:

1. **Files were already migrated**: Some files may have been previously migrated from nose without updating the tracking information.

2. **Indirect dependencies**: Tests may not directly import nose but depend on other modules that use nose.

3. **Legacy unittest code**: Tests may be using unittest (which is compatible with pytest) rather than nose, but are counted as "not migrated" in your tracking.

To resolve these discrepancies:

1. **Verify with grep**: Use grep to search for direct nose imports:
   ```bash
   grep -r "import nose\|from nose" --include="*.py" .
   ```

2. **Check with pytest**: Run the tests with pytest after uninstalling nose to see if they still work:
   ```bash
   pip uninstall -y nose && python -m pytest path/to/test_file.py
   ```

3. **Update tracking manually**: If tests are working without nose but are still tracked as "not migrated," update your tracking data manually.

4. **Document assumptions**: Make note of any decisions made about files that were auto-marked as migrated to help future maintainers understand your reasoning.

---

## Comprehensive Guide to Test Isolation

Based on our migration experience, test isolation is one of the most challenging aspects of migrating from nose to pytest. Here's a comprehensive approach to handling isolation issues:

### 1. Creating an Improved Base Test Class

For complex test suites, create an enhanced base class with better isolation features:

```python
class ImprovedTestBase:
    """Base class with better test isolation."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, tmp_path):
        """Setup and teardown with better isolation."""
        # Use pytest's tmp_path fixture for unique test directories
        self.test_dir = os.path.join(str(tmp_path), f"test_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Save original configuration state
        self.original_configs = {}
        for config_name in ['important_setting', 'another_setting']:
            self.original_configs[config_name] = get_config(config_name)
        
        # Setup your test environment
        self.initialize_test_environment()
        
        yield  # Test runs here
        
        # Restore original configurations
        for name, value in self.original_configs.items():
            set_config(name, value)
            
        # Clean up any resources
        self.cleanup_resources()
```

### 2. State Sharing Patterns

When tests or test phases must share state, use these patterns:

#### Pattern 1: Explicit State Transfer
```python
def test_phase1(self):
    # Run first phase
    result = run_operation()
    # Store result for next test
    self.store_result('key1', result)

def test_phase2(self):
    # Get result from previous phase
    result = self.get_stored_result('key1')
    # Continue testing
```

#### Pattern 2: Controlled Global State
```python
class TestClass:
    # Class variable to track current test instance
    current_instance = None
    
    def setup_method(self):
        # Set current instance to this test
        TestClass.current_instance = self
        # Initialize test-specific state
        self.my_state = {}
    
    # Other functions can access state through class reference
    # This avoids issues with closures and lambda functions
```

### 3. Handling Database and File System State

For tests involving databases and file operations:

1. **Use unique directories for each test**:
   ```python
   def test_function(self, tmp_path):
       test_dir = os.path.join(str(tmp_path), f"test_{uuid.uuid4().hex[:8]}")
       # Use this directory for all file operations
   ```

2. **Create fresh contexts for different test phases**:
   ```python
   # For phase 1
   context1 = create_context(directory1)
   run_tests(context1)
   
   # For phase 2 - completely new context
   context2 = create_context(directory2)
   run_tests(context2)
   ```

3. **Flush caches between test phases**:
   ```python
   # Clear any cached state
   context.execute_command('clean_cache')
   # Now run the test
   run_test(context)
   ```

### 4. Dealing with Pickling and Serialization

1. **Avoid lambda functions in serialized contexts**:
   ```python
   # BAD - will cause pickle errors
   context.execute_dynamic(lambda x: some_function(x, parameter))
   
   # GOOD - use named functions
   def wrapper_function(x):
       # Get parameters from a safe place
       return some_function(x, get_parameter())
   
   context.execute_dynamic(wrapper_function)
   ```

2. **Be careful with closures**:
   ```python
   # BAD - closure references local variable
   def outer_function(parameter):
       def inner_function():
           return parameter  # This causes pickle issues
       return inner_function
   
   # GOOD - use class state instead
   class TestClass:
       @classmethod
       def set_parameter(cls, value):
           cls.parameter = value
           
       def inner_function(self):
           return self.__class__.parameter
   ```

### 5. Handling Permission Issues with Example Files

Tests that execute example files as subprocesses may encounter permission issues:

1. Make example files executable: `chmod +x path/to/example.py`
2. Skip tests with permission problems during migration: `@pytest.mark.skip(reason="Permission issues")`
3. Consider modifying the test to use internal APIs instead of subprocess calls for greater test reliability

### 6. Debugging Isolation Issues

When you encounter test isolation problems:

1. **Run tests individually**: Verify they pass in isolation
2. **Run with high verbosity**: `pytest -vv` to see detailed output
3. **Use print debugging**: Add print statements to track state changes
4. **Create test order-aware fixtures**: If needed, use fixtures that know about test order

This guide represents lessons learned from our experience migrating a complex codebase from nose to pytest. These patterns have helped us successfully migrate tests while ensuring they work both individually and in sequence.