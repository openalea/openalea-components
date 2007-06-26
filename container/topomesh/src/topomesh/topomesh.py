# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Grid : grid package
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
				ITopoMesh,ICellListMesh,IPointListMesh,IMutableMesh
from openalea.container.id_generator import IdGenerator

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
	def __init__ (self, cid, pid) :
		InvalidLink.__init__(self,"cell %d and point %d are not linked" % (cid,pid))

class TopoMesh (ITopoMesh,ICellListMesh,IPointListMesh,IMutableMesh) :
	"""
	implementation of a topological mesh
	"""
	__doc__+=ITopoMesh.__doc__
	def __init__ (self) :
		"""
		constructor of an empty mesh
		"""
		self._cells={}
		self._points={}
		self._cid_generator=IdGenerator()
		self._pid_generator=IdGenerator()
	
	########################################################################
	#
	#		Mesh concept
	#
	########################################################################
	def is_valid (self) :
		return True
	is_valid.__doc__=ITopoMesh.is_valid.__doc__
	
	def has_point (self, pid) :
		return pid in self._points
	has_point.__doc__=ITopoMesh.has_point.__doc__
	
	def has_cell (self, cid) :
		return cid in self._cells
	has_cell.__doc__=ITopoMesh.has_cell.__doc__
	
	########################################################################
	#
	#		Cell list concept
	#
	########################################################################
	def cells (self, pid=None) :
		if pid is None :
			return self._cells.iterkeys()
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		return iter(self._points[pid])
	cells.__doc__=ICellListMesh.cells.__doc__
	
	def nb_cells (self, pid=None) :
		if pid is None :
			return len(self._cells)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		return len(self._points[pid])
	nb_cells.__doc__=ICellListMesh.nb_cells.__doc__
	
	def cell_neighbors (self, cid) :
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		neighbors_list=[cid]
		for pid in self._cells[cid] :
			neighbors_list.extend(self._points[pid])
		neighbors=set(neighbors_list)
		neighbors.remove(cid)
		return iter(neighbors)
	cell_neighbors.__doc__=ICellListMesh.cell_neighbors.__doc__
	
	def nb_cell_neighbors (self, cid) :
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		s=set([cid])
		for pid in self._cells[cid] :
			s.union(self._points[pid])
		return len(s)-1
	nb_cell_neighbors.__doc__=ICellListMesh.nb_cell_neighbors.__doc__
	
	#########################################################################
	#
	#		Point list concept
	#
	#########################################################################
	def points (self, cid=None) :
		if cid is None :
			return self._points.iterkeys()
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		return iter(self._cells[cid])
	points.__doc__=IPointListMesh.points.__doc__
	
	def nb_points (self, cid=None) :
		if cid is None :
			return len(self._points)
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		return len(self._cells[cid])
	nb_points.__doc__=IPointListMesh.nb_points.__doc__
	
	def point_neighbors (self, pid) :
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		neighbors_list=[pid]
		for cid in self._points[pid] :
			neighbors_list.extend(self._cells[cid])
		neighbors=set(neighbors_list)
		neighbors.remove(pid)
		return iter(neighbors)
	point_neighbors.__doc__=IPointListMesh.point_neighbors.__doc__
	
	def nb_point_neighbors (self, pid) :
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		s=set([pid])
		for cid in self._points[pid] :
			s.union(self._cells[cid])
		return len(s)-1
	nb_point_neighbors.__doc__=IPointListMesh.nb_point_neighbors.__doc__
	
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_cell (self, cid=None) :
		cid=self._cid_generator.get_id(cid)
		self._cells[cid]=set()
		return cid
	add_cell.__doc__=IMutableMesh.add_cell.__doc__
	
	def add_point (self, pid=None) :
		pid=self._pid_generator.get_id(pid)
		self._points[pid]=set()
		return pid
	add_point.__doc__=IMutableMesh.add_point.__doc__
	
	def add_link (self, cid, pid) :
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		self._cells[cid].add(pid)
		self._points[pid].add(cid)
	add_link.__doc__=IMutableMesh.add_link.__doc__
	
	def remove_cell (self, cid) :
		try :
			self._cid_generator.release_id(cid)
		except KeyError :
			raise StrInvalidCell(cid)
		for pid in self._cells[cid] :
			self._points[pid].remove(cid)
		del self._cells[cid]
	remove_cell.__doc__=IMutableMesh.remove_cell.__doc__
	
	def remove_point (self, pid) :
		try :
			self._pid_generator.release_id(pid)
		except KeyError :
			raise StrInvalidPoint(pid)
		for cid in self._points[pid] :
			self._cells[cid].remove(pid)
		del self._points[pid]
	remove_point.__doc__=IMutableMesh.remove_point.__doc__
	
	def remove_link (self, cid, pid) :
		if not self.has_cell(cid) :
			raise StrInvalidCell(cid)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		try :
			self._cells[cid].remove(pid)
			self._points[pid].remove(cid)
		except KeyError :
			raise StrInvalidLink(cid,pid)
	remove_link.__doc__=IMutableMesh.remove_link.__doc__


