
import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"


# Header

# Setup script

# Package name
name = 'openalea.container'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '2.0.0' 

# Description
description= 'basic data structures in OpenAlea.' 
long_description= '''
containers is a set of data structures used in openalea
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
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    keywords = '',

    
    # Define what to execute with scons
    scons_scripts=['SConstruct'],
    scons_parameters=["build","build_prefix="+build_prefix],

    # Packages
    namespace_packages = [namespace],
    create_namespaces = True,
    packages =  [ 'openalea.' + x for x in find_packages('src') ],
    package_dir = { 'openalea.container':  pj('src','container'),  }, 

    
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so'],},

    zip_safe= False,

    lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    inc_dirs = { 'include' : pj(build_prefix, 'include') },
    
    #postinstall_scripts = ['',],

    # Scripts
#    entry_points = { 'console_scripts': [
#                            'fake_script = openalea.fakepackage.amodule:console_script', ],
#                      'gui_scripts': [
#                            'fake_gui = openalea.fakepackage.amodule:gui_script',]},

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    #install_requires = [],


    )


