# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Topomesh : container package
#
#       Copyright or  or Copr. 2006 INRIA - CIRAD - INRA
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
This module provide a simple pure python implementation
for a topomesh interface
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

__all__ = ["TopomeshError"
         , "InvalidDart"
         , "Topomesh"]


from array import array
from interface.topomesh import (TopomeshError, InvalidDart
                              , ITopomesh, IDartListMesh
                              , INeighborhoodMesh
                              , IMutableMesh)
from utils import IdDict


class Topomesh (ITopomesh, IDartListMesh, INeighborhoodMesh, IMutableMesh) :
	"""Implementation of a topological mesh
	"""
	
	def __init__ (self, idgenerator = "set") :
		"""Constructor of an empty mesh
		
		:Parameters:
		 - `idgenerator` (str) - type of id gen used in the
		                         mesh
		"""
		#list of darts
		self._degree = IdDict(idgenerator = idgenerator)
		
		#topological relations between darts
		self._borders = {}
		self._regions = {}

	def clear (self) :
		"""Clear topomesh from any info
		"""
		self._degree.clear()
		self._borders.clear()
		self._regions.clear()
	
	########################################################################
	#
	#               Mesh concept
	#
	########################################################################
	def degree (self, did) :
		try :
			return self._degree[did]
		except KeyError :
			raise InvalidDart(did)
	
	degree.__doc__ = ITopomesh.degree.__doc__
	
	def is_valid (self) :#TODO
		return True
	
	is_valid.__doc__ = ITopomesh.is_valid.__doc__
	
	def has_dart (self, did) :
		return did in self._degree
	
	has_dart.__doc__ = ITopomesh.has_dart.__doc__
	
	def _borders_with_offset (self, dids, offset) :
		if offset == 0 :
			return iter(dids)
		else :
			bids = set()
			for did in dids :
				bids |= set(self._borders[did])
			
			return self._borders_with_offset(bids, offset - 1)
	
	def borders (self, did, offset = 1) :
		if self.degree(did) == 0 and offset == 1 :
			return iter([])
		
		if self.degree(did) - offset < 0 :
			msg = "Degree (%d) of dart %d is smaller than offset (%d)" \
			    % (self.degree(did), did, offset)
			raise TopomeshError(msg)
		
		return self._borders_with_offset([did], offset)
	
	borders.__doc__ = ITopomesh.borders.__doc__
	
	def nb_borders (self, did) :
		return len(self._borders[did])
	
	nb_borders.__doc__ = ITopomesh.nb_borders.__doc__
	
	def _regions_with_offset (self, dids, offset) :
		if offset == 0 :
			return iter(dids)
		else :
			rids = set()
			for did in dids :
				rids |= set(self._regions[did])
			
			return self._regions_with_offset(rids, offset - 1)
	
	def regions (self, did, offset = 1) :
		return self._regions_with_offset([did], offset)
	
	regions.__doc__ = ITopomesh.regions.__doc__
	
	def nb_regions (self, did) :
		return len(self._regions[did])
	
	nb_regions.__doc__ = ITopomesh.nb_regions.__doc__
	
	########################################################################
	#
	#               Dart list concept
	#
	########################################################################
	def _darts (self, degree) :
		for did, deg in self._degree.iteritems() :
			if deg == degree :
				yield did
	
	def darts (self, degree = None) :
		if degree is None :
			return iter(self._degree)
		else :
			return self._darts(degree)
	
	darts.__doc__ = IDartListMesh.darts.__doc__
	
	def __iter__ (self) :
		return iter(self._degree)
	
	def nb_darts (self, degree = None) :
		if degree is None :
			return len(self._degree)
		else :
			nb = 0
			for did, deg in self._degree.iteritems() :
				if deg == degree :
					nb += 1
			
			return nb
	
	nb_darts.__doc__ = IDartListMesh.nb_darts.__doc__
	
	########################################################################
	#
	#               Neighborhood concept
	#
	########################################################################
	def border_neighbors (self, did) :
		for bid in self.borders(did) :
			for rid in self.regions(bid) :
				if rid != did :
					yield rid
	
	border_neighbors.__doc__ = INeighborhoodMesh.border_neighbors.__doc__
	
	def nb_border_neighbors (self, did) :
		return len(tuple(self.border_neighbors(did) ) )
	
	nb_border_neighbors.__doc__ = INeighborhoodMesh.nb_border_neighbors.__doc__
	
	def region_neighbors (self, did) :
		for rid in self.regions(did) :
			for bid in self.borders(rid) :
				if bid != did :
					yield bid
	
	region_neighbors.__doc__ = INeighborhoodMesh.region_neighbors.__doc__
	
	def nb_region_neighbors (self, did) :
		return len(tuple(self.region_neighbors(did) ) )
	
	nb_region_neighbors.__doc__ = INeighborhoodMesh.nb_region_neighbors.__doc__
	
	########################################################################
	#
	#               Mutable mesh concept
	#
	########################################################################
	def add_dart (self, degree, did = None) :
		try :
			did = self._degree.add(degree, did)
		except KeyError :
			raise InvalidDart(did)
		
		self._borders[did] = array("L")
		self._regions[did] = array("L")
		
		return did
	
	add_dart.__doc__ = IMutableMesh.add_dart.__doc__
	
	def remove_dart (self, did) :
		try :
			del self._degree[did]
		except KeyError :
			raise InvalidDart(did)
		
		#remove links
		for bid in tuple(self._borders[did]) :
			self.unlink(did, bid)
		
		for rid in tuple(self._regions[did]) :
			self.unlink(rid, did)
		
		del self._borders[did]
		del self._regions[did]
	
	remove_dart.__doc__ = IMutableMesh.remove_dart.__doc__
	
	def link (self, did, bid) :
		if self.degree(bid) + 1 != self.degree(did) :
			raise InvalidDart(bid)
		
		self._borders[did].append(bid)
		self._regions[bid].append(did)
	
	link.__doc__ = IMutableMesh.link.__doc__
	
	def unlink (self, did, bid) :
		self._borders[did].remove(bid)
		self._regions[bid].remove(did)
	
	unlink.__doc__=IMutableMesh.unlink.__doc__















