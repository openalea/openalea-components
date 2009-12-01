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
		return elm.center()
	elif isinstance(elm,SVGPath) :
		pts = tuple(elm.polyline_ctrl_points() )
		return pts[len(pts) / 2]
	else :
		raise NotImplementedError("don't know how to handleelm of type %s" % type(elm) )

def tup2 (vec) :
	return (vec[0],vec[1])

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
					ori = pt2 - pt1
					ori.normalize()
					pt1 += ori * abs(ori * source_elm.radius() )
				if isinstance(target_elm,SVGCenteredElement) :
					ori = pt1 - pt2
					ori.normalize()
					pt2 += ori * abs(ori * target_elm.radius() )
				
				svgelm.append('M',[tup2(pt1)])
				svgelm.append('L',[tup2(pt2)])
		elif isinstance(svgelm,SVGSphere) :
			if len(tuple(svgelm.commands() ) ) == 0 :
				#TODO better circle
				cent = svgelm.center()
				rad = svgelm.radius()
				pt0 = cent + (rad[0],0,0)
				pt1 = cent + (0,rad[1],0)
				pt2 = cent - (rad[0],0,0)
				pt3 = cent - (0,rad[1],0)
				svgelm.append('M',[tup2(pt0)])
				svgelm.append('L',[tup2(pt1)])
				svgelm.append('L',[tup2(pt2)])
				svgelm.append('L',[tup2(pt3)])
				svgelm.append('z')

