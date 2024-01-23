# -*- coding: utf-8 -*-
"""setup file for pandas package"""
__revision__ = "$Id$"

import os
from setuptools import setup, find_namespace_packages
# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/pandas_wralea/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

name = "OpenAlea.Pandas"
description = "Pandas modules for Visualea."
long_description = "Interfaces some of the `Pandas <http://pandas.pydata.org/>`_ functionalities as nodes in VisuAlea." 
authors = "Christophe Pradal"
authors_email = "christophe.pradal at cirad.fr"
url = "http://openalea.rtfd.io"
license = "Cecill-C"

packages = find_namespace_packages(where='src', include=['openalea.*'])

setup(
    name=name,
    version=version,
    description=description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,

    packages = packages,
    package_dir={ '' : 'src' },
    include_package_data = True,
    zip_safe = False,
    package_data = {'' : ['*.csv'],},

    entry_points = {
        "wralea": ['openalea.pandas = openalea.pandas_wralea'],
    }
)
