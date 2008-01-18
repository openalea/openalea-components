from openalea.plantgl.scenegraph import Sphere,Box,FaceSet,QuadSet,Translated,Scaled,ImageTexture
from openalea.plantgl.math import Vector3,Matrix4,eulerRotationZYX,scaling
from svg_element import SVGElement

class SVGCenteredElement (SVGElement) :
	def __init__ (self, parent=None, svgid=None) :
		SVGElement.__init__(self,parent,svgid)
	
	def radius (self) :
		return self._transform2D.getTransformationB()[0]
	
	def center (self) :
		return self._transform2D.getTransformationB()[2]
	
	def rotate (self, angle) :
		SVGElement.rotate(self,angle)
		rot=eulerRotationZYX((-angle,0,0))
		self._center=rot*self._center

class SVGBox (SVGCenteredElement) :
	"""
	a square or a box
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGCenteredElement.__init__(self,parent,svgid)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self, svgnode) :
		SVGCenteredElement.load(self,svgnode)
		rx=float(self.get_default(svgnode,"width",0))/2.
		ry=float(self.get_default(svgnode,"height",0))/2.
		rz=float(self.get_default(svgnode,"depth",0))/2.
		cx=float(self.get_default(svgnode,"x",0))+rx
		cy=float(self.get_default(svgnode,"y",0))+ry
		cz=float(self.get_default(svgnode,"z",0))+rz
		cx,cy=self.real_pos(cx,cy)
		self._transform2D*=Matrix4.translation((cx,cy,cz))#l'ordre est important
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	
	def save (self, svgnode) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		rx,ry,rz=self.radius()
		cx,cy,cz=self.center()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz))))
		self._transform2D*=Matrix4.translation( (-cx,-cy,-cz) )
		SVGCenteredElement.save(self,svgnode)
		self.set_node_type(svgnode,"rect")
		svgnode.setAttribute("width","%f" % (2*rx))
		svgnode.setAttribute("height","%f" % (2*ry))
		svgnode.setAttribute("depth","%f" % (2*rz))
		svgcx,svgcy=self.svg_pos(cx,cy)
		svgnode.setAttribute("x","%f" % (svgcx-rx))
		svgnode.setAttribute("y","%f" % (svgcy-ry))
		svgnode.setAttribute("z","%f" % (cz-rz))
		self._transform2D*=Matrix4.translation((cx,cy,cz))
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		pglshape.geometry=Box(Vector3(1,1,1))
		SVGCenteredElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		pglshape.geometry=Box(Vector3(1,1,1))
		SVGCenteredElement.to_pgl3D(self,pglshape)

class SVGSphere (SVGCenteredElement) :
	"""
	a circle or sphere
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGCenteredElement.__init__(self,parent,svgid)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self, svgnode) :
		SVGCenteredElement.load(self,svgnode)
		rx=float(self.get_default(svgnode,"sodipodi:rx",0))
		ry=float(self.get_default(svgnode,"sodipodi:ry",0))
		rz=float(self.get_default(svgnode,"sodipodi:rz",0))
		cx=float(self.get_default(svgnode,"sodipodi:cx",0))
		cy=float(self.get_default(svgnode,"sodipodi:cy",0))
		cz=float(self.get_default(svgnode,"sodipodi:cz",0))
		cx,cy=self.real_pos(cx,cy)
		self._transform2D*=Matrix4.translation((cx,cy,cz))#l'ordre est important
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	
	def save (self, svgnode) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		rx,ry,rz=self.radius()
		cx,cy,cz=self.center()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz))))
		self._transform2D*=Matrix4.translation( (-cx,-cy,-cz) )
		SVGCenteredElement.save(self,svgnode)
		self.set_node_type(svgnode,"path")
		svgnode.setAttribute("sodipodi:type","arc")
		svgnode.setAttribute("sodipodi:rx","%f" % rx)
		svgnode.setAttribute("sodipodi:ry","%f" % ry)
		svgnode.setAttribute("sodipodi:rz","%f" % rz)
		svgcx,svgcy=self.svg_pos(cx,cy)
		svgnode.setAttribute("sodipodi:cx","%f" % svgcx)
		svgnode.setAttribute("sodipodi:cy","%f" % svgcy)
		svgnode.setAttribute("sodipodi:cz","%f" % cz)
		self._transform2D*=Matrix4.translation((cx,cy,cz))
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		pglshape.geometry=Sphere(1.,32)
		SVGCenteredElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		pglshape.geometry=Sphere(1.,8)
		SVGCenteredElement.to_pgl3D(self,pglshape)

class SVGImage (SVGElement) :
	"""
	an image represented in pgl as a square with an image texture
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGElement.__init__(self,parent,svgid)
		self._filename=None
		self._image=None
	
	def size (self) :
		v=self._transform2D.getTransformationB()[0]
		return v[0],v[1]
	
	def pos (self) :
		return self._transform2D.getTransformationB()[2]
	
	def filename (self) :
		return self._filename
	
	def set_filename (self, filename) :
		self._filename=filename
	
	def absfilename (self) :
		return self.abs_path(self.filename())
	
	def image (self) :
		return self._image
	
	def set_image (self, image) :
		self._image=image
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self, svgnode) :
		SVGElement.load(self,svgnode)
		width=float(self.get_default(svgnode,"width",0))
		height=float(self.get_default(svgnode,"height",0))
		x=float(self.get_default(svgnode,"x",0))
		y=float(self.get_default(svgnode,"y",0))
		z=float(self.get_default(svgnode,"z",0))
		self.set_filename(str(self.get_default(svgnode,"xlink:href","")))
		x,y=self.real_pos(x,y+height)
		self._transform2D*=Matrix4.translation((x,y,z))#l'ordre est important
		self._transform2D*=Matrix4(scaling((width,height,1.)))
	
	def save (self, svgnode) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		width,height=self.size()
		x,y,z=self.pos()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (width,height,1.))))
		self._transform2D*=Matrix4.translation( (-x,-y,-z) )
		SVGElement.save(self,svgnode)
		self.set_node_type(svgnode,"image")
		svgx,svgy=self.svg_pos(x,y)
		svgnode.setAttribute("x","%f" % svgx)
		svgnode.setAttribute("y","%f" % (svgy-height))
		svgnode.setAttribute("z","%f" % z)
		svgnode.setAttribute("width","%f" % width)
		svgnode.setAttribute("height","%f" % height)
		svgnode.setAttribute("xlink:href",self.filename())
		self._transform2D*=Matrix4.translation((x,y,z))
		self._transform2D*=Matrix4(scaling((width,height,1.)))
	##############################################
	#
	#		pgl interface
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

