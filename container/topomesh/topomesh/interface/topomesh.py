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
This module provide a grid interface
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

class InvalidCell (Exception) :
	"""
	exception raised when a wrong cell id is provided
	"""
	def __init__ (self, cid) :
		raise RuntimeError()

class InvalidPoint (Exception) :
	"""
	exception raised when a wrong point id is provided
	"""
	def __init__ (self, pid) :
		raise RuntimeError()

class InvalidLink (Exception) :
	"""
	exception raised when a link between a cell and a point does not exist
	"""
	def __init__ (self, cid, pid) :
		raise RuntimeError()

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
		raise RuntimeError()
	
	########################################################################
	#
	#		Mesh concept
	#
	########################################################################
	def is_valid (self) :
		"""
		test wether the mesh fulfill all mesh properties
		"""
		raise RuntimeError()
	
	def has_point (self, pid) :
		"""
		return true if the point
		specified by its id is in mesh
		"""
		raise RuntimeError()
	
	def has_cell (self, cid) :
		"""
		return true if the cell
		specified by its id is in mesh
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def nb_cells (self, pid=None) :
		"""
		number of cells around a point
		or total number of cell if pid is None
		"""
		raise RuntimeError()
	
	def cell_neighbors (self, cid) :
		"""
		iterator on all implicit neighbors of a cell
		"""
		raise RuntimeError()
	
	def nb_cell_neighbors (self, cid) :
		"""
		nb of implicit neighbors of a cell
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def nb_points (self, cid=None) :
		"""
		number of cells around a point
		or total number of points if cid is None
		"""
		raise RuntimeError()
	
	def point_neighbors (self, pid) :
		"""
		iterator on all implicit neighbors of a point
		"""
		raise RuntimeError()
	
	def nb_point_neighbors (self, pid) :
		"""
		number of implicit neighbors of a point
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def add_point (self, pid=None) :
		"""
		add a new point connected to nothing
		if pid is None, create a free id
		return used pid
		"""
		raise RuntimeError()
	
	def add_link (self, cid, pid) :
		"""
		add a link between a cell and a point
		cell and point must already exist in the mesh
		"""
		raise RuntimeError()
	
	def remove_cell (self, cid) :
		"""
		remove a cell and all the references to attached points
		do not remove attached points
		"""
		raise RuntimeError()
	
	def remove_point (self, pid) :
		"""
		remove a point and all the references to attached cells
		do not remove attached cells
		"""
		raise RuntimeError()
	
	def remove_link (self, cid, pid) :
		"""
		remove a link between a cell and a point
		"""
		raise RuntimeError()

