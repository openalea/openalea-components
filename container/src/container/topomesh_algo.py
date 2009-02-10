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
This module provide a simple pure python implementation
for a some topomesh algorithms
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

###########################################################
#
#	remove unwanted elements
#
###########################################################
def clean_geometry (mesh) :
	"""
	remove wisps not geometrically defined
	i.e. with no borders
	"""
	for scale in xrange(1,mesh.degree()+1) :
		for wid in list(mesh.wisps(scale)) :
			if mesh.nb_borders(scale,wid) == 0 :
				mesh.remove_wisp(scale,wid)

def clean_orphans (mesh) :
	"""
	remove wisps with no regions
	"""
	for scale in xrange(mesh.degree()-1,-1,-1) :
		for wid in list(mesh.wisps(scale)) :
			if mesh.nb_regions(scale,wid) == 0 :
				mesh.remove_wisp(scale,wid)
###########################################################
#
#	mesh partitioning
#
###########################################################def expand (mesh, scale, wids) :
	"""
	add a layer of wisps around a given set of wisps
	using borders to define the neighborhood
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wisps : a list of wid
	return : a set of wid
	"""
	inside_wisps = set(wisps)
	for wid in wids :
		inside_wisps.update(mesh.border_neighbors(scale,wid))
	return inside_cells

def border (mesh, scale, wids) :#TODO gestion des bords du mesh a preciser
	"""
	compute the outermost layer of wisps around a set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wids : a list of wid
	return : a set of wid
	"""
	inside_wisps = set(wids)
	border = set()
	for wid in wids :
		for bid in mesh.borders(scale,wid) :
			if len(set(mesh.regions(scale-1,bid)) - inside_wisps) > 0 :
				border.add(cid)
	return border

def shrink (mesh, scale, wids) :
	"""
	remove a layer of wisps around a set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wids : a list of wid
	return : a set of wid
	"""
	return set(wids) - border(mesh,scale,wids)

def expand_to_border (mesh, scale, wids) :
	"""
	compute the set of elements that touch the set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wids : a list of wid
	return : a set of wid
	"""
	border = set()
	for wid in wids :
		border.update(mesh.borders(scale,wid))
	return border
	
def expand_to_region (mesh, scale, wids) :
	"""
	compute the set of elements touched by the set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wids : a list of wid
	return : a set of wid
	"""
	cells = set()
	for wid in wids :
		cells.update(mesh.regions(scale,wid))
	return cells

def external_border (mesh, scale, wids) :#TODO verifier coherence avec border
	"""
	compute the list of border elements around this set of wisps
	mesh : a container.topomesh instance
	scale : the scale of cell elements
	wids : a list of wid
	return : a set of wid
	"""
	inside_wisps = set(wids)
	#compute list of borders_elms
	border_elms = expand_to_border(mesh,scale,wids)
	#remove inside borders
	border = []
	for bid in border_elms :
		regions = set(mesh.regions(scale-1,bid))
		if (len(regions) == 1) or (len(regions - inside_wisps) > 0) :
			border.append(bid)
	return border
