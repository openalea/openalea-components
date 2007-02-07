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

from interface import topomesh
from id_generator import IdGenerator

class InvalidCell (Exception) :
	"""
	exception raised when a wrong cell id is provided
	"""
	def __init__ (self, cid) :
		Exception.__init__(self,"cell %d does not exist" % cid)

class InvalidPoint (Exception) :
	"""
	exception raised when a wrong point id is provided
	"""
	def __init__ (self, pid) :
		Exception.__init__(self,"point %d does not exist" % pid)

class InvalidLink (Exception) :
	"""
	exception raised when a link between a cell and a point does not exist
	"""
	def __init__ (self, cid, pid) :
		Exception.__init__(self,"cell %d and point %d are not linked" % (cid,pid))

class TopoMesh (object) :
	"""
	interface definition of a topological mesh
	a mesh links elements of two separate sets E1 (cells) and E2 (points)
	it thus define an implicit neighborhood between elements
	of the same set as two elements of E1 (resp E2) that share
	the same element of E2 (resp E1)
	"""
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
		"""
		test wether the mesh fulfill all mesh properties
		"""
		return True
	
	def has_point (self, pid) :
		"""
		return true if the point
		specified by its id is in mesh
		"""
		return pid in self._points
	
	def has_cell (self, cid) :
		"""
		return true if the cell
		specified by its id is in mesh
		"""
		return cid in self._cells
	
	########################################################################
	#
	#		Cell list concept
	#
	########################################################################
	def cells (self, pid=None) :
		"""
		iterator on cells linked to a given point
		or all cells if pid is None
		"""
		if pid is None :
			return self._cells.iterkeys()
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		return iter(self._points[pid])
	
	def nb_cells (self, pid=None) :
		"""
		number of cells around a point
		or total number of cell if pid is None
		"""
		if pid is None :
			return len(self._cells)
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		return len(self._points[pid])
	
	def cell_neighbors (self, cid) :
		"""
		iterator on all implicit neighbors of a cell
		"""
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		neighbors_list=[]
		for pid in self._cells[cid] :
			neighbors_list.extend(self._points[pid])
		neighbors=set(neighbors_list)
		neighbors.remove(cid)
		return iter(neighbors)
	
	def nb_cell_neighbors (self, cid) :
		"""
		nb of implicit neighbors of a cell
		"""
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		s=set()
		for pid in self._cells[cid] :
			s.union(self._points[pid])
		return len(s)-1
	
	#########################################################################
	#
	#		Point list concept
	#
	#########################################################################
	def points (self, cid=None) :
		"""
		iterator on point around a given cell
		or all points if cid is None
		"""
		if cid is None :
			return self._points.iterkeys()
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		return iter(self._cells[cid])
	
	def nb_points (self, cid=None) :
		"""
		number of cells around a point
		or total number of points if cid is None
		"""
		if cid is None :
			return len(self._points)
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		return len(self._cells[cid])
	
	def point_neighbors (self, pid) :
		"""
		iterator on all implicit neighbors of a point
		"""
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		neighbors_list=[]
		for cid in self._points[pid] :
			neighbors_list.extend(self._cells[cid])
		neighbors=set(neighbors_list)
		neighbors.remove(pid)
		return iter(neighbors)
	
	def nb_point_neighbors (self, pid) :
		"""
		number of implicit neighbors of a point
		"""
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		s=set()
		for cid in self._points[pid] :
			s.union(self._cells[cid])
		return len(s)-1
	
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_cell (self, cid=None) :
		"""
		add a new cell connected to nothing
		if cid is None, create a free id
		return used cid
		"""
		cid=self._cid_generator.get_id(cid)
		self._cells[cid]=set()
		return cid
	
	def add_point (self, pid=None) :
		"""
		add a new point connected to nothing
		if pid is None, create a free id
		return used pid
		"""
		pid=self._pid_generator.get_id(pid)
		self._points[pid]=set()
		return pid
	
	def add_link (self, cid, pid) :
		"""
		add a link between a cell and a point
		cell and point must already exist in the mesh
		"""
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		self._cells[cid].add(pid)
		self._points[pid].add(cid)
	
	def remove_cell (self, cid) :
		"""
		remove a cell and all the references to attached points
		do not remove attached points
		"""
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		for pid in self._cells[cid] :
			self._points[pid].remove(cid)
		del self._cells[cid]
	
	def remove_point (self, pid) :
		"""
		remove a point and all the references to attached cells
		do not remove attached cells
		"""
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		for cid in self._points[pid] :
			self._cells[cid].remove(pid)
		del self._points[pid]
	
	def remove_link (self, cid, pid) :
		"""
		remove a link between a cell and a point
		"""
		if not self.has_cell(cid) :
			raise InvalidCell(cid)
		if not self.has_point(pid) :
			raise InvalidPoint(pid)
		try :
			cell_set.remove(pid)
			point_set.remove(cid)
		except KeyError :
			raise InvalidLink(cid,pid)


