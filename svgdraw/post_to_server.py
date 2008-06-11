from openalea.deploy import gforge
from glob import glob
from os import path
import getpass

egg_files=glob("dist/*.egg")
if len(egg_files)!=1 :
	raise UserWarning("clean dist directory")

filename=egg_files[0]
print filename
name_end=path.basename(filename).split("-")[1]
release=".".join(name_end.split(".")[:2])

project=43 #vplants
package=path.basename(filename).split("-")[0]#"VPlants-NotReleased"

passwd = getpass.getpass("password:")
gforge.login("chopard",passwd)
print "loged"
print "package"
if gforge.get_package_id(project,package)<0 :
	gforge.add_package(project,package)
print "release"
if gforge.get_release_id(project,package,release)<0 :
	gforge.add_release(project,package,release,"","")
print "add file"
gforge.add_file(43,package,release,filename)
print "added"
gforge.logout()
