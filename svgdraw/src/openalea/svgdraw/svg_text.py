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
This module defines SVG text related elements
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

from svg_element import SVGElement,read_float,write_float
from xml_element import XMLElement,ELEMENT_TYPE,TEXT_TYPE

def read_text_fragments (span_node, current_size) :
	"""Read text informations in
	a set of xml nodes
	
	:Parameters:
	 - `span_node` (XMLElement) - top node
	 - `current_size` (int) - current size of txt
	
	:Return: a list of string with
	  their font size
	
	:Returns Type: list of (str,int)
	"""
	fragments = []
	#read current size
	for gr in span_node.get_default("style","").split(";") :
		if ":" in gr :
			k,v = gr.split(":")
			if k == "font-size" :
				current_size = read_float(v)
	#walk through children to find fragments
	for node in span_node.children() :
		if node.nodetype() == ELEMENT_TYPE :
			if node.nodename() == "svg:tspan" :
				for frag in read_text_fragments(node,current_size) :
					fragments.append(frag)
		elif node.nodetype() == TEXT_TYPE :
			fragments.append( (node.get_default("data",""),current_size) )
	#return
	return fragments

class SVGText (SVGElement) :
	"""A text positioned in space
	"""
	
	def __init__ (self, x, y, txt, font_size = 8, id=None) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x coordinate of the
		    top left corner of the text
		    (in svg coordinates)
		 - `y` (float) - y coordinate of the
		    top left corner of the text
		    (in svg coordinates)
		 - `txt` (str) - message to display
		 - `font_size` (int) - height of the text
		 - `id` (str) - unique id for this element
		"""
		SVGElement.__init__(self,id,None,"svg:text")
		self._x = x
		self._y = y
		self.set_text(txt,font_size)
		
	##################################################
	#
	#		attributes
	#
	##################################################
	def pos (self) :
		"""Retrieve coordinates of
		the top left corner of the text
		in svg coordinates.
		
		:Returns Type: float,float
		"""
		return (self._x,self._y)
	
	def text (self) :
		"""Retrieve displayed message
		
		:Returns Type: str
		"""
		return "".join(tup[0] for tup in self._txt_fragments)
	
	def set_text (self, txt, font_size = 10) :
		"""Set message to display
		
		:Parameters:
		 - `txt` (str) - message
		 - `font_size` - size of text
		"""
		self._txt_fragments = [(txt,font_size)]
	
	def fragments (self) :
		"""Iterate on all text parts
		
		A text fragment is a piece of
		text with a unique font size.
		
		:Returns Type: iter of (str,int)
		"""
		return iter(self._txt_fragments)
	
	def add_text_fragment (self, txt, font_size) :
		"""Add a new text part
		
		.. seealso:: :func:`fragments`
		
		:Parameters:
		 - `txt` (str) - message
		 - `font_size` (int) - size of the text
		"""
		self._txt_fragments.append( (txt,font_size) )
	
	def clear (self) :
		"""Remove all messages from this text
		"""
		self._txt_fragments = []
	
	##############################################
	#
	#		font size style
	#
	##############################################
	def font_size (self) :
		"""Retrieve a unique font size
		for this text.
		
		:Returns Type: int
		"""
		try :
			size = read_float(self.get_style("font-size") )
			if size is None :
				return 0.
			else :
				return size
		except KeyError :
			return 0.
	
	def set_font_size (self, size) :
		"""Set a unique font size
		for this text.
		
		:Parameters:
		 - `size` (int)
		"""
		self.set_style("font-size",write_float(size) )
		for k,v in [("font-style","normal"),
		            ("font-weight","normal"),
		            ("text-align","start"),
		            ("text-anchor","start"),
		            ("font-family","Bitstream Vera Sans") ] :
			try :
				val = self.get_style(k)
			except KeyError :
				self.set_style(k,v)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		SVGElement.load(self)
		self._x = read_float(self.get_default("x","0") )
		self._y = read_float(self.get_default("y","0") )
		
		#read txt fragments
		self.clear()
		size = self.font_size()
		for txt,size in read_text_fragments(self.child(0),size) :
			self.add_text_fragment(txt,size)
		self.clear_children()
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("x","%f" % self._x)
		self.set_attribute("y","%f" % self._y)
		self.set_attribute("xml:space","preserve")
		
		#text fragments
		self.clear_children()		for txt,size in self._txt_fragments :
			#span
			span = XMLElement(None,ELEMENT_TYPE,"svg:tspan")
			self.add_child(span)
			span.set_attribute("x","%f" % self._x)
			span.set_attribute("y","%f" % self._y)
			span.set_attribute("sodipodi:role","line")
			span.set_attribute("style","font-size:%s" % write_float(size) )
			#txt
			txtelm = XMLElement(None,TEXT_TYPE)
			span.add_child(txtelm)
			txtelm.set_attribute("data","%s" % txt)
		#save
		SVGElement.save(self)

