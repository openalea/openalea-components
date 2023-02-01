# -*- coding: utf-8 -*-
"""setup file for stdlib package"""
__revision__ = "$Id: $"

import os
from setuptools import setup, find_packages

__license__ = 'Cecill-C'
__revision__ = "$Id: $"

pj = os.path.join

version = '2.0.0'
release = '2.0'
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

pkgs = find_packages('src')
packages = pkgs
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
                   'openalea.numpy.demo = openalea.numpy_demo_wralea',
                   'openalea.numpy.test = openalea.numpy_test_wralea',
              ],
        },

#    pylint_packages = [ 'src' + os.sep + x.replace('.',os.sep) for x in find_packages('src')],

    )
