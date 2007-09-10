# -*- python -*-
# -*- coding: latin-1 -*-
#
#       TopoMesh : topomesh package
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

from interface.topomesh import InvalidFace,InvalidPoint,InvalidLink,\
				ITopoMesh,IFaceListMesh,IPointListMesh,IMutableMesh
from openalea.container.utils.id_generator import IdGenerator

class StrInvalidFace (InvalidFace) :
	"""
	exception raised when a wrong face id is provided
	"""
	def __init__ (self, fid) :
		InvalidFace.__init__(self,"face %d does not exist" % fid)

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

class TopoMesh (ITopoMesh,IFaceListMesh,IPointListMesh,IMutableMesh) :
	"""
	implementation of a topological mesh
	"""
	__doc__+=ITopoMesh.__doc__
	def __init__ (self) :
		"""
		constructor of an empty mesh
		"""
		self._faces={}
		self._points={}
		self._fid_generator=IdGenerator()
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
	
	def has_face (self, fid) :
		return fid in self._faces
	has_face.__doc__=ITopoMesh.has_face.__doc__
	
	########################################################################
	#
	#		Cell list concept
	#
	########################################################################
	def faces (self, pid=None) :
		if pid is None :
			return self._faces.iterkeys()
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		return iter(self._points[pid])
	faces.__doc__=IFaceListMesh.faces.__doc__
	
	def nb_faces (self, pid=None) :
		if pid is None :
			return len(self._faces)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		return len(self._points[pid])
	nb_cells.__doc__=IFaceListMesh.nb_cells.__doc__
	
	def face_neighbors (self, fid) :
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		neighbors_list=[fid]
		for pid in self._faces[fid] :
			neighbors_list.extend(self._points[pid])
		neighbors=set(neighbors_list)
		neighbors.remove(fid)
		return iter(neighbors)
	face_neighbors.__doc__=IFaceListMesh.face_neighbors.__doc__
	
	def nb_face_neighbors (self, fid) :
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		neighbors_list=[fid]
		for pid in self._faces[fid] :
			neighbors_list.extend(self._points[pid])
		neighbors=set(neighbors_list)
		return len(neighbors)-1
	nb_face_neighbors.__doc__=IFaceListMesh.nb_face_neighbors.__doc__
	
	#########################################################################
	#
	#		Point list concept
	#
	#########################################################################
	def points (self, fid=None) :
		if fid is None :
			return self._points.iterkeys()
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		return iter(self._faces[fid])
	points.__doc__=IPointListMesh.points.__doc__
	
	def nb_points (self, fid=None) :
		if fid is None :
			return len(self._points)
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		return len(self._faces[fid])
	nb_points.__doc__=IPointListMesh.nb_points.__doc__
	
	def point_neighbors (self, pid) :
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		neighbors_list=[pid]
		for fid in self._points[pid] :
			neighbors_list.extend(self._faces[fid])
		neighbors=set(neighbors_list)
		neighbors.remove(pid)
		return iter(neighbors)
	point_neighbors.__doc__=IPointListMesh.point_neighbors.__doc__
	
	def nb_point_neighbors (self, pid) :
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		neighbors_list=[pid]
		for fid in self._points[pid] :
			neighbors_list.extend(self._faces[cid])
		neighbors=set(neighbors_list)
		return len(neighbors)-1
	nb_point_neighbors.__doc__=IPointListMesh.nb_point_neighbors.__doc__
	
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_face (self, fid=None) :
		fid=self._fid_generator.get_id(fid)
		self._faces[fid]=[]
		return fid
	add_face.__doc__=IMutableMesh.add_face.__doc__
	
	def add_point (self, pid=None) :
		pid=self._pid_generator.get_id(pid)
		self._points[pid]=set()
		return pid
	add_point.__doc__=IMutableMesh.add_point.__doc__
	
	def add_link (self, fid, pid) :
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		self._faces[fid].append(pid)
		self._points[pid].add(fid)
	add_link.__doc__=IMutableMesh.add_link.__doc__
	
	def remove_face (self, fid) :
		try :
			self._fid_generator.release_id(fid)
		except KeyError :
			raise StrInvalidFace(fid)
		for pid in self._faces[fid] :
			self._points[pid].remove(fid)
		del self._faces[fid]
	remove_face.__doc__=IMutableMesh.remove_face.__doc__
	
	def remove_point (self, pid) :
		try :
			self._pid_generator.release_id(pid)
		except KeyError :
			raise StrInvalidPoint(pid)
		for fid in self._points[pid] :
			self._faces[fid].remove(pid)
		del self._points[pid]
	remove_point.__doc__=IMutableMesh.remove_point.__doc__
	
	def remove_link (self, fid, pid) :
		if not self.has_face(fid) :
			raise StrInvalidFace(fid)
		if not self.has_point(pid) :
			raise StrInvalidPoint(pid)
		try :
			self._faces[fid].remove(pid)
			self._points[pid].remove(fid)
		except KeyError :
			raise StrInvalidLink(fid,pid)
	remove_link.__doc__=IMutableMesh.remove_link.__doc__


