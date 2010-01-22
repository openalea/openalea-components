from glob import glob
from os import getcwd
from os.path import join,dirname,basename,splitext
from openalea.misc.list_modules import list_modules

pkg_root = dirname(dirname(getcwd() ) )
pkg_name = basename(pkg_root)

f = open("autosum.rst",'w')
f.write("""
.. this file is dedicated to the reference guide

.. In order to include a module so that it is automatically documented, it must in your python path

.. In other words, sphinx will automatically create the reference guide (using automodule)
   only if it can import the module.

.. Keep the structure of this file as close as possible to the orginal one


.. _%s_reference:

Reference guide
###############
.. contents::
""" % pkg_name)

modules = []

for mod_name in list_modules(join(pkg_root,"src",pkg_name) ) :
	gr = mod_name.split(".")
	if not gr[-1].startswith("_") \
	   and not gr[-1].endswith("_rc") :
		modules.append([pkg_name] + gr)

modules.sort()

for mod_dec in modules :
	full_mod_name = ".".join(mod_dec)
	print full_mod_name
	f.write("""
.. currentmodule:: openalea.%s
""" % full_mod_name)
	title = ":mod:`openalea.%s` module" % full_mod_name
	f.write("\n" + title + "\n" + "=" * len(title) + "\n\n")
	f.write("""
Download the source file :download:`../../src/%s.py`.
""" % join(*mod_dec) )
	f.write("""

.. automodule:: openalea.%s
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :synopsis: doc todo
""" % full_mod_name)

f.close()

