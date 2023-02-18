# -*- coding: utf-8 -*-
"""setup file for stdlib package"""

import os
from setuptools import setup, find_packages


name = 'OpenAlea.StdLib'
package = 'stdlib'
description = 'OpenAlea standard logical component library.'
long_description = 'OpenAlea standard logical component library from Python'
authors = 'OpenAlea consortium'
authors_email = 'christophe.pradal@cirad fr'
url = 'https://github.com/openalea/openalea-components'
license = 'Cecill-C'
__license__ = license

# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

setup(
    name=name,
    version=version,
    description=description, 
    long_description = long_description,
    author = authors,
    author_email = authors_email,
    url = url,
    license = license,

    zip_safe=False,

    packages=find_packages('src'),

    package_dir={'':'src' },

    # Add package platform libraries if any
    include_package_data=True,
    package_data = {'' : ['*.csv'],},

    # Dependencies
    setup_requires = ['openalea.deploy'],

    # entry_points
    entry_points = {
        "wralea": ['openalea.color = openalea.color', 
                   'openalea.csv = openalea.csv', 
                   'openalea.string = openalea.string',
                   'openalea.data = openalea.data',
                   'openalea.datafile = openalea.datafile',
                   'openalea.file = openalea.file',
                   'openalea.functional = openalea.functional',
                   'openalea.math = openalea.math', 
                   'openalea.model = openalea.model',
                   'openalea.pickling = openalea.pickling', 
                   'openalea.plotools = openalea.plotools',
                   'openalea.python = openalea.python',
                   'openalea.spatial = openalea.spatial',
                   'openalea.stand = openalea.stand',
                   'openalea.stat = openalea.stat',
                   'openalea.system = openalea.system',
                   'openalea.tutorial = openalea.tutorial',
                   'openalea.tutorial.design pattern = openalea.tutorial.pattern',
                   'openalea.tutorial.functional = openalea.tutorial.functional',
                   'openalea.tutorial.multiprocess = openalea.tutorial.multiprocess',
                   'openalea.multiprocessing = openalea.multiprocessing',
                   'openalea.path = openalea.path',

                   # Deprecated
                   'catalog.color = deprecated', 
                   'catalog.data = deprecated',
                   'catalog.csv = deprecated', 
                   'catalog.file = deprecated',
                   'catalog.functional = deprecated',
                   'catalog.math = deprecated', 
                   'catalog.model = deprecated',
                   'catalog.pickling = deprecated', 
                   'catalog.python = deprecated',
                   'catalog.string = deprecated',
              ],
        },
    )


