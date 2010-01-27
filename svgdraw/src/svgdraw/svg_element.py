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
This module defines an abstract svg element
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

import re
from os.path import join,dirname
from xml_element import XMLElement,SVG_ELEMENT_TYPE
from transform import SVGTransform,translation,rotation,scaling

#to read svg transformations or values
#norm : http://www.w3.org/TR/SVG/coords.html#TransformAttribute
sep = r"\s*,?\s*"
digit = r"([-]?\d+[.]?\d*e?[+-]?\d?)"
float_re = re.compile(digit+r"(em)?(ex)?(px)?(pt)?(pc)?(cm)?(mm)?(in)?(\%)?")

matrix_re = re.compile("matrix\("+digit+sep+digit+sep+digit+sep+digit+sep+digit+sep+digit+"\)")
translate_re = re.compile("translate\("+digit+sep+digit+"?\)")
scale_re = re.compile("scale\("+digit+sep+digit+"?\)")

def read_color (color_str) :
	"""Read a color string
	
	:Parameters:
	 - `color_str` (str) - a valid
	   string representation of
	   an SVG color
	
	:Return: tuple R,G,B if color
	  is valid, None otherwise
	
	Returns Type:
	 - (int,int,int)
	 - None
	"""
	if color_str == "none" :
		return None
	else : #assert haxedecimal definition
	       #of the color col = #rrggbb
		col_str = color_str.lower()[1:]#remove '#'
		red = int(col_str[:2],16)
		green = int(col_str[2:4],16)
		blue = int(col_str[4:],16)
		return (red,green,blue)

def write_color (color) :
	"""Create an str repr of a color
	
	:Parameters:
	 - `color` ( (int,int,int) ) -
	   RGB representation of a color,
	   (None for empty color)
	
	:Returns Type: str
	"""
	if color is None :
		return "none"
	else :
		return "#%.2x%.2x%.2x" % color

def read_float (val_str) :
	"""Read a float string
	
	:Parameters:
	 - `val_str` (str) - a valid
	   string representation of
	   a floating number
	
	:Return: the value if the string
	  is valid, None otherwise
	
	Returns Type:
	 - float
	 - None
	"""
	if val_str == "none" :
		return None
	else :
		res = float_re.match(val_str)
		return float(res.groups()[0])

def write_float (val) :
	"""Create an str repr of a float
	
	:Parameters:
	 - `val` (float) - actual value
	   of the number or None
	
	:Returns Type: str
	"""
	if val is None :
		return "none"
	else :
		return "%f" % val

class SVGElement (XMLElement) :
	"""Base class for all SVG element
	
	store attributes of geometry and style
	"""
	
	def __init__ (self, nodeid=None, parent=None, nodename="svg") :
		"""Constructor
		
		:Parameters:
		 - `nodeid` (str) - a unique id for this node
		 - `parent` (:class:`SVGElement`) - owner of
		    this node. Default None means that this
		    element is top level.
		 - `nodename` (str) - name of this particular
		    type of node
		"""
		XMLElement.__init__(self,parent,SVG_ELEMENT_TYPE,nodename,nodeid)
		
		#graphic style
		self._style = {}
		
		#transformation
		self._transform = SVGTransform()#transformation matrix expressed
		                                #in parent frame
		                                #pos_Rparent = transform * pos_Rlocal
		
		#filename for abs path
		self._svgfilename = None
	
	##############################################
	#
	#		access to style elements
	#
	##############################################
	def get_style (self, key) :
		"""Return style associated with this key
		
		:Parameters:
		 - `key` (str) - style descriptor
		
		:Returns Type: str
		"""
		return self._style[key]
	
	def set_style (self, key, str_val) :
		"""Set the style associated with this key
		
		:Parameters:
		 - `key` (str) - style descriptor
		 - `str_val` (str) - actual value
		"""
		self._style[key] = str_val
	
	def displayed (self) :
		"""Tells wether this element is visible or not
		
		:Returns Type: bool
		"""
		if "display" in self._style :
			return self._style["display"] != "none"
		else :
			return False
	
	def set_display (self, display) :
		"""Set the visibility of this element
		
		:Parameters:
		 - `display` (bool)
		"""
		if display :
			self._style["display"] = "true"
		else :
			self._style["display"] = "none"
	
	def fill (self) :
		"""Return color used to fill the element
		
		Return None if element is not filled
		
		.. seealso: :func:stroke
		
		:Returns Type:
		 - (int,int,int)
		 - None
		"""
		if "fill" in self._style :
			return read_color(self._style["fill"])
		else :
			return None
	
	def set_fill (self, color) :
		"""Set the color used to fill the element
		
		.. seealso: :func:set_stroke
		
		:Parameters:
		 - `color` (int,int,int) - color
		   used to fill the element, None
		   if no color is used
		"""
		self._style["fill"] = write_color(color)
	
	def stroke (self) :
		"""Return color used to paint border of the element
		
		Return None if element is not filled
		
		.. seealso: :func:fill
		
		:Returns Type:
		 - (int,int,int)
		 - None
		"""
		if "stroke" in self._style :
			return read_color(self._style["stroke"])
		else :
			return None
	
	def set_stroke (self, color) :
		"""Set the color used to paint the border
		
		.. seealso: :func:set_fill
		
		:Parameters:
		 - `color` (int,int,int) - color
		   used to fill border ofthe element,
		   None if no color is used
		"""
		self._style["stroke"] = write_color(color)
	
	def stroke_width (self) :
		"""Return size of the border
		
		:Returns Type: float
		"""
		if "stroke-width" in self._style :
			width = read_float(self._style["stroke-width"])
			if width is None :
				return 0.
			else :
				return width
		else :
			return 0.
	
	def set_stroke_width (self, width) :
		"""Set the size of the border
		
		:Parameters:
		 - `width` (float) - size of
		   the border in pixels
		"""
		self._style["stroke-width"] = write_float(width)
	
	##############################################
	#
	#		change of referential
	#
	##############################################
	def scene_pos (self, pos) :
		"""Express the position in scene
		absolute referential.
		
		Apply recursively all transformations
		to pos to obtain the absolute position
		in the scene.
		
		:Parameters:
		 - `pos` (float,float) - local
		    coordinates of a point
		
		:Returns Type: float,float
		"""
		ppos = self._transform.apply_to_point(pos)
		if self.parent() is None :
			return ppos
		else :
			return self.parent().scene_pos(ppos)
	
	##############################################
	#
	#		transformation
	#
	##############################################
	def transformation (self) :
		"""Retrieve the associated transformation
		
		:Returns Type: :class:`SVGTransform`
		"""
		return self._transform
	
	def set_transformation (self, transfo) :
		"""Set the transformation of this element
		
		Copy the transformation, then assign it
		to the element.
		
		:Parameters:
		 - `transfo` (:class:`SVGTransform`)
		"""
		self._transform.clone(transfo)
	
	def transform (self, transfo) :
		"""Combine a transformation with
		the actual transformation of this
		element.
		
		:Parameters:
		 - `transfo` (:class:`SVGTransform`)
		"""
		self._transform = self._transform * transfo
	
	def translate (self, dx, dy) :
		"""Combine a translation
		with the actual transformation
		of this element.
		
		:Parameters:
		 - `dx` (float) - x displacement
		 - `dy` (float) - y displacement
		"""
		self._transform = self._transform * translation(dx,dy)
	
	def rotate (self, angle) :
		"""Combine a rotation
		with the actual transformation
		of this element.
		
		:Parameters:
		 - `angle` (float) - angle of
		   the rotation around Oz in
		   direct orientation.
		"""
		self._transform = self._transform * rotation(angle)
	
	def scale (self, sx, sy) :
		"""Combine a scaling
		with the actual transformation
		of this element.
		
		:Parameters:
		 - `sx` (float) - x scaling
		 - `sy` (float) - y scaling
		"""
		self._transform = self._transform * scaling(sx,sy)
	
	##############################################
	#
	#		SVG interface
	#
	##############################################
	def abs_path (self, filename) :
		"""absolute path to SVG file
		
		Used by images to access their
		content since it is stored
		outside of the main SVG file.
		"""
		if self.parent() is None :
			if self._svgfilename is None :
				return filename
			else :
				return join(dirname(self._svgfilename),filename)
		else :
			return self.parent().abs_path(filename)
	
	def load_style (self) :
		"""Load style attribute as a map
		
		Style attributes are originally stored
		in a "style" attribute. Parse this
		attribute to create a more easy access.
		
		:Returns Type: dict of (str|str)
		"""
		style = {}
		for style_elm in self.get_default("style","").split(";") :
			if ":" in style_elm :
				key,val = style_elm.split(":")
				style[key] = val
		return style
	
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		XMLElement.load(self)
		self._style.update(self.load_style() )
		#transformation
		if self.has_attribute("transform") :
			txt = self.attribute("transform")
			self._transform.read(txt)
	
	def save_style (self) :
		"""Save style map as an XML attribute
		"""
		style = self.load_style()
		style.update(self._style)
		self.set_attribute("style",";".join(["%s:%s" % it for it in style.iteritems()]) )
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		XMLElement.save(self)
		self.save_style()
		self.set_attribute("transform",self._transform.write() )

