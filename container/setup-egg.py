# -*- coding: iso-8859-15 -*-
import os, sys
from setuptools import setup
pj = os.path.join


##############
# Setup script

# Package name
name= 'container'

#openalea namespace
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
# major.minor.patch
# alpha: patch + 'a'+ 'number'
# beta: patch= patch + 'b' + 'number'
major= '1'
minor= '1'
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

# For other meta-information, please read the Python distutils documentation.

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
    
    namespace_packages = [namespace],
    create_namespaces = True,

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
    include_package_data = True,
    zip_safe = False,

    )


