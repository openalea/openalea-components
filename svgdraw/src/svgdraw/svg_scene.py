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
This module defines a special top level layer
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from svg_group import SVGGroup,SVGLayer

class SVGScene (SVGGroup) :
	"""Maintain a list of svg elms
	"""
	
	def __init__ (self, width = 0, height = 0) :
		"""Constructor
		
		widht and height do not define a clipping
		box. Hence, all objects in this scene do
		not necessarily lie inside (width,height)
		
		:Parameters:
		 - `width` (float) - actual width
		   of the group.
		 - `height` (float) - actual height
		   of the group
		"""
		SVGGroup.__init__(self,width,height,"pglscene")
		self.set_nodename("svg:svg")
		self.set_attribute("xmlns:dc",
		                   "http://purl.org/dc/elements/1.1/")
		self.set_attribute("xmlns:cc",
		                   "http://web.resource.org/cc/")
		self.set_attribute("xmlns:rdf",
		                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		self.set_attribute("xmlns:svg",
		                   "http://www.w3.org/2000/svg")
		self.set_attribute("xmlns:xlink",
		                   "http://www.w3.org/1999/xlink")
		self.set_attribute("xmlns:inkscape",
		                   "http://www.inkscape.org/namespaces/inkscape")
		self.set_attribute("xmlns:sodipodi",
		                   "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
	
	##################################################
	#
	#		id generator
	#
	##################################################
	##################################################
	#
	#		natural vs svg position
	#
	##################################################
	def natural_pos (self, svgx, svgy) :
		"""Return position in a natural frame
		
		Oy oriented toward top instead of bottom.
		
		:Parameters:
		 - `svgx` (float) - x coordinate of the point
		 - `svgy` (float) - y coordinate of the point
		    considering Oy axis oriented downward
		
		:Returns Type: float,float
		"""
		return (svgx,self.height() - svgy)
	
	def svg_pos (self, x, y) :
		"""Return position in drawing frame
		
		Oy oriented toward bottom.
		
		:Parameters:
		 - `x` (float) - x coordinate of the point
		 - `y` (float) - y coordinate of the point
		    considering Oy axis oriented upward
		
		:Returns Type: float,float
		"""
		return (x,self.height() - y)
	
	##################################################
	#
	#		layers access
	#
	##################################################
	def get_layer (self, name) :
		"""Walks among childrens to find
		the first layer with the given name.
		
		:Parameters:
		 - `name` (str) - name (not id) of the
		   layer
		
		:Returns Type: :class:`SVGLayer`
		"""
		for elm in self.elements() :
			if isinstance(elm,SVGLayer) :
				if elm.attribute("inkscape:label") == name :
					return elm
	
	def layers (self) :
		"""Iterate on all layers in this scene
		
		:Returns Type: iter of `SVGLayer`
		"""
		for elm in self.elements() :
			if isinstance(elm,SVGLayer) :
				yield elm

