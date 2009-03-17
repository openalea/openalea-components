# -*- python -*-
# -*- coding: latin-1 -*-
#
#       IdDict : container package
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
This module provide a dictionnary that create keys when needed
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

from id_generator import IdMaxGenerator,IdSetGenerator,IdListGenerator

IdGen = {"max":IdMaxGenerator,
		  "set":IdSetGenerator,
		  "list":IdListGenerator}

class IdDict (dict) :
	"""
	store a tuple of (id,elm)
	create an id when needed
	"""
	def __init__ (self, *args, **kwdargs) :
		try :
			gen_name = kwdargs.pop("idgenerator")
		except KeyError :
			gen_name = "set"
		dict.__init__(self,*args,**kwdargs)
		try :
			self._id_generator=IdGen[gen_name]()
		except KeyError :
			raise UserWarning("the required id generator (%s) is unknown,\navailable generator are %s" % (gen_name,str(IdGen.keys())) )
		
		for k,v in self.iteritems() :
			self._id_generator.get_id(k)
	
	def add (self, val, key=None) :
		try :
			key=self._id_generator.get_id(key)
			dict.__setitem__(self,key,val)
			return key
		except IndexError :
			raise KeyError(key)
	
	################################################
	#
	#		dict interface
	#
	################################################
	def __delitem__ (self, key) :
		dict.__delitem__(self,key)
		self._id_generator.release_id(key)
	
	def __setitem__ (self, key, val) :
		self._id_generator.get_id(key)
		dict.__setitem__(self,key,val)
	
	def clear (self) :
		dict.clear(self)
		self._id_generator=IdGenerator()
	
	def copy (self) :
		return IdDict(self)
	
	def pop (self, key, *args) :
		try :
			val=dict.pop(self,key)
			self._id_generator.release_id(key)
			return val
		except KeyError :
			if len(args)>0 :
				return args[0]
			else :
				raise
	
	def popitem (self) :
		key,val=dict.popitem(self)
		self._id_generator.release_id(key)
		return key,val
	
	def setdefault (self, key, *args) :
		if key not in self :
			self._id_generator.get_id(key)
		return dict.setdefault(key,*args)
	
	def update (self, E, **F) :
		raise NotImplementedError("lapin compris")
