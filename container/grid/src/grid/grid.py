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
for a grid interface
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

from interface import grid

class Grid (grid.Grid) :
	"""
	interface definition of simple N dimensional grids
	with finite number of case per dimension
	"""
	
	def __init__ (self, shape) :
		"""
		constructor of a finite grid
		:param shape: number of case in each dimension
		:type shape: iter of int
		"""
		self._shape=[int(s) for s in shape]
		offset=[1]
		for i,incr in enumerate(self._shape[:-1]) :
			offset.append(offset[i]*incr)
		self._offset=offset
	
	# ##########################################################
	#
	#		Grid concept
	#
	# ##########################################################
	def dim (self) :
		"""
		dmension of the grid
		number of coordinates
		:rtype: int
		"""
		return len(self._shape)
	
	def shape (self) :
		"""
		return the shape of the grid,
		number of cases per dimension
		
		:rtype: iter of int
		"""
		return iter(self._shape)
	
	# ##########################################################
	#
	#		Case list concept
	#
	# ##########################################################
	def __len__ (self) :
		"""
		number of cases in the grid
		
		:rtype: int
		"""
		s=1
		for incr in self._shape : s*=incr
		return s
	
	def __iter__ (self) :
		"""
		iterator on case indexes
		
		:rtype: iter of int
		"""
		return iter(xrange(self.__len__()))
	
	def index (self, coord ) :
		"""
		compute the index of a case from his position
		inverse function of `coordinates`
		
		:param coord: position in each dimension
		:type coord: tuple of int
		:rtype: int
		"""
		return sum([coord[i]*offset for i,offset in enumerate(self._offset)])
	
	def coordinates (self, ind) :
		"""
		compute the position in each dimension from the index of the case
		inverse function of `index`
		
		:param ind: index of the case
		:type ind: int
		:rtype: tuple of int
		"""
		if not (0<=ind<len(self)) :
			raise IndexError("index out of range index: %d max : %d" % (ind,len(self)))
		reste=ind
		coord=[]
		for i in xrange(self.dim()-1,-1,-1) :
			coord.append(reste/self._offset[i])
			reste=reste%self._offset[i]
		coord.reverse()
		return coord

	


