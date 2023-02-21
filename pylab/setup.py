# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 2249 2010-02-08 17:27:37Z cokelaer $"

import sys
import os

from setuptools import setup, find_packages

# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/oapylab/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

name = 'OpenAlea.Pylab'
package = 'pylab'
description= 'Pylab interface'
long_description= 'Pylab interface provides a set of nodes that provide pylab tools within OpenAlea'
authors= 'Thomas Cokelaer, Christophe Pradal'
authors_email = 'christophe.pradal@cirad.fr'
url = 'https://openalea.rtfd.io'
license = 'Cecill-C'

pkgs = find_packages('src')
packages = pkgs
package_dir = {'':'src'}

setup_requires = ['openalea.deploy']
install_requires = []

setup(
    # Meta data (no edition needed if you correctly defined the variables above)
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords = '',	
    
    # package installation
    packages= packages,	
    package_dir= package_dir,

    # Namespace packages creation by deploy
    #namespace_packages = [namespace],
    #create_namespaces = True,
    zip_safe= False,
    
    # Dependencies
    setup_requires = setup_requires,
    install_requires = install_requires,
    
    include_package_data = True,
    
    entry_points = {
            "wralea": [ "pylab = openalea.pylab_main_wralea",
                        "pylab.demo = openalea.pylab_demo_wralea",
                        "pylab.plotting = openalea.pylab_plotting_wralea",
                        "pylab.datasets = openalea.pylab_datasets_wralea",
                        "pylab.decorators = openalea.pylab_decorators_wralea",
                        "pylab.Drawing = openalea.pylab_drawing_wralea",
                        "pylab.test = openalea.pylab_test_wralea",
                        "pylab.patches = openalea.pylab_patches_wralea",
                        "pylab.mplot3d = openalea.pylab_3d_wralea",
            ]
            },

    )


