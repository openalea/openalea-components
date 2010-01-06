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
This module defines a set of algorithms for svg elements
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from math import sqrt
from svg_primitive import SVGCenteredElement,SVGSphere
from svg_path import SVGPath,SVGConnector
from svg_group import SVGGroup

def expand_path (sc) :
	"""Ensure that all elements that
	are not direct svg primitives are
	well defined as path.
	"""
	for elm in sc.elements() :
		_expand_path(elm,sc)

def find_center (elm) :
	if isinstance(elm,SVGCenteredElement) :
		pt = elm.center()
	elif isinstance(elm,SVGPath) :
		pts = tuple(elm.polyline_ctrl_points() )
		pt = pts[len(pts) / 2]
	else :
		raise NotImplementedError("don't know how to handle elm of type %s" % type(elm) )
	
	return elm.scene_pos(pt)

def _expand_path (svgelm, sc) :
	if isinstance(svgelm,SVGGroup) :
		for elm in svgelm.elements() :
			_expand_path(elm,sc)
	else :
		if isinstance(svgelm,SVGConnector) :
			if len(tuple(svgelm.commands() ) ) == 0 :
				source_elm = sc.get_by_id(svgelm.source() )
				target_elm = sc.get_by_id(svgelm.target() )
				pt1 = find_center(source_elm)
				pt2 = find_center(target_elm)
				if isinstance(source_elm,SVGCenteredElement) :
					dx = pt2[0] - pt1[0]
					dy = pt2[1] - pt1[1]
					n = sqrt(dx * dx + dy * dy)
					dx /= n
					dy /= n
					rx,ry = source_elm.radius()
					R = abs(dx * rx + dy * ry)
					pt1 = (pt1[0] + dx * R,
					       pt1[1] + dy * R)
				if isinstance(target_elm,SVGCenteredElement) :
					dx = pt1[0] - pt2[0]
					dy = pt1[1] - pt2[1]
					n = sqrt(dx * dx + dy * dy)
					dx /= n
					dy /= n
					rx,ry = target_elm.radius()
					R = abs(dx * rx + dy * ry)
					pt2 = (pt2[0] + dx * R,
					       pt2[1] + dy * R)
				
				svgelm.move_to(*pt1)
				svgelm.line_to(*pt2)

