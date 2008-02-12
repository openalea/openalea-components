# -*- python -*-
# -*- coding: latin-1 -*-
#
#       ITopoMesh : topomesh package
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
This module provide a topological mesh interface
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

class TopomeshError (Exception) :
	"""
	base class for all exception in a topomesh
	"""

class InvalidCell (TopomeshError,KeyError) :
	"""
	exception raised when a wrong cell id is provided
	"""

class InvalidPoint (TopomeshError,KeyError) :
	"""
	exception raised when a wrong point id is provided
	"""

class InvalidLink (TopomeshError,KeyError) :
	"""
	exception raised when a link between a cell and a point does not exist
	"""

class ITopomesh (object) :
	"""
	interface definition of a topological mesh
	a mesh links elements of two separate sets E1 (cells) and E2 (points)
	it thus define an implicit neighborhood between elements
	of the same set as two elements of E1 (resp E2) that share
	the same element of E2 (resp E1)
	"""
	def is_valid (self) :
		"""
		test wether the mesh fulfill all mesh properties
		"""
		raise NotImplementedError
	
	def has_point (self, pid) :
		"""
		return true if the point
		specified by its id is in mesh
		"""
		raise NotImplementedError
	
	def has_cell (self, cid) :
		"""
		return true if the cell
		specified by its id is in mesh
		"""
		raise NotImplementedError
	
	def has_link (self, lid) :
		"""
		return True if the link
		specified by its id is in the mesh
		"""
		raise NotImplementedError

class ILinkMesh (object) :
	"""
	explicit links
	"""
	def links (self) :
		"""
		iterator on all links in the mesh
		return : iter of lid
		"""
		raise NotImplementedError
	
	def cell_links (self, cid) :
		"""
		iterator on all links outside a given cell
		return : iter of lid
		"""
		raise NotImplementedError
	
	def nb_cell_links (self, cid) :
		"""
		number of links attached to this cell
		return : int
		"""
		raise NotImplementedError
	
	def point_links (self, pid) :
		"""
		iterator on all links inside a given point
		return : iter of lid
		"""
		raise NotImplementedError
	
	def nb_point_links (self, cid) :
		"""
		number of links attached to this point
		return : int
		"""
		raise NotImplementedError
	
	def cell (self, lid) :
		"""
		cell corresponding to the source of the link
		return : cid
		"""
		raise NotImplementedError
	
	def point (self, lid) :
		"""
		point corresponding to the target of the link
		return : pid
		"""
		raise NotImplementedError

class ICellListMesh (object) :
	"""
	mesh view as a collection of cells
	"""
	def cells (self, pid=None) :
		"""
		iterator on cells linked to a given point
		or all cells if pid is None
		"""
		raise NotImplementedError
	
	def nb_cells (self, pid=None) :
		"""
		number of cells around a point
		or total number of cell if pid is None
		"""
		raise NotImplementedError
	
	def cell_neighbors (self, cid) :
		"""
		iterator on all implicit neighbors of a cell
		"""
		raise NotImplementedError
	
	def nb_cell_neighbors (self, cid) :
		"""
		nb of implicit neighbors of a cell
		"""
		raise NotImplementedError

class IPointListMesh (object) :
	"""
	mesh view as a collection of points
	"""
	def points (self, cid=None) :
		"""
		iterator on point around a given cell
		or all points if cid is None
		"""
		raise NotImplementedError
	
	def nb_points (self, cid=None) :
		"""
		number of cells around a point
		or total number of points if cid is None
		"""
		raise NotImplementedError
	
	def point_neighbors (self, pid) :
		"""
		iterator on all implicit neighbors of a point
		"""
		raise NotImplementedError
	
	def nb_point_neighbors (self, pid) :
		"""
		number of implicit neighbors of a point
		"""
		raise NotImplementedError

class IMutableMesh (object) :
	"""
	interface for editing methods on mesh
	"""
	def add_cell (self, cid=None) :
		"""
		add a new cell connected to nothing
		if cid is None, create a free id
		return used cid
		"""
		raise NotImplementedError
	
	def remove_cell (self, cid) :
		"""
		remove a cell and all the references to attached points
		do not remove attached points
		"""
		raise NotImplementedError
	
	def remove_point (self, pid) :
		"""
		remove a point and all the references to attached cells
		do not remove attached cells
		"""
		raise NotImplementedError
	
	def add_point (self, pid=None) :
		"""
		add a new point connected to nothing
		if pid is None, create a free id
		return used pid
		"""
		raise NotImplementedError
	
	def add_link (self, cid, pid, lid=None) :
		"""
		add a link between a cell and a point
		cell and point must already exist in the mesh
		return the link id used
		"""
		raise NotImplementedError
	
	def remove_link (self, lid) :
		"""
		remove a link between a cell and a point
		"""
		raise NotImplementedError

