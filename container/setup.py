
import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"


# Header

# Setup script

# Package name
name = 'container'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '2.0.2'

# Description
description= 'Basic data structures in OpenAlea.'
long_description= '''
Container is a set of data structures used in openalea
such as : graph, grid, topomesh
'''

# Author
author= 'Jerome Chopard'
author_email= 'jerome.chopard@sophia.inria.fr'
url= 'http://openalea.gforge.inria.fr'
license= 'Cecill-C'


# Main setup
setup(
    # Meta data
    name='openalea.container',
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    keywords = '',


    # Define what to execute with scons
    #scons_scripts=['SConstruct'],
    #scons_parameters=["build","build_prefix="+build_prefix],

    # Packages
    namespace_packages = [namespace],
    create_namespaces = True,
    #packages =  [ 'openalea.' + x for x in find_packages('src') ],
    packages =  [ 'openalea.container' ],
    package_dir = { 'openalea.container':  pj('src','container'),
                    '' : 'src'  },

    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so', '*.dylib'],},

    zip_safe= False,

    #lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    #inc_dirs = { 'include' : pj(build_prefix, 'include') },

    #postinstall_scripts = ['',],

    # Scripts
    entry_points = {
        "wralea": ['container.mesh = openalea.container.wralea.mesh',]
              },

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    #install_requires = [],

    pylint_packages = ['src/container', 'src/container/backend', 'src/container/utils', 'src/container/generator', 'src/openalea/iterator', 'src/openalea/traversal']

    )
