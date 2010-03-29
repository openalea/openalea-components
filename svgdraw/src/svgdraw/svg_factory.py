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
This module defines a factory to create an svg node from its nodename
"""

__license__= "Cecill-C"
__revision__=" $Id: svg_factory.py 8503 2010-03-18 13:10:32Z chopard $ "

from svg_primitive import SVGBox,SVGSphere,SVGImage
from svg_path import SVGPath,SVGConnector
from svg_stack import SVGStack
from svg_text import SVGText
from svg_group import SVGGroup,SVGLayer

def svg_element (xmlelm) :
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
		if xmlelm.has_attribute("sodipodi:type") \
		   and xmlelm.attribute("sodipodi:type") == "arc" :#its a circle
				return SVGSphere(0,0,1,1)
				#TODO extend to other sodipodi types if needed
		else : #either a path or a connector
			if xmlelm.has_attribute("inkscape:connector-type") :#it's a connector
				return SVGConnector(None,None)
			else : #it's a simple path
				return SVGPath()
	elif name == "g" :#either a group or a layer
		if xmlelm.has_attribute("inkscape:groupmode") : #either a layer or a stack
			if xmlelm.has_attribute("descr") \
			   and xmlelm.attribute("descr") == "stack" :
				return SVGStack()
			else :
				return SVGLayer("layer",1,1)
		else :
			return SVGGroup(1,1)
	else :
		raise KeyError("Node not recognized: '%s'" % name)

