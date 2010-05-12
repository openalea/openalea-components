# -*- python -*-
# -*- coding: latin-1 -*-
#
#       svg : image package
#
#       Copyright 2006 - 2008 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

"""This module provide basics function to handle SVG images"""

__license__ = "Cecill-C"
__revision__ = " $Id: svg_inout.py 2245 2010-02-08 17:11:34Z cokelaer $ "

# TODO: functionalities depends on vplants

from openalea.svgdraw import (open_svg, SVGImage, SVGSphere
                            ,SVGPath, SVGGroup, SVGLayer, SVGScene)

def loadsc (filename) :
    f = open_svg(filename,'r')
    sc = f.read()
    f.close()
    return sc,

def writesc (sc, filename) :
    f = open_svg(filename,'w')
    f.write(sc)
    f.close()

def get_elm (svggr, svgid) :
    return svggr.get_id(svgid),

def svg_image (svgid, image, filename=None) :
    if filename is None :
        filename = svgid
    
    if image is not None :
        w,h = image.size
    else :
        w,h = (10,10)
    
    svgim = SVGImage(0,0,w,h,filename,svgid)
    return svgim,

def svg_point (svgid, x, y, radius=2, color=None) :
    svgelm = SVGSphere(x,y,radius,radius,svgid)
    svgelm.set_fill(color)
    return svgelm,

def svg_polyline (svgid, pts, color=None, stroke_width=1.) :
    svgelm = SVGPath(svgid)
    svgelm.move_to(*pts[0])
    for pt in pts[1:] :
        svgelm.line_to(*pt)
    svgelm.set_fill(None)
    svgelm.set_stroke(color)
    svgelm.set_stroke_width(stroke_width)
    return svgelm,

def svg_group (svgid, svg_elms) :
    svggr = SVGGroup(100,100,svgid)
    for elm in svg_elms :
        svggr.append(elm)
    return svggr,

def svg_layer (svgid, svg_elms, name=None) :
    if name is None :
        name = svgid
    
    svglay = SVGLayer(name,100,100,svgid)
    for elm in svg_elms :
        svglay.append(elm)
    return svglay,

def svg_scene (width, height, layers) :
    svgsc = SVGScene(width,height)
    
    for lay in layers :
        svgsc.append(lay)
    return svgsc,

def svg_elements (svggr):
    return list(svggr.elements() ),

def svg_positions (svg_pts) :
    coords = {}
    for pt in svg_pts :
        coords[pt.svgid()] = pt.scene_pos(pt.center() )
    return coords

__all__ = ["loadsc", "writesc",
         "get_elm",
         "svg_image", "svg_point", "svg_polyline",
         "svg_group", "svg_layer",
         "svg_scene",
         "svg_elements",
         "svg_positions"]
