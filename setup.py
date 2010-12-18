import os
from setuptools import setup, find_packages

packages = find_packages(where='src')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(name='contracts',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://andreacensi.github.com/contracts/',

      description = ("A rich type/value checking system for Python functions. "
                     "Contracts can be specified with a rich syntax, "
                     "either with decorators or directly in docstrings. "),
      long_description = read('README.txt'),
      keywords = "type checking, value checking, contracts",
      license = "LGPL",

	  version="0.1",
      package_dir={'':'src'},
      packages=['contracts'],
      install_requires=['pyparsing'],
      tests_require=['nose'],
      entry_points={},
)


