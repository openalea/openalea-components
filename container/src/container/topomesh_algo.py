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
#	mesh edition
#
###########################################################
def clean_remove (mesh, scale, wid) :
	"""
	remove a wisp and all wisps of smaller degree
	that are no longer connected to anything
	"""
	wid_list = [wid]
	for deg in xrange(scale,0,-1) :
		orphans = set()
		for wid in wid_list :
			bids = tuple(mesh.borders(deg,wid))
			mesh.remove_wisp(deg,wid)
			for bid in bids :
				if mesh.nb_regions(deg-1,bid) == 0 :
					orphans.add(bid)
		wid_list = orphans
	for wid in wid_list :
		mesh.remove_wisp(0,wid)
def merge_wisps (mesh, scale, wid1, wid2) :
	"""
	merge two wisps into a single one
	assertion1 : wisps share a border
	assertion2 : this frontier has only these two wisps as regions
	return wid of newly created wisp
	"""
	#find common frontier that will be removed
	frontier = set(mesh.borders(scale,wid1)) & set(mesh.borders(scale,wid2))
	#test assertion 1
	assert len(frontier) > 0
	#test assertion 2
	for bid in frontier :
		assert mesh.nb_regions(scale-1,bid) == 2
	#create new wisp
	nwid = mesh.add_wisp(scale)
	#connect with regions if needed
	if scale < mesh.degree() :
		for rid in set(mesh.regions(scale,wid1)) | set(mesh.regions(scale,wid2)) :
			mesh.link(scale+1,rid,nwid)
	#connect with borders
	for bid in (set(mesh.borders(scale,wid1)) | set(mesh.borders(scale,wid2))) - frontier :
		mesh.link(scale,nwid,bid)
	#remove old wisps
	clean_remove(mesh,scale,wid1)
	clean_remove(mesh,scale,wid2)
	#return
	return nwid

def flip_edge (mesh, eid) :
	"""
	flip the orientation of an edge
	in a triangulated mesh
	"""
	#definition of local elements
	fid1,fid2 = mesh.regions(1,eid) #work only if planar polygon
	pid3,pid4 = mesh.borders(1,eid)
	pid1, = set(mesh.borders(2,fid1,2)) - set( (pid3,pid4) )
	pid2, = set(mesh.borders(2,fid2,2)) - set( (pid3,pid4) )
	eid13, = set(mesh.borders(2,fid1)) - set(mesh.regions(0,pid3))
	eid14, = set(mesh.borders(2,fid1)) - set(mesh.regions(0,pid4))
	eid23, = set(mesh.borders(2,fid2)) - set(mesh.regions(0,pid3))
	eid24, = set(mesh.borders(2,fid2)) - set(mesh.regions(0,pid4))
	#relink eid
	mesh.unlink(1,eid,pid3)
	mesh.unlink(1,eid,pid4)
	mesh.link(1,eid,pid1)
	mesh.link(1,eid,pid2)
	#relink faces
	mesh.unlink(2,fid1,eid14)
	mesh.unlink(2,fid2,eid23)
	mesh.link(2,fid1,eid23)
	mesh.link(2,fid2,eid14)
###########################################################
#
#	remove unwanted elements
#
###########################################################
def clean_geometry (mesh) :
	"""
	remove wisps not geometrically defined
	i.e. with number of border smaller than scale+1
	return a list of removed elements
	"""
	removed = []
	for scale in xrange(1,mesh.degree()+1) :
		for wid in list(mesh.wisps(scale)) :
			if mesh.nb_borders(scale,wid) < (scale+1) :
				mesh.remove_wisp(scale,wid)
				removed.append( (scale,wid) )
	return removed

def clean_orphans (mesh) :
	"""
	remove wisps with no regions
	return a list of removed elements
	"""
	removed = []
	for scale in xrange(mesh.degree()-1,-1,-1) :
		for wid in list(mesh.wisps(scale)) :
			if mesh.nb_regions(scale,wid) == 0 :
				mesh.remove_wisp(scale,wid)
				removed.append( (scale,wid) )
	return removed

def _find_neighbor (mesh, scale, wid, wid_list) :
	"""
	internal function to find a border neighbor
	of wid in the provided list of wid
	"""
	for ind,eid in enumerate(wid_list) :
		if wid in set(mesh.border_neighbors(scale,eid)) :
			return ind
	raise ValueError("no neighbor find in this list")

def clean_duplicated_borders (mesh, outer = True) :
	"""
	replace all wisps that account for the same
	border between two regions by a unique wisp
	
	if outer is True, then even elements that share
	only one region are simplified
	"""
	for scale in xrange(1,mesh.degree()) :
		#find duplicated borders
		bd = {}
		for wid in mesh.wisps(scale) :
			rids = list(mesh.regions(scale,wid))
			rids.sort()
			key = tuple(rids)
			try :
				bd[key].append(wid)
			except KeyError :
				bd[key] = [wid]
		if outer :
			duplicated = [v for k,v in bd.iteritems() if len(v) > 1]
		else :
			duplicated = [v for k,v in bd.iteritems() if len(k) > 1 and len(v) > 1]
		#merge duplicates
		for wids in duplicated :
			wid1 = wids.pop(0)
			while len(wids) > 0 :
				try :
					#find a neighbor of wid
					ind = _find_neighbor(mesh,scale,wid1,wids)
					wid2 = wids.pop(ind)
					#merge wid1 and wid2
					wid1 = merge_wisps(mesh,scale,wid1,wid2)
				except ValueError :
					print "pb"
					wid1 = wids.pop(0)

def clean_duplicated_borders (mesh, outer = True) :
	"""
	replace all wisps that account for the same
	border between two regions by a unique wisp
	
	if outer is True, then even elements that share
	only one region are simplified
	"""
	for deg in xrange(mesh.degree()-1,mesh.degree()-2,-1) :
		#find duplicated borders
		bd = {}
		for wid in mesh.wisps(deg) :
			rids = list(mesh.regions(deg,wid))
			rids.sort()
			key = tuple(rids)
			try :
				bd[key].append(wid)
			except KeyError :
				bd[key] = [wid]
		if outer :
			duplicated = [(k,v) for k,v in bd.iteritems() if len(v) > 1]
		else :
			duplicated = [(k,v) for k,v in bd.iteritems() if len(k) > 1 and len(v) > 1]
		#replace duplicates by a single element
		for rids,wids in duplicated :
			#create new single element
			nwid = mesh.add_wisp(deg)
			for rid in rids :
				mesh.link(deg+1,rid,nwid)
			#find external border of wids
			for bid in external_border(mesh,deg,wids) :
				mesh.link(deg,nwid,bid)
			#remove duplicates
			for wid in wids :
				clean_remove(mesh,deg,wid)

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
	inside_wisps = set(wids)
	for wid in wids :
		inside_wisps.update(mesh.border_neighbors(scale,wid))
	return inside_wisps

def border (mesh, scale, wids, outer = False) :
	"""
	compute the outermost layer of wisps around a set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisp elements
	wids : a list of wid
	outer : a boolean that tells wether or not wisps with only one regions are considered
	return : a set of wid
	"""
	inside_wisps = set(wids)
	border = set()
	for wid in wids :
		for bid in mesh.borders(scale,wid) :
			if outer and mesh.nb_regions(scale-1,bid) == 1 :
				border.add(wid)
			elif len(set(mesh.regions(scale-1,bid)) - inside_wisps) > 0 :
				border.add(wid)
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
	borders = set()
	for wid in wids :
		borders.update(mesh.borders(scale,wid))
	return borders
	
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

def external_border (mesh, scale, wids) :
	"""
	compute the list of border elements around this set of wisps
	mesh : a container.topomesh instance
	scale : the scale of wisps elements
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
