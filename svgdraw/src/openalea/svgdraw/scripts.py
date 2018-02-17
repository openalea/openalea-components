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
Set of scripts to work around SVGScenes
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

def to_svg_namespace (node) :
	"""	add 'svg:' to all nodenames
	that represent svg elements.
	
	:Parameters:
	 - `node` (:class:`SVGElement`) - base node
	   to consider, usually an :class:`SVGScene`
	
	:Return: None, modify things in place
	"""
	if node.has_attribute("xmlns") :
		node.remove_attribute("xmlns")
	if node.nodename() in ("svg","g","path","rect","image","defs","metadata") :
		node.set_nodename("svg:%s" % node.nodename())
	for child in node.children() :
		to_svg_namespace(child)

def remove_attribute (node, attr_name, nodename=None) :
	"""Remove a specific attribute
	from all nodes below node.
	
	:Parameters:
	 - `node` (:class:`SVGElement`) - base node
	   to consider, usually an :class:`SVGScene`
	 - `attr_name` (str) - name of the
	   attribute to discard
	 - `nodename` (str) - if not None, restrict
	   the action of this function to node
	   with the given nodename
	
	:Return: None, modify things in place
	"""
	if (nodename is None) or (node.nodename() == nodename) :
		if node.has_attribute(attr_name) :
			node.remove_attribute(attr_name)
	for child in node.children() :
		remove_attribute(child,attr_name,nodename)

