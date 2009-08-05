from openalea.plantgl.scenegraph import Sphere,Box,FaceSet,QuadSet,Translated,Scaled,ImageTexture
from openalea.plantgl.math import Vector3,Matrix4,eulerRotationZYX,scaling
from svg_element import SVGElement
from xml_element import XMLElement,ELEMENT_TYPE,TEXT_TYPE

class SVGCenteredElement (SVGElement) :
	def __init__ (self, id=None, parent=None, nodename=None) :
		SVGElement.__init__(self,id,parent,nodename)
	
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
	def __init__ (self, id=None, parent=None) :
		SVGCenteredElement.__init__(self,id,parent,"svg:rect")
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGCenteredElement.load(self)
		rx=float(self.get_default("width",0))/2.
		ry=float(self.get_default("height",0))/2.
		rz=float(self.get_default("depth",0))/2.
		cx=float(self.get_default("x",0))+rx
		cy=float(self.get_default("y",0))+ry
		cz=float(self.get_default("z",0))+rz
		cx,cy=self.real_pos(cx,cy)
		self._transform2D*=Matrix4.translation((cx,cy,cz))#l'ordre est important
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	
	def save (self) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		rx,ry,rz=self.radius()
		cx,cy,cz=self.center()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz))))
		self._transform2D*=Matrix4.translation( (-cx,-cy,-cz) )
		self.set_attribute("width","%f" % (2*rx))
		self.set_attribute("height","%f" % (2*ry))
		self.set_attribute("depth","%f" % (2*rz))
		svgcx,svgcy=self.svg_pos(cx,cy)
		self.set_attribute("x","%f" % (svgcx-rx))
		self.set_attribute("y","%f" % (svgcy-ry))
		self.set_attribute("z","%f" % (cz-rz))
		SVGCenteredElement.save(self)
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
	def __init__ (self, id=None, parent=None) :
		SVGCenteredElement.__init__(self,id,parent,"svg:path")
		self.set_attribute("sodipodi:type","arc")
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGCenteredElement.load(self)
		rx=float(self.get_default("sodipodi:rx",0))
		ry=float(self.get_default("sodipodi:ry",0))
		rz=float(self.get_default("sodipodi:rz",0))
		cx=float(self.get_default("sodipodi:cx",0))
		cy=float(self.get_default("sodipodi:cy",0))
		cz=float(self.get_default("sodipodi:cz",0))
		cx,cy=self.real_pos(cx,cy)
		self._transform2D*=Matrix4.translation((cx,cy,cz))#l'ordre est important
		self._transform2D*=Matrix4(scaling((rx,ry,rz)))
	
	def save (self) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		rx,ry,rz=self.radius()
		cx,cy,cz=self.center()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (rx,ry,rz))))
		self._transform2D*=Matrix4.translation( (-cx,-cy,-cz) )
		self.set_attribute("sodipodi:rx","%f" % rx)
		self.set_attribute("sodipodi:ry","%f" % ry)
		self.set_attribute("sodipodi:rz","%f" % rz)
		svgcx,svgcy=self.svg_pos(cx,cy)
		self.set_attribute("sodipodi:cx","%f" % svgcx)
		self.set_attribute("sodipodi:cy","%f" % svgcy)
		self.set_attribute("sodipodi:cz","%f" % cz)
		SVGCenteredElement.save(self)
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
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:image")
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
	def load (self) :
		SVGElement.load(self)
		width=float(self.get_default("width",0))
		height=float(self.get_default("height",0))
		x=float(self.get_default("x",0))
		y=float(self.get_default("y",0))
		z=float(self.get_default("z",0))
		self.set_filename(str(self.get_default("xlink:href","")))
		x,y=self.real_pos(x,y+height)
		self._transform2D*=Matrix4.translation((x,y,z))#l'ordre est important
		self._transform2D*=Matrix4(scaling((width,height,1.)))
	
	def save (self) :
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		width,height=self.size()
		x,y,z=self.pos()
		self._transform2D*=Matrix4(scaling(tuple(inv(r) for r in (width,height,1.))))
		self._transform2D*=Matrix4.translation( (-x,-y,-z) )
		svgx,svgy=self.svg_pos(x,y)
		self.set_attribute("x","%f" % svgx)
		self.set_attribute("y","%f" % (svgy-height))
		self.set_attribute("z","%f" % z)
		self.set_attribute("width","%f" % width)
		self.set_attribute("height","%f" % height)
		self.set_attribute("xlink:href",self.filename())
		SVGElement.save(self)
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
class SVGText (SVGElement) :
	"""
	a text positioned in space
	"""
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:text")
		self._txt = None
		self._font_size = 0
	
	def pos (self) :
		return self._transform2D.getTransformationB()[2]
	
	def text (self) :
		return self._txt
	
	def set_text (self, txt) :
		self._txt = txt
	
	def font_size (self) :
		return self._font_size
	
	def set_font_size (self, size) :
		self._font_size = size
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGElement.load(self)
		x = float(self.get_default("x",0) )
		y = float(self.get_default("y",0) )
		z = float(self.get_default("z",0) )
		x,y = self.real_pos(x,y)
		self._transform2D *= Matrix4.translation( (x,y,z) )
		#font size
		if self.has_attribute("style") :
			style=self.attribute("style")
			for style_elm in style.split(";") :
				key,val=style_elm.split(":")
				if key == "font-size" :
					#assert val end with px
					self._font_size = int(val[:-2])
		
		tspan = self.child(0)
		txtnode = tspan.child(0)
		self._txt = txtnode.get_default('data',"")
	
	def save (self) :
		x,y,z = self.pos()
		self._transform2D *= Matrix4.translation( (-x,-y,-z) )
		svgx,svgy = self.svg_pos(x,y)
		self.set_attribute("x","%f" % svgx)
		self.set_attribute("y","%f" % svgy)
		self.set_attribute("z","%f" % z)
		self.set_attribute("xml:space","preserve")
		#font size
		style={}
		if self.has_attribute("style") :
			for gr in self.attribute("style").split(";") :
				k,v=gr.split(":")
				style[k]=v
		style["font-size"] = "%dpx" % self.font_size()
		style["font-style"] = "normal"
		style["font-weight"] = "normal"
		style["text-align"] = "start"
		style["text-anchor"] = "start"
		style["font-family"] = "Bitstream Vera Sans"
		self.set_attribute("style",";".join(["%s:%s" % it for it in style.iteritems()]))
		
		#span
		if self.nb_children() > 1 :
			raise UserWarning("trouble with text node")
		if self.nb_children() == 1 :
			span = self.child(0)
			assert span.nodetype() == ELEMENT_TYPE
			assert span.nodename() == "svg:tspan"
		else :
			span = XMLElement(None,ELEMENT_TYPE,"svg:tspan")
			self.add_child(span)
		span.set_attribute("x","%f" % svgx)
		span.set_attribute("y","%f" % svgy)
		span.set_attribute("sodipodi:role","line")
		#txt
		if span.nb_children() > 1 :
			raise UserWarning("trouble with text node")
		if span.nb_children() == 1 :
			txt = span.child(0)
			assert txt.nodetype() == TEXT_TYPE
		else :
			txt = XMLElement(None,TEXT_TYPE)
			span.add_child(txt)
		txt.set_attribute("data","%s" % self.text() )
		#save
		SVGElement.save(self)
		self._transform2D *= Matrix4.translation( (x,y,z) )
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def to_pgl2D (self, pglshape) :
		raise NotImplementedError
	
	def to_pgl3D (self, pglshape) :
		raise NotImplementedError

