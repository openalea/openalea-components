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

from openalea.plantgl.scenegraph import Sphere,Box,FaceSet,QuadSet,Translated,Scaled,ImageTexture
from openalea.plantgl.math import Vector3,Matrix4,eulerRotationZYX,scaling
from svg_element import SVGElement,read_float,write_float
from xml_element import XMLElement
from svg_path import SVGPath

class SVGCenteredElement (SVGElement) :
	def __init__ (self, id=None, parent=None, nodename=None) :
		SVGElement.__init__(self,id,parent,nodename)
	
	def radius (self) :
		return self._transform.getTransformationB()[0]
	
	def center (self) :
		return self._transform.getTransformationB()[2]

class SVGBox (SVGCenteredElement) :
	"""
	a square or a box
	"""
	def __init__ (self, id=None, parent=None) :
		SVGCenteredElement.__init__(self,id,parent,"svg:rect")
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGCenteredElement.load(self)
		rx = float(self.get_default("width",0) ) / 2.
		ry = float(self.get_default("height",0) ) / 2.
		cx = float(self.get_default("x",0) ) + rx
		cy = float(self.get_default("y",0) ) + ry
		cx,cy = self.real_pos(cx,cy)
		self._transform *= Matrix4.translation( (cx,cy,0) )#order is important
		self._transform *= Matrix4(scaling( (rx,ry,1) ) )
	
	def save (self) :
		inv = lambda x : 1. / x if abs(x) > 1e-6 else 0.
		rx,ry,rz = self.radius()
		cx,cy,cz = self.center()
		self._transform *= Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz) ) ) )
		self._transform *= Matrix4.translation( (-cx,-cy,-cz) )
		self.set_attribute("width","%f" % (2 * rx) )
		self.set_attribute("height","%f" % (2 * ry) )
		self.set_attribute("depth","%f" % (2 * rz) )
		svgcx,svgcy = self.svg_pos(cx,cy)
		self.set_attribute("x","%f" % (svgcx - rx) )
		self.set_attribute("y","%f" % (svgcy - ry) )
		SVGCenteredElement.save(self)
		self._transform *= Matrix4.translation( (cx,cy,cz) )
		self._transform *= Matrix4(scaling( (rx,ry,rz) ) )
	##############################################
	#
	#		pgl interface #TODO deprecated
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		pglshape.geometry=Box(Vector3(1,1,1))
		SVGCenteredElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		pglshape.geometry=Box(Vector3(1,1,1))
		SVGCenteredElement.to_pgl3D(self,pglshape)

class SVGSphere (SVGCenteredElement,SVGPath) :
	"""
	a circle or sphere
	"""
	def __init__ (self, id=None, parent=None) :
		SVGPath.__init__(self,id,parent)
		#SVGCenteredElement.__init__(self)
		self.set_attribute("sodipodi:type","arc")
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGPath.load(self)
		rx = float(self.get_default("sodipodi:rx",0) )
		ry = float(self.get_default("sodipodi:ry",0) )
		cx = float(self.get_default("sodipodi:cx",0) )
		cy = float(self.get_default("sodipodi:cy",0) )
		cx,cy = self.real_pos(cx,cy)
		self._transform *= Matrix4.translation( (cx,cy,0) )#order is important
		self._transform *= Matrix4(scaling( (rx,ry,1) ) )
	
	def save (self) :
		inv = lambda x : 1. / x if abs(x)>1e-6 else 0.
		rx,ry,rz = self.radius()
		cx,cy,cz = self.center()
		self._transform *= Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz) ) ) )
		self._transform *= Matrix4.translation( (-cx,-cy,-cz) )
		self.set_attribute("sodipodi:rx","%f" % rx)
		self.set_attribute("sodipodi:ry","%f" % ry)
		svgcx,svgcy = self.svg_pos(cx,cy)
		self.set_attribute("sodipodi:cx","%f" % svgcx)
		self.set_attribute("sodipodi:cy","%f" % svgcy)
		SVGPath.save(self)
		self._transform *= Matrix4.translation( (cx,cy,cz) )
		self._transform *=Matrix4(scaling( (rx,ry,rz) ) )
	##############################################
	#
	#		pgl interface #TODO deprecated
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		pglshape.geometry=Sphere(1.,32)
		SVGPath.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		pglshape.geometry=Sphere(1.,8)
		SVGPath.to_pgl3D(self,pglshape)

class SVGImage (SVGElement) :
	"""
	an image represented in pgl as a square with an image texture
	"""
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:image")
		self._filename = None
		self._image = None
	
	def size (self) :
		v = self._transform.getTransformationB()[0]
		return v[0],v[1]
	
	def pos (self) :
		return self._transform.getTransformationB()[2]
	
	def filename (self) :
		return self._filename
	
	def set_filename (self, filename) :
		self._filename = filename
	
	def absfilename (self) :
		return self.abs_path(self.filename() )
	
	def image (self) :
		return self._image
	
	def set_image (self, image) :
		self._image = image
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGElement.load(self)
		width = float(self.get_default("width",0) )
		height = float(self.get_default("height",0) )
		x = float(self.get_default("x",0) )
		y = float(self.get_default("y",0) )
		self.set_filename(str(self.get_default("xlink:href","") ) )
		x,y = self.real_pos(x,y+height)
		self._transform *= Matrix4.translation( (x,y,0.) )#order is important
		self._transform *= Matrix4(scaling((width,height,1.) ) )
	
	def save (self) :
		inv = lambda x : 1./x if abs(x)>1e-6 else 0.
		width,height = self.size()
		x,y,z = self.pos()
		self._transform *= Matrix4(scaling(tuple(inv(r) for r in (width,height,1.) ) ) )
		self._transform *= Matrix4.translation( (-x,-y,-z) )
		svgx,svgy = self.svg_pos(x,y)
		self.set_attribute("x","%f" % svgx)
		self.set_attribute("y","%f" % (svgy-height) )
		self.set_attribute("width","%f" % width)
		self.set_attribute("height","%f" % height)
		self.set_attribute("xlink:href",self.filename() )
		SVGElement.save(self)
		self._transform *= Matrix4.translation( (x,y,z) )
		self._transform *= Matrix4(scaling( (width,height,1.) ) )
	##############################################
	#
	#		pgl interface #TODO deprecated
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		e=1e-2
		qs=QuadSet([(0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.)],
						[(0,1,2,3)])
		qs.texCoordList=[(0.+e,0.+e),(1.-e,0.+e),(1.-e,1.-e),(0.+e,1.-e)]
		tex=ImageTexture(self.absfilename())
		pglshape.geometry=qs
		pglshape.appearance=tex
		SVGElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		e=1e-2
		qs=QuadSet([(0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.)],
						[(0,1,2,3)])
		qs.texCoordList=[(0.+e,0.+e),(1.-e,0.+e),(1.-e,1.-e),(0.+e,1.-e)]
		tex=ImageTexture(self.absfilename())
		pglshape.geometry=qs
		pglshape.appearance=tex
		SVGElement.to_pgl3D(self,pglshape)

