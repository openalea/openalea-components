from setuptools import setup, find_packages
#from openalea.deploy.metainfo import read_metainfo

#metadata = read_metainfo('metainfo.ini', verbose=True)
#for key, value in zip(metadata.keys(), metadata.values()):
#    exec("%s = '%s'" % (key, value))

name = 'openalea.image'
version = '2.2.0' # TODO: replace by a version.py
description = 'Image manipulation'
long_description = description+ ' for VisuAlea from the OpenAlea platform.'
authors = 'Jerome Chopard, Eric Moscardi and Christophe Pradal'
authors_email = 'christophe pradal at cirad fr'
url = 'https://openalea.rtfd.io'
license = 'Cecill-C'

pkg_root_dir = 'src'
packages = find_packages('src')
package_dir = dict([('', 'src')])

# Meta information
long_description = '''
Image contains algorithms to play with data images
and visualea nodes to wrap numpy algorithms
'''

###########
#
#		compile QT interfaces
#
###########
import os

# rc_file = "src/image/gui/icons/icons.qrc"
# out_file = "src/image/gui/icons_rc.py"
# os.system("pyrcc4 -o %s %s" % (out_file,rc_file) )

# setup function call
#
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
    keywords='openalea, image',
    # package installation
    packages=packages,
    package_dir=package_dir,
    # Namespace packages creation by deploy
    #namespace_packages=[namespace],
    #create_namespaces=True,
    # tell setup not to create a zip file but install the egg as a directory (recomended to be set to False)
    zip_safe=False,
    # Dependencies
    setup_requires=['openalea.deploy'],
    #install_requires=[],
    #dependency_links=['http://openalea.gforge.inria.fr/pi'],

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data=True,
    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include
    package_data={'': ['*.pyd', '*.so', '*.zip', '*.png', '*.qrc'], },

    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points={
        'wralea': ['openalea.image = openalea.image_wralea',
                   'openalea.image.serial = openalea.image_wralea.serial',
                   'openalea.image.interpolation = openalea.image_wralea.interpolation',
                   'openalea.image.algo = openalea.image_wralea.algo',
                   'openalea.image.registration = openalea.image_wralea.registration',
                   'openalea.image.gui = openalea.image_wralea.gui',
                   'openalea.image.demo = openalea.image_demo_wralea', ],

        'openalea.image': [
            'openalea.image/image = openalea.image.plugin.algo',
        ],

        'oalab.plugin': [
            'oalab/image = openalea.image.plugin.oalab',
        ],

        'oalab.applet': [
            'oalab.applet/image = openalea.image.plugin.applet',
        ],

        'openalea.interface': [
            'openalea.interface/image = openalea.image.plugin.interface',
        ],

    },

)
