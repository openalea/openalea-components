# -*- python -*-
#
#       svgdraw: svg library
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

"""
This module defines a group svg element
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

from svg_element import SVGElement,read_float,write_float

class SVGGroup (SVGElement) :
	"""Container that group svg primitives
	"""
	def __init__ (self, width, height, id=None) :
		"""Constructor
		
		widht and height do not define a clipping
		box. Hence, all objects in this group do
		not necessarily lie inside (width,height)
		
		:Parameters:
		 - `width` (float) - actual width
		   of the group.
		 - `height` (float) - actual height
		   of the group
		 - `id` (str) - unique id for this element
		"""
		SVGElement.__init__(self,id,None,"svg:g")
		self._width = width
		self._height = height
		self._elms = []
	
	##################################################
	#
	#		attributes
	#
	##################################################
	def width (self) :
		"""Retrieve width of the group
		
		:Returns Type: float
		"""
		return self._width
	
	def height (self) :
		"""Retrieve height of the group
		
		:Returns Type: float
		"""
		return self._height
	
	def size (self,) :
		"""Retrieve size of the group
		
		:Returns Type: float,float
		"""
		return (self._width,self._height)
	
	def set_size (self, width, height) :
		"""Set the size of the group
		
		:Parameters:
		 - `width` (float)
		 - `height` (float)
		"""
		self._width = width
		self._height = height
	
	def elements (self) :
		"""Iterate on all elements in the group
		
		:Returns Type: iter of SVGElement
		"""
		return iter(self._elms)
	
	def __iter__ (self) :
		"""alias for :func:`elements`
		
		.. seealso: :func:`elements`
		
		:Returns Type: iter of SVGElement
		"""
		return self.elements()
	
	def __len__ (self) :
		"""Number of elements in the group
		
		:Returns Type: int
		"""
		return len(self._elms)
	
	def __getitem__ (self, ind) :
		"""direct access to a given element
		
		list interface
		
		:Returns Type: :class:`SVGElement`
		"""
		return self._elms[ind]
	
	def append (self, svgelm) :
		"""Append a new element in the group
		
		:Parameters:
		 - `svgelm` (:class:`SVGElement`)
		"""
		self.add_child(svgelm)
		self._elms.append(svgelm)
	
	def clear_elements (self) :
		"""Remove all elements from the group
		"""
		for elm in self.elements() :
			self.remove_child(elm)
		self._elms=[]
	##################################################
	#
	#		svg elements access
	#
	##################################################
	def get_by_id (self, svgid) :
		"""Return an element whose id is svgid
		
		Recursively search in subgroups
		
		:Parameters:
		 - `svgid` (str)
		
		:Return: the founded element or None
		
		:Returns Type:
		 - :class:`SVGElement`
		 - None
		"""
		#search in the group
		for elm in self.elements() :
			if elm.id() == svgid :
				return elm
		
		#recursively search in subgroups
		for elm in self.elements() :
			if isinstance(elm,SVGGroup) :
				found = elm.get_by_id(svgid)
				if found is not None :
					return found
	
	##############################################
	#
	#		elements factory
	#
	##############################################
	def svg_element (self, xmlelm) :
		"""Factory
		
		Construct the appropriate SVGElement
		according to informations stored
		in an XMLElement
		
		:Returns Type: :class:`SVGElement`
		"""
		name = xmlelm.nodename()
		if name[:4] == "svg:" :
			name = name[4:]
		
		if name == "rect" :
			return SVGBox(0,0,1,1)
		elif name == "image" :
			return SVGImage(0,0,1,1,None)
		elif name == "text" :
			return SVGText(0,0,"txt")
		elif name == "circle" :
			return SVGSphere(0,0,1,1)
		elif name == "ellipse" :
			return SVGSphere(0,0,1,1)
		elif name == "path" :#either a path, a circle or a connector
			if xmlelm.has_attribute("sodipodi:type") :#may be a circle
				if xmlelm.attribute("sodipodi:type") == "arc" :#its a circle
					return SVGSphere(0,0,1,1)
				else :
					raise UserWarning("mode not recognized")
			else : #either a path or a connector
				if xmlelm.has_attribute("inkscape:connector-type") :#it's a connector
					return SVGConnector(None,None)
				else : #it's a simple path
					return SVGPath()
		elif name == "g" :#either a group or a layer
			if xmlelm.has_attribute("inkscape:groupmode") : #either a layer or a stack
				if xmlelm.has_attribute("descr") and xmlelm.attribute("descr") == "stack" :
					return SVGStack()
				else :
					return SVGLayer("layer",1,1)
			else :
				return SVGGroup(1,1)
		else :
			return None
	
	##############################################
	#
	#		xml interface
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		SVGElement.load(self)
		self._width = read_float(self.get_default("width","0") )
		self._height = read_float(self.get_default("height","0") )
		#svg elements load
		for ind in xrange(self.nb_children() ) :
			svgelm = self.svg_element(self.child(ind) )
			if svgelm is not None :
				svgelm.from_node(self.child(ind) )
				self.set_child(ind,svgelm)
				self._elms.append(svgelm)
				svgelm.load()
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("width","%f" % self._width)
		self.set_attribute("height","%f" % self._height)
		SVGElement.save(self)
		#save elements in the group
		for svgelm in self.elements() :
			svgelm.save()

class SVGLayer (SVGGroup) :
	"""Add a layer attribute to SVGGroup
	"""
	def __init__ (self, name, width, height, id=None) :
		"""Constructor
		
		widht and height do not define a clipping
		box. Hence, all objects in this group do
		not necessarily lie inside (width,height)
		
		:Parameters:
		 - `name` (str) - name of the layer
		 - `width` (float) - actual width
		   of the group.
		 - `height` (float) - actual height
		   of the group
		 - `id` (str) - unique id for this element
		"""
		SVGGroup.__init__(self,width,height,id)
		self.set_name(name)
	
	##################################################
	#
	#		attributes
	#
	##################################################
	def name (self) :
		"""Retrieve the name of this layer
		
		:Returns Type: str
		"""
		return self._name
	
	def set_name (self, name) :
		"""Set the name of this layer
		
		:Parameters:
		 - `name` (str)
		"""
		self.set_attribute("inkscape:label",name)
		self.set_attribute("inkscape:groupmode","layer")
		self._name = name
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		SVGGroup.load(self)
		self.set_name(self.get_default("inkscape:label","lay") )
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("inkscape:label",self.name() )
		self.set_attribute("inkscape:groupmode","layer")
		SVGGroup.save(self)

from xml_element import XMLElement
from svg_primitive import SVGBox,SVGSphere,SVGImage
from svg_path import SVGPath,SVGConnector
from svg_stack import SVGStack
from svg_text import SVGText

