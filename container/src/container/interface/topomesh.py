# -*- python -*-
# -*- coding: utf-8 -*-
#
#       ITopoMesh : container package
#
#       Copyright  or Copr. 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provides a topological mesh interface
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

class TopomeshError (Exception) :
	"""Base class for all exception in a topomesh
	"""


class InvalidDart (TopomeshError, KeyError) :
	"""Exception raised when a wrong dart id is provided
	"""


class ITopomesh (object) :
	"""Interface definition of a topological mesh
	
	A mesh is formed of elements called darts separated by
	elements of degree-1
	"""
	
	def degree (self, did) :
		"""Degree of a given dart
		"""
		raise NotImplementedError
	
	def is_valid (self) :
		"""Test wether the mesh fulfill all mesh properties
		"""
		raise NotImplementedError
	
	def has_dart (self, did) :
		"""Return true if the dart specified by its id
		is in mesh
		"""
		raise NotImplementedError
	
	def borders (self, did, degree_offset = 1) :
		"""Iterator on all border of this dart
		"""
		raise NotImplementedError
	
	def nb_borders (self, did, degree_offset = 1) :
		"""Number of border of this dart
		"""
		raise NotImplementedError
	
	def regions (self, did) :
		"""Iterator on all regions this dart separate
		"""
		raise NotImplementedError
	
	def nb_regions (self, did) :
		"""Number of regions this darts separate
		"""
		raise NotImplementedError


class IDartListMesh (object) :
	"""A mesh viewe as a collection of darts
	"""
	
	def darts (self, degree = None) :
		"""Iterator on all darts of a given degree
		
		If degree is None, iterate on all darts in the mesh
		"""
		raise NotImplementedError
	
	def nb_darts (self, degree = None) :
		"""Number of darts of the given degree
		or total number of darts if degree is None
		"""
		raise NotImplementedError


class INeighborhoodMesh (object) :
	"""Implicit neighborhood between darts at the same degree
	"""
	
	def border_neighbors (self, did) :
		"""Iterator on all darts at the same degree
		that share a border with this dart
		"""
		raise NotImplementedError
	
	def nb_border_neighbors (self, did) :
		"""Number of border_neighbors of this dart
		"""
		raise NotImplementedError
	
	def region_neighbors (self, did) :
		"""Iterator on all darts at the same degree
		that share a region with this dart
		"""
		raise NotImplementedError
	
	def nb_region_neighbors (self, did) :
		"""Number of region_neighbors of this dart
		"""
		raise NotImplementedError


class IMutableMesh (object) :
	"""Interface for editing methods on mesh
	"""
	
	def add_dart (self, degree, did = None) :
		"""Add a new dart connected to nothing
		
		if did is None, create a free id
		
		returns used did
		"""
		raise NotImplementedError
	
	def remove_dart (self, did) :
		"""Remove dart from the mesh
		
		Also remove all attached links
		"""
		raise NotImplementedError
	
	def link (self, did, bid) :
		"""Link a dart to its border
		
		:Parameters:
		 - `did` (did) - id of the dart
		 - `bid` (bid) - id of the new border
		"""
		raise NotImplementedError
	
	def unlink (self, did, bid) :
		"""Remove a link between a region and its border
		"""
		raise NotImplementedError












