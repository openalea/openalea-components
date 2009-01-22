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
for a topomesh interface
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

from interface.topomesh import TopomeshError,InvalidWisp,InvalidDegree,\
				ITopomesh,IWispListMesh,INeighborhoodMesh,IMutableMesh
from relation import Relation

class StrInvalidWisp (InvalidWisp) :
	"""
	exception raised when a wrong wisp id is provided
	"""
	def __init__ (self, degree, wid) :
		InvalidWisp.__init__(self,"wisp %d of degree %d does not exist" % (wid,degree))

class StrInvalidDegree (InvalidDegree) :
	"""
	exception raised when a wrong degree is provided
	"""
	def __init__ (self, degree) :
		InvalidDegree.__init__(self,"degree %d is outside of mesh bounds" % degree)

class Topomesh (ITopomesh,IWispListMesh,INeighborhoodMesh,IMutableMesh) :
	"""
	implementation of a topological mesh
	"""
	__doc__+=ITopomesh.__doc__
	def __init__ (self, degree) :
		"""
		constructor of an empty mesh
		"""
		self._degree=degree
		self._neighborhood=[Relation() for i in xrange(degree+1)]
	########################################################################
	#
	#		Mesh concept
	#
	########################################################################
	def degree (self) :
		return self._degree
	degree.__doc__=ITopomesh.degree.__doc__
	
	def is_valid (self) :
		return True
	is_valid.__doc__=ITopomesh.is_valid.__doc__
	
	def has_wisp (self, degree, wid) :
		try :
			return self._neighborhood[degree].has_left(wid)
		except IndexError :
			raise StrInvalidDegree(degree)
	has_wisp.__doc__=ITopomesh.has_wisp.__doc__
	
	def _borders (self, degree, wid) :
		"""
		internal function to access borders of an element
		"""
		r=self._neighborhood[degree-1]
		for lid in r.from_right(wid) :
			yield r.left(lid)
	
	def _borders_with_offset (self, degree, wids, offset) :
		if offset==0 :
			return wids
		else :
			ret=set()
			for wid in wids :
				ret|=set(self._borders_with_offset(degree-1,self._borders(degree,wid),offset-1))
			return iter(ret)
	
	def borders (self, degree, wid, offset=1) :
		if degree-offset<0 :
			raise InvalidDegree ("smallest wisps have no borders")
		return self._borders_with_offset(degree-1,self._borders(degree,wid),offset-1)
	borders.__doc__=ITopomesh.borders.__doc__
	
	def nb_borders (self, degree, wid) :
		if degree<1 :
			raise InvalidDegree ("smallest wisps have no borders")
		return self._neighborhood[degree-1].nb_links_from_right(wid)
	nb_borders.__doc__=ITopomesh.nb_borders.__doc__
	
	def regions (self, degree, wid) :
		if degree >= self.degree() :
			raise InvalidDegree ("biggest wisps do not separate regions")
		r=self._neighborhood[degree]
		for lid in r.from_left(wid) :
			yield r.right(lid)
	regions.__doc__=ITopomesh.regions.__doc__
	
	def nb_regions (self, degree, wid) :
		if degree >= self.degree() :
			raise InvalidDegree ("biggest wisps do not separate regions")
		return self._neighborhood[degree].nb_links_from_left(wid)
	nb_regions.__doc__=ITopomesh.nb_regions.__doc__
	########################################################################
	#
	#		Wisp list concept
	#
	########################################################################
	def wisps (self, degree) :
		try :
			return self._neighborhood[degree].left_elements()
		except IndexError :
			raise StrInvalidDegree(degree)
	wisps.__doc__=IWispListMesh.wisps.__doc__
	
	def nb_wisps (self, degree) :
		try :
			return self._neighborhood[degree].nb_left_elements()
		except IndexError :
			raise StrInvalidDegree(degree)
	nb_wisps.__doc__=IWispListMesh.nb_wisps.__doc__
	########################################################################
	#
	#		Neighborhood concept
	#
	########################################################################
	def border_neighbors (self, degree, wid) :
		for bid in self.borders(degree,wid) :
			for rid in self.regions(degree-1,bid) :
				if rid != wid :
					yield rid
	border_neighbors.__doc__=INeighborhoodMesh.border_neighbors.__doc__
	
	def nb_border_neighbors (self, degree, wid) :
		return len(list(self.border_neighbors(degree,wid)))
	nb_border_neighbors.__doc__=INeighborhoodMesh.nb_border_neighbors.__doc__
	
	def region_neighbors (self, degree, wid) :
		for rid in self.regions(degree,wid) :
			for bid in self.borders(degree+1,rid) :
				if bid != wid :
					yield bid
	region_neighbors.__doc__=INeighborhoodMesh.region_neighbors.__doc__
	
	def nb_region_neighbors (self, degree, wid) :
		return len(list(self.region_neighbors(degree,wid)))
	nb_region_neighbors.__doc__=INeighborhoodMesh.nb_region_neighbors.__doc__
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_wisp (self, degree, wid=None) :
		wid=self._neighborhood[degree].add_left_element(wid)
		if degree>0 :
			wid2=self._neighborhood[degree-1].add_right_element(wid)
			if wid!=wid2 :
				raise TopomeshError("internal mismatch between two relations")
		return wid
	add_wisp.__doc__=IMutableMesh.add_wisp.__doc__
	
	def remove_wisp (self, degree, wid) :
		self._neighborhood[degree].remove_left_element(wid)
		if degree>0 :
			self._neighborhood[degree-1].remove_right_element(wid)
	remove_wisp.__doc__=IMutableMesh.remove_wisp.__doc__
	
	def link (self, degree, wid, border_id) :
		if degree<1 :
			raise InvalidDegree ("smallest wisps have no neighbors")
		self._neighborhood[degree-1].add_link(border_id,wid)
	link.__doc__=IMutableMesh.link.__doc__
	
	def unlink (self, degree, wid, border_id) :
		if degree<1 :
			raise InvalidDegree ("smallest wisps have no neighbors")
		self._neighborhood[degree-1].remove_link(border_id,wid)
	unlink.__doc__=IMutableMesh.unlink.__doc__

