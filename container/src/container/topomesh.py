# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Topomesh : topomesh package
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
for a topomesh interface
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

from interface.topomesh import InvalidCell,InvalidPoint,InvalidLink,\
				ITopomesh,ILinkMesh,ICellListMesh,IPointListMesh,IMutableMesh
from utils import IdDict

class StrInvalidCell (InvalidCell) :
	"""
	exception raised when a wrong cell id is provided
	"""
	def __init__ (self, cid) :
		InvalidCell.__init__(self,"cell %d does not exist" % cid)

class StrInvalidPoint (InvalidPoint) :
	"""
	exception raised when a wrong point id is provided
	"""
	def __init__ (self, pid) :
		InvalidPoint.__init__(self,"point %d does not exist" % pid)

class StrInvalidLink (InvalidLink) :
	"""
	exception raised when a link between a cell and a point does not exist
	"""
	def __init__ (self, lid) :
		InvalidLink.__init__(self,"link %d does not exist" % lid)

class Topomesh (ITopomesh,ILinkMesh,ICellListMesh,IPointListMesh,IMutableMesh) :
	"""
	implementation of a topological mesh
	"""
	__doc__+=ITopomesh.__doc__
	def __init__ (self) :
		"""
		constructor of an empty mesh
		"""
		self._cell_links=IdDict()
		self._point_links=IdDict()
		self._link_extremities=IdDict()
	
	########################################################################
	#
	#		Mesh concept
	#
	########################################################################
	def is_valid (self) :
		return True
	is_valid.__doc__=ITopomesh.is_valid.__doc__
	
	def has_point (self, pid) :
		return pid in self._point_links
	has_point.__doc__=ITopomesh.has_point.__doc__
	
	def has_cell (self, cid) :
		return cid in self._cell_links
	has_cell.__doc__=ITopomesh.has_cell.__doc__
	
	def has_link (self, lid) :
		return lid in self._link_extremities
	has_link.__doc__=ITopomesh.has_link.__doc__
	########################################################################
	#
	#		Link Mesh concept
	#
	########################################################################
	def links (self) :
		return self._link_extremities.iterkeys()
	links.__doc__=ILinkMesh.links.__doc__
	
	def cell_links (self, cid) :
		try :
			return iter(self._cell_links[cid])
		except KeyError :
			raise StrInvalidCell(cid)
	cell_links.__doc__=ILinkMesh.cell_links.__doc__
	
	def nb_cell_links (self, cid) :
		try :
			return len(self._cell_links[cid])
		except KeyError :
			raise StrInvalidCell(cid)
	nb_cell_links.__doc__=ILinkMesh.nb_cell_links.__doc__
	
	def point_links (self, pid) :
		try :
			return iter(self._point_links[pid])
		except KeyError :
			raise StrInvalidPoint(pid)
	point_links.__doc__=ILinkMesh.point_links.__doc__
	
	def nb_point_links (self, pid) :
		try :
			return len(self._point_links[pid])
		except KeyError :
			raise StrInvalidPoint(pid)
	nb_point_links.__doc__=ILinkMesh.nb_point_links.__doc__
	
	def cell (self, lid) :
		try :
			return self._link_extremities[lid][0]
		except KeyError :
			raise StrInvalidLink(lid)
	cell.__doc__=ILinkMesh.cell.__doc__
	
	def point (self, lid) :
		try :
			return self._link_extremities[lid][1]
		except KeyError :
			raise StrInvalidLink(lid)
	point.__doc__=ILinkMesh.point.__doc__
	########################################################################
	#
	#		Cell list concept
	#
	########################################################################
	def _cells (self, pid) :
		try :
			for lid in self.point_links(pid) :
				yield self.cell(lid)
		except KeyError :
			raise StrInvalidPoint(pid)
	
	def cells (self, pid=None) :
		if pid is None :
			return self._cell_links.iterkeys()
		else :
			return self._cells(pid)
	cells.__doc__=ICellListMesh.cells.__doc__
	
	def nb_cells (self, pid=None) :
		if pid is None :
			return len(self._cell_links)
		try :
			return len(self._point_links[pid])
		except KeyError :
			raise StrInvalidPoint(pid)
	nb_cells.__doc__=ICellListMesh.nb_cells.__doc__
	
	def cell_neighbors (self, cid) :
		neighbors=set()
		for pid in self.points(cid) :
			neighbors|=set(self.cells(pid))
		neighbors.remove(cid)
		return iter(neighbors)
	cell_neighbors.__doc__=ICellListMesh.cell_neighbors.__doc__
	
	def nb_cell_neighbors (self, cid) :
		neighbors=set()
		for pid in self.points(cid) :
			neighbors|=set(self.cells(pid))
		return len(neighbors)-1
	nb_cell_neighbors.__doc__=ICellListMesh.nb_cell_neighbors.__doc__
	
	#########################################################################
	#
	#		Point list concept
	#
	#########################################################################
	def _points (self, cid) :
		try :
			for lid in self.cell_links(cid) :
				yield self.point(lid)
		except KeyError :
			raise StrInvalidCell(cid)
	
	def points (self, cid=None) :
		if cid is None :
			return self._point_links.iterkeys()
		else :
			return self._points(cid)
	points.__doc__=IPointListMesh.points.__doc__
	
	def nb_points (self, cid=None) :
		if cid is None :
			return len(self._point_links)
		try :
			return len(self._cells[cid])
		except KeyError :
			raise StrInvalidCell(cid)
	nb_points.__doc__=IPointListMesh.nb_points.__doc__
	
	def point_neighbors (self, pid) :
		neighbors=set()
		for cid in self.cells(pid) :
			neighbors|=set(self.points(cid))
		neighbors.remove(pid)
		return iter(neighbors)
	point_neighbors.__doc__=IPointListMesh.point_neighbors.__doc__
	
	def nb_point_neighbors (self, pid) :
		neighbors=set()
		for cid in self.cells(pid) :
			neighbors|=set(self.points(cid))
		return len(neighbors)-1
	nb_point_neighbors.__doc__=IPointListMesh.nb_point_neighbors.__doc__
	
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_cell (self, cid=None) :
		return self._cell_links.add(set(),cid)
	add_cell.__doc__=IMutableMesh.add_cell.__doc__
	
	def remove_cell (self, cid) :
		for lid in list(self.cell_links(cid)) :
			self.remove_link(lid)
		del self._cell_links[cid]
	remove_cell.__doc__=IMutableMesh.remove_cell.__doc__
	
	def add_point (self, pid=None) :
		return self._point_links.add(set(),pid)
	add_point.__doc__=IMutableMesh.add_point.__doc__
	
	def remove_point (self, pid) :
		for lid in list(self.point_links(pid)) :
			self.remove_link(lid)
		del self._point_links[pid]
	remove_point.__doc__=IMutableMesh.remove_point.__doc__
	
	def add_link (self, cid, pid, lid=None) :
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		lid=self._link_extremities.add( (cid,pid),lid )
		self._cell_links[cid].add(lid)
		self._point_links[pid].add(lid)
		return lid
	add_link.__doc__=IMutableMesh.add_link.__doc__
	
	def remove_link (self, lid) :
		cid=self.cell(lid)
		self._cell_links[cid].remove(lid)
		pid=self.point(lid)
		self._point_links[pid].remove(lid)
		del self._link_extremities[lid]
	remove_link.__doc__=IMutableMesh.remove_link.__doc__


