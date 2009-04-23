# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Topomesh : container package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provide a simple way to serialize a mesh in a txt file
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

from topomesh import Topomesh
from utils.utils_txt import write_description,read_description

def topomesh_to_txt (f, mesh, description) :
    """
    write the txt representation of a topomesh
    """
    #create base node
    f.write("BEGIN topomesh degree %d\n" % mesh.degree())
    f.write("\n")
    #description
    write_description(f,description)
    f.write("\n")

    #write wisps
    for deg in xrange(mesh.degree() + 1) :
        f.write("BEGIN wisp degree %d\n" % deg)
        for wid in mesh.wisps(deg) :
            f.write("id %d\n" % wid)
        f.write("END wisp degree %d\n" % deg)

    #write links between wisps
    f.write("BEGIN decomposition\n")
    for deg in xrange(1,mesh.degree() + 1) :
        for wid in mesh.wisps(deg) :
            for bid in mesh.borders(deg,wid) :
                f.write("link degree %d wid %d bid %d\n" % (deg,wid,bid))
    f.write("END decomposition\n")

    f.write("END topomesh\n")

    #return
    return f

def txt_to_topomesh (f, method = "set") :
    """
    retrieve the topomesh structure from txt stream
    returns topomesh,description
    """
    #create topomesh
    line = ""
    while "BEGIN topomesh" not in line :
        line = f.readline()
    deg = int(line.split(" ")[3])
    mesh = Topomesh(deg,method)
    #read description
    descr = read_description(f)

    #wisps
    for i in xrange(mesh.degree() + 1) :
        line = ""
        while "BEGIN wisp" not in line :
            line = f.readline()
        deg = int(line.split(" ")[3])
        line = f.readline()
        while "END wisp" not in line :
            mesh.add_wisp(deg,int(line.split(" ")[1]) )
            line = f.readline()

    #links
    line = ""
    while "BEGIN decomposition" not in line :
        line = f.readline()
    line = f.readline()
    while "END decomposition" not in line :
        gr = line.split(" ")
        mesh.link(int(gr[2]),int(gr[4]),int(gr[6]))
        line = f.readline()

    #return
    return mesh,descr

def write_topomesh (filename, mesh, description) :
    """
    write a topomesh in a file using a txt representation
    """
    f = open(filename,'w')
    topomesh_to_txt(f,mesh,description)
    f.close()

def read_topomesh (filename, method = "set") :
    """
    read a topomesh stored in a file as a txt representation
    """
    f = open(filename,'r')
    mesh,descr = txt_to_topomesh(f,method)
    f.close()
    return mesh,descr
