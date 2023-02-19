import os
pj = os.path.join

from setuptools import setup, find_packages
from openalea.deploy.metainfo import read_metainfo

# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/pkg_builder/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

name = "OpenAlea.PkgBuilder"
description = "Creates a layout for openalea packages based on defined guidelines."
long_description = description # TODO: Read the README.md
authors = "Christophe Pradal"
authors_email = "christophe.pradal at cirad.fr"
url = "http://openalea.rtfd.io"
license = "Cecill-C"

setup(
    name=name,
    version=version,
    description=description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,

    #namespace_packages=['openalea'],

    packages = find_packages('src'),
    package_dir={ '' : 'src' },
    include_package_data = True,
    zip_safe = False,


    entry_points = {
        "console_scripts": [
                 "alea_create_package = openalea.pkg_builder.layout:main",
                 ],
    }

)

