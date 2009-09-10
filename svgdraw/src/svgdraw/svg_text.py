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
This module defines a set of primitive elements
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from vplants.plantgl.math import Matrix4
from svg_element import SVGElement,read_float,write_float
from xml_element import XMLElement,ELEMENT_TYPE,TEXT_TYPE

def read_text_fragments (span_node, current_size) :
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
	"""
	a text positioned in space
	"""
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:text")
		self._txt_fragments = []
		
	def pos (self) :
		return self._transform.getTransformationB()[2]
	
	def text (self) :
		return "".join(tup[0] for tup in self._txt_fragments)
	
	def set_text (self, txt, font_size = 10) :
		self._txt_fragments = [(txt,font_size)]
	
	def fragments (self) :
		return iter(self._txt_fragments)
	
	def add_text_fragment (self, txt, font_size) :
		self._txt_fragments.append( (txt,font_size) )
	##############################################
	#
	#		font size style
	#
	##############################################
	def font_size (self) :
		try :
			size = read_float(self.get_style("font-size") )
			if size is None :
				return 0.
			else :
				return size
		except KeyError :
			return 0.
	
	def set_font_size (self, size) :
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
		SVGElement.load(self)
		x = float(self.get_default("x",0) )
		y = float(self.get_default("y",0) )
		x,y = self.real_pos(x,y)
		self._transform *= Matrix4.translation( (x,y,0) )
		
		#read txt fragments
		size = self.font_size()
		for txt,size in read_text_fragments(self.child(0),size) :
			self.add_text_fragment(txt,size)
		self.clear_children()
	
	def save (self) :
		x,y,z = self.pos()
		self._transform *= Matrix4.translation( (-x,-y,-z) )
		svgx,svgy = self.svg_pos(x,y)
		self.set_attribute("x","%f" % svgx)
		self.set_attribute("y","%f" % svgy)
		self.set_attribute("xml:space","preserve")
		
		#text fragments
		for txt,size in self._txt_fragments :
			#span
			span = XMLElement(None,ELEMENT_TYPE,"svg:tspan")
			self.add_child(span)
			span.set_attribute("x","%f" % svgx)
			span.set_attribute("y","%f" % svgy)
			span.set_attribute("sodipodi:role","line")
			span.set_attribute("style","font-size:%s" % write_float(size) )
			#txt
			txtelm = XMLElement(None,TEXT_TYPE)
			span.add_child(txtelm)
			txtelm.set_attribute("data","%s" % txt)
		#save
		SVGElement.save(self)
		self._transform *= Matrix4.translation( (x,y,z) )
	##############################################
	#
	#		pgl interface #TODO deprecated
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		raise NotImplementedError
	
	def to_pgl3D (self, pglshape) :
		raise NotImplementedError

