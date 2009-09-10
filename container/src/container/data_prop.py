# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Topomesh : container package
#
#       Copyright or  or Copr. 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

"""
This module provide a python definition of a property
"""

__license__= "Cecill-C"
__revision__=" $Id: grid.py 116 2007-02-07 17:44:59Z tyvokka $ "

class DataProp (dict) :
	"""
	Implementation of property with unit, type and description
	"""
	
	def __init__ (self, *args, **kwds) :
		self._name = kwds.pop("name","")
		self._unit = kwds.pop("unit","")
		self._type = kwds.pop("type","")
		self._description = kwds.pop("description","")
		dict.__init__(self,*args,**kwds)
	
	##########################################################
	#
	#		accessors
	#
	##########################################################
	def name (self) :
		"""Retrieve the name of this property.
		"""
		return self._name
	
	def unit (self) :
		"""Retrieve unit of this property.
		"""
		return self._unit
	
	def type (self) :
		"""Retrieve type of data in this property.
		"""
		return self._type
	
	def description (self) :
		"""Return the description associated with this property.
		"""
		return self._description
