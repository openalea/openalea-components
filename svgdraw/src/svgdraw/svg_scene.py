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
		SVGGroup.__init__(self,width,height,"pglscene")
		self.set_nodename("svg:svg")
		self.set_attribute("xmlns:dc","http://purl.org/dc/elements/1.1/")
		self.set_attribute("xmlns:cc","http://web.resource.org/cc/")
		self.set_attribute("xmlns:rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		self.set_attribute("xmlns:svg","http://www.w3.org/2000/svg")
		self.set_attribute("xmlns:xlink","http://www.w3.org/1999/xlink")
		self.set_attribute("xmlns:inkscape","http://www.inkscape.org/namespaces/inkscape")
		self.set_attribute("xmlns:sodipodi","http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
	
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
		"""
		return (svgx,self.height() - svgy)
	
	def svg_pos (self, x, y) :
		"""Return position in drawing frame.
		
		Oy oriented toward bottom.
		"""
		return (x,self._height() - y)
	
	##################################################
	#
	#		layers access
	#
	##################################################
	def get_layer (self, layer_name) :
		"""Walks among childrens to find the first layer with the given name
		"""
		for elm in self.elements() :
			if isinstance(elm,SVGLayer) :
				if elm.attribute("inkscape:label") == layer_name :
					return elm
	
	def layers (self) :
		"""Iterate on all layers in this scene.
		"""
		for elm in self.elements() :
			if isinstance(elm,SVGLayer) :
				yield elm

