# -*- python -*-
# -*- coding: latin-1 -*-
#
#       IdGenerator : graph package
#
#       Copyright or � or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Fred Theveny <theveny@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provide a generator for id numbers
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka-toufou $ "

class IdMaxGenerator(object) :
	def __init__ (self) :
		self._id_max = 0
	
	def get_id (self, id = None) :
		if id is None :
			ret = self._id_max
			self._id_max += 1
			return ret
		else :
			self._id_max = max(self._id_max,id+1)
			return id
	
	def release_id (self, id) :
		pass
class IdSetGenerator(object) :
	def __init__ (self) :
		self._id_max = 0
		self._available_ids = set()
	
	def get_id (self, id = None) :
		if id is None :
			if len(self._available_ids) == 0 :
				ret = self._id_max
				self._id_max += 1
				return ret
			else :
				return self._available_ids.pop()
		else :
			if id >= self._id_max :
				self._available_ids.update(xrange(self._id_max,id))
				self._id_max = id+1
				return id
			else :
				try :
					self._available_ids.remove(id)
					return id
				except KeyError :
					raise IndexError("id %d already used" % id)
	
	def release_id (self, id) :
		if id > self._id_max :
			raise IndexError("id out of range")
		elif id in self._available_ids :
			raise IndexError("id already not used")
		else :
			self._available_ids.add(id)

class IdGenerator (IdSetGenerator) :
	pass
class IdListGenerator(object) :
	def __init__ (self) :
		self._id_max=0
		self._id_list=[]
	
	def get_id (self, id=None) :
		if id is None :
			if len(self._id_list)==0 :
				ret=self._id_max
				self._id_max+=1
				return ret
			else :
				return self._id_list.pop()
		else :
			if id>=self._id_max :
				self._id_list.extend(range(self._id_max,id))
				self._id_max=id+1
				return id
			else :
				try :
					ind=self._id_list.index(id)
					del self._id_list[ind]
					return id
				except ValueError :
					raise IndexError("id %d already used" % id)
	
	def release_id (self, id) :
		if id>self._id_max :
			raise IndexError("id out of range")
		elif id in self._id_list :
			raise IndexError("id already not used")
		else :
			self._id_list.append(id)

