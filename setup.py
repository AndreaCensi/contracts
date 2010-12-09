from setuptools import setup, find_packages

packages = find_packages(where='src')

setup(name='contracts',
	  version="0.1",
      package_dir={'':'src'},
      packages=['contracts'],
      install_requires=['pyparsing',
                        'numpy', # TODO: make numpy optional?
                        ],
      entry_points={
        #  'console_scripts': [
        #    'pg = procgraph.scripts.pg:main',
        #    'pgdoc = procgraph.scripts.pgdoc:main',
        #    'pgindex = procgraph.scripts.pgindex:main'
        # ]
      },
)


