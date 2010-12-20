import os
from setuptools import setup, find_packages

packages = find_packages(where='src')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(name='PyContracts',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://andreacensi.github.com/contracts/',

      description = ("A rich type/value checking system for Python functions. "
                     "Contracts are specified with a rich DSL syntax, "
                     " directly in docstrings with the "
                     " `:type:' and `:rtype:' annotations. "),
      
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

	  version="0.1",
      package_dir={'':'src'},
      packages=['contracts'],
      install_requires=['pyparsing'],
      tests_require=['nose'],
      entry_points={},
)

#  Intended Audience :: Science/Research
#  Topic :: Scientific/Engineering
#  Topic :: System :: Clustering
# Topic :: System :: Distributed Computing
# Topic :: System :: Hardware :: Symmetric Multi-processing