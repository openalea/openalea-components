# -*- coding: utf-8 -*-
"""setup file for pandas package"""

import os
from setuptools import setup, find_namespace_packages
# find version number in src/openalea/scheduler/version.py
_version = {}
with open("src/openalea/scheduler/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

name = "OpenAlea.Scheduler"
description = "scheduler package for OpenAlea."
long_description = "The scheduler package implement the management of tasks. Used for simulations purpose." 
authors = "Jerome Chopard, Christophe Pradal"
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
        "wralea": ['openalea.scheduler = openalea.scheduler_wralea'],
    }
)
