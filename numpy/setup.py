# -*- coding: utf-8 -*-
"""setup file for stdlib package"""

import os
from setuptools import setup, find_namespace_packages

pj = os.path.join

# find version number in src/openalea/numpy_wralea/version.py
_version = {}
with open("src/openalea/numpy_wralea/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

project = 'openalea'
name = 'OpenAlea.Numpy'
namespace = 'openalea'
package = 'numpy'
description = 'Numpy modules for Visualea'
long_description = 'Export some methods from NumPy to use in Visualea'
authors = 'OpenAlea consortium'
authors_email = 'christophe pradal at cirad fr, Eric Moscardi at sophia inria fr, Thomas Cokelaer at sophia inria fr, Daniel Barbeau at sophia inria fr'
url = 'https://github.com/openalea/openalea-components'
license = 'Cecill-C'

packages = find_namespace_packages(where='src', include=['openalea.*'])
package_dir = {'':'src'}

setup_requires = ['openalea.deploy']
install_requires = []


setup(
    name=name,
    version=version,
    description=description,
    long_description = long_description,
    author = authors,
    author_email = authors_email,
    url = url,
    license = license,
    keywords = '',	

    packages=packages,
    package_dir=package_dir,

    # Namespace packages creation by deploy
    #namespace_packages = [namespace],
    #create_namespaces = True,
    zip_safe= False,
    
    # Dependencies
    setup_requires = setup_requires,
    install_requires = install_requires,

    include_package_data = True,

    # entry_points
    entry_points = {
        "wralea": ['openalea.numpy = openalea.numpy_wralea',
                   'openalea.numpy.random = openalea.numpy_wralea.random',
                   'openalea.numpy.creation = openalea.numpy_wralea.creation',
                   'openalea.numpy.infos = openalea.numpy_wralea.infos',
                   'openalea.numpy.input_output = openalea.numpy_wralea.input_output',
                   'openalea.numpy.manipulation = openalea.numpy_wralea.manipulation',
                   'openalea.numpy.math = openalea.numpy_wralea.math',
                   'openalea.numpy.sorting_searching = openalea.numpy_wralea.sorting_searching',
                   'openalea.numpy.window = openalea.numpy_wralea.window',
                   'openalea.numpy.demo = openalea.numpy_demo_wralea',
                   'openalea.numpy.test = openalea.numpy_test_wralea',
              ],
        },

#    pylint_packages = [ 'src' + os.sep + x.replace('.',os.sep) for x in find_packages('src')],

    )
