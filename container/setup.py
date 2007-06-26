# -*- coding: iso-8859-15 -*-

# Header

#Check dependencies

#####################
# Import dependencies

import os, sys
pj= os.path.join

try:
    from openalea import config
except ImportError:
    print """
ImportError : openalea.config not found. 
Please install the openalea package before.	
See http://openalea.gforge.inria.fr
"""
    sys.exit()

try:
    from openalea.distx import setup,Shortcut
except ImportError:
    print """
ImportError : openalea.distx package not found.
Please, first install the openalea.distx package.
See http://openalea.gforge.inria.fr
"""
    sys.exit()


##############
# Setup script

# Package name
name= 'container'

#openalea namespace
namespace=config.namespace 

pkg_name= namespace + '.' + name

# Package version policy
# major.minor.patch
# alpha: patch + 'a'+ 'number'
# beta: patch= patch + 'b' + 'number'
major= '1'
minor= '0'
patch= '0'
version= '%s.%s.%s' % (major, minor, patch)

# Description of the package

# Short description
description= 'Container package for OpenAlea.' 

long_description= '''
A set of widely used containers to share among openalea community.
'''

# Author
author= 'Jérôme Chopard'
author_email= 'jerome.chopard@sophia.inria.fr'

# URL
url= 'http://openalea.gforge.inria.fr/dokuwiki/doku.php?id=packages:container'

# License: License for the starter package.
# Please, choose an OpenSource license for distribution of your package.

# LGPL compatible INRIA license
license= 'Cecill-C' 

# Scons build directory
build_prefix= "build-scons"

# For other meta-information, please read the Python distutils documentation.

# Main setup
setup(
    # Meta data
    name="container",
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    
    # Define what to execute with scons
    # scons is responsible to put compiled library in the write place
    # ( lib/, package/, etc...)
    scons_scripts = [],

    # scons parameters  
    scons_parameters = ["build_prefix="+build_prefix],
    
    namespace=[namespace],

    # pure python  packages
    packages= [ pkg_name,
				pkg_name+'.graph',
				pkg_name+'.graph.interface',

				pkg_name+'.grid',
				pkg_name+'.grid.interface',

				pkg_name+'.topomesh',
				pkg_name+'.topomesh.interface',

				pkg_name+'.utils'],
    # python packages directory
    package_dir= { pkg_name : ".",
                   pkg_name+'.graph' :pj('graph','src','graph'),
                   pkg_name+'.graph.interface' :pj('graph','src','graph','interface'),

                   pkg_name+'.grid' :pj('grid','src','grid'),
                   pkg_name+'.grid.interface' :pj('grid','src','grid','interface'),

                   pkg_name+'.topomesh' :pj('topomesh','src','topomesh'),
                   pkg_name+'.topomesh.interface' :pj('topomesh','src','topomesh','interface'),

                   pkg_name+'.utils' :pj( '.' , 'utils' ),
		   
                   },
                   
    # Add package platform libraries if any
    include_package_lib = True,

    # copy shared data in default OpenAlea directory
    # map of 'destination subdirectory' : 'source subdirectory'
    external_data={},

    # Add shortcuts
    win_shortcuts = [],
    freedesk_shortcuts = [],

    # Windows registery (list of (key, subkey, name, value))
    winreg = []

    )


