# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Grid : grid package
#
#       Copyright or � or Copr. 2006 INRIA - CIRAD - INRA  
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

class Grid (object) :
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
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def shape (self) :
		"""
		return the shape of the grid,
		number of cases per dimension
		
		:rtype: iter of int
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def __iter__ (self) :
		"""
		iterator on case indexes
		
		:rtype: iter of int
		"""
		raise RuntimeError()
	
	def index (self, coord ) :
		"""
		compute the index of a case from his position
		inverse function of `coordinates`
		
		:param coord: position in each dimension
		:type coord: tuple of int
		:rtype: int
		"""
		raise RuntimeError()
	
	def coordinates (self, ind) :
		"""
		compute the position in each dimension from the index of the case
		inverse function of `index`
		
		:param ind: index of the case
		:type ind: int
		:rtype: tuple of int
		"""
		raise RuntimeError()
	


