# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""setup file for pandas package"""

import os
from setuptools import setup, find_namespace_packages
# find version number in src/openalea/scheduler/version.py
_version = {}
with open("src/openalea/secondnature/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

name = "OpenAlea.SecondNature"
description = "SecondNature package for OpenAlea.."
long_description = "The OpenAlea.SecondNature package is a typical package example to help developper to create their own package, compatible with OpenAlea standards." 
authors = "Daniel Barbeau, Christophe Pradal"
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
    entry_points = {
        'gui_scripts': ['secondnature = openalea.secondnature.main:level_one',],
    }
)


