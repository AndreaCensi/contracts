import os
from setuptools import setup, find_packages

packages = find_packages(where='src')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

short = ('PyContracts is a Python package that allows to declare '
         ' constraints on function parameters and return values. '
         'Contracts can be specified using Python3 annotations, '
         ' or inside a docstring :type: and :rtype: tags. '
         ' PyContracts supports a basic type system, variables binding, '
         ' arithmetic constraints, and has several specialized '
         ' contracts (notably for Numpy arrays), as well as an extension API.') 
    
setup(name='PyContracts',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://andreacensi.github.com/contracts/',

      description = short,
      
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Testing'
      ],
      
      long_description = read('README.txt'),
      keywords = "type checking, value checking, contracts",
      license = "LGPL",

	  version="0.9",
      package_dir={'':'src'},
      packages=['contracts'],
      install_requires=['pyparsing'],
      tests_require=['nose'],
      entry_points={},
)

