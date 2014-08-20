import os
from setuptools import setup, find_packages

version = "1.6.4"

description = (
'PyContracts is a Python package that allows to declare '
'constraints on function parameters and return values. '
'Contracts can be specified using Python3 annotations, '
'in a decorator, or inside a docstring :type: and :rtype: tags. '
'PyContracts supports a basic type system, variables binding, '
'arithmetic constraints, and has several specialized '
'contracts (notably for Numpy arrays), as well as an extension API.')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

long_description = read('README.rst')

import sys
pyparsing_version_condition = '<'
if sys.version_info[0] >= 3:
    pyparsing_version_condition = '>='
pyparsing = 'pyparsing%s2.0.0' % pyparsing_version_condition


setup(name='PyContracts',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://andreacensi.github.com/contracts/',

      description=description,
      long_description=long_description,
      keywords="type checking, value checking, contracts",
      license="LGPL",

      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Testing'
      ],

    version=version,
      download_url='http://github.com/AndreaCensi/contracts/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[pyparsing, 'decorator'],
      tests_require=['nose'],
      entry_points={},
)

