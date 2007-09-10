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

class TopoMeshError (Exception) :
	"""
	base class for all exception in a topomesh
	"""

class InvalidFace (TopoMeshError,KeyError) :
	"""
	exception raised when a wrong face id is provided
	"""

class InvalidPoint (TopoMeshError,KeyError) :
	"""
	exception raised when a wrong point id is provided
	"""

class InvalidLink (TopoMeshError) :
	"""
	exception raised when a link between a face and a point does not exist
	"""

class ITopoMesh (object) :
	"""
	interface definition of a topological mesh
	a mesh links elements of two separate sets E1 (faces) and E2 (points)
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
	
	def has_face (self, cid) :
		"""
		return true if the face
		specified by its id is in mesh
		"""
		raise NotImplementedError

class IFaceListMesh (object) :
	"""
	mesh view as a collection of faces
	"""
	def faces (self, pid=None) :
		"""
		iterator on faces linked to a given point
		or all faces if pid is None
		"""
		raise NotImplementedError
	
	def nb_faces (self, pid=None) :
		"""
		number of faces around a point
		or total number of faces if pid is None
		"""
		raise NotImplementedError
	
	def face_neighbors (self, fid) :
		"""
		iterator on all implicit neighbors of a face
		"""
		raise NotImplementedError
	
	def nb_face_neighbors (self, fid) :
		"""
		nb of implicit neighbors of a face
		"""
		raise NotImplementedError

class IPointListMesh (object) :
	"""
	mesh view as a collection of points
	"""
	def points (self, fid=None) :
		"""
		iterator on point around a given face
		or all points if fid is None
		"""
		raise NotImplementedError
	
	def nb_points (self, fid=None) :
		"""
		number of faces around a point
		or total number of points if fid is None
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
	def add_face (self, fid=None) :
		"""
		add a new face connected to nothing
		if fid is None, create a free id
		return used fid
		"""
		raise NotImplementedError
	
	def add_point (self, pid=None) :
		"""
		add a new point connected to nothing
		if pid is None, create a free id
		return used pid
		"""
		raise NotImplementedError
	
	def add_link (self, fid, pid) :
		"""
		add a link between a face and a point
		face and point must already exist in the mesh
		"""
		raise NotImplementedError
	
	def remove_face (self, fid) :
		"""
		remove a face and all the references to attached points
		do not remove attached points
		"""
		raise NotImplementedError
	
	def remove_point (self, pid) :
		"""
		remove a point and all the references to attached cells
		do not remove attached cells
		"""
		raise NotImplementedError
	
	def remove_link (self, fid, pid) :
		"""
		remove a link between a face and a point
		"""
		raise NotImplementedError

