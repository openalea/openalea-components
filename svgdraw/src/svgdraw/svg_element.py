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
	if color is None :
		return "none"
	else :
		return "#%.2x%.2x%.2x" % color

def read_float (val_str) :
	if val_str == "none" :
		return None
	else :
		res = float_re.match(val_str)
		return float(res.groups()[0])

def write_float (val) :
	return "%f" % val

class SVGElement (XMLElement) :
	"""
	base class for all SVG element
	store attribute of geometry and style
	"""
	
	type = "base"
	
	def __init__ (self, nodeid=None, parent=None, nodename="svg") :
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
		"""Return style associated with this key.
		"""
		return self._style[key]
	
	def set_style (self, key, str_val) :
		"""Set the style associated with this key.
		"""
		self._style[key] = str_val
	
	def displayed (self) :
		"""Tells wether this element is visible or not.
		"""
		if "display" in self._style :
			return self._style["display"] != "none"
		else :
			return False
	
	def set_display (self, display) :
		"""Set the visibility of this element.
		"""
		if display :
			self._style["display"] = "true"
		else :
			self._style["display"] = "none"
	
	def fill (self) :
		"""Return color used to fill the element.
		"""
		if "fill" in self._style :
			return read_color(self._style["fill"])
		else :
			return None
	
	def set_fill (self, color) :
		"""Set the color used to fill the element.
		"""
		self._style["fill"] = write_color(color)
	
	def stroke (self) :
		"""Return color used to paint border of the element.
		"""
		if "stroke" in self._style :
			return read_color(self._style["stroke"])
		else :
			return None
	
	def set_stroke (self, color) :
		"""Set the color used to paint the border.
		"""
		self._style["stroke"] = write_color(color)
	
	def stroke_width (self) :
		"""Return size of the border.
		"""
		if "stroke-width" in self._style :
			width = read_float (self._style["stroke-width"])
			if width is None :
				return 0.
			else :
				return width
		else :
			return 0.
	
	def set_stroke_width (self, width) :
		"""Set the size of the border.
		"""
		self._style["stroke-width"] = write_float(width)
	##################################################
	#
	#		natural vs svg position
	#
	##################################################
	def natural_pos (self, svgx, svgy) :
		"""Return position in a natural frame
		
		Oy oriented toward top instead of bottom.
		"""
		if self.parent() is None :
			return (svgx,svgy)
		else :
			return self.parent().natural_pos(svgx,svgy)
	
	def svg_pos (self, x, y) :
		"""Return position in drawing frame.
		
		Oy oriented toward bottom.
		"""
		if self.parent() is None :
			return (x,y)
		else :
			return self.parent().svg_pos(x,y)
	
	##############################################
	#
	#		change of referential
	#
	##############################################
	def scene_pos (self, pos) :
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
		return self._transform
	
	def set_transformation (self, transfo) :
		self._transform.clone(transfo)
	
	def transform (self, transfo) :
		self._transform = self._transform * transfo
	
	def translate (self, dx, dy) :
		self._transform = self._transform * translation(dx,dy)
	
	def rotate (self, angle) :
		self._transform = self._transform * rotation(angle)
	
	def scale (self, sx, sy) :
		self._transform = self._transform * scaling(sx,sy)
	
	##############################################
	#
	#		SVG interface
	#
	##############################################
	def abs_path (self, filename) :
		if self.parent() is None :
			if self._svgfilename is None :
				return filename
			else :
				return join(dirname(self._svgfilename),filename)
		else :
			return self.parent().abs_path(filename)
	
	def load_style (self) :
		style = {}
		for style_elm in self.get_default("style","").split(";") :
			if ":" in style_elm :
				key,val = style_elm.split(":")
				style[key] = val
		return style
	
	def load (self) :
		XMLElement.load(self)
		self._style.update(self.load_style() )
		#transformation
		if self.has_attribute("transform") :
			txt = self.attribute("transform")
			self._transform.read(txt)
	
	def save_style (self) :
		style = self.load_style()
		style.update(self._style)
		self.set_attribute("style",";".join(["%s:%s" % it for it in style.iteritems()]) )
	
	def save (self) :
		XMLElement.save(self)
		self.save_style()
		self.set_attribute("transform",self._transform.write() )

