from openalea.plantgl.scenegraph import Shape,Polyline,Color3
from openalea.plantgl.math import Vector3,Matrix3,Matrix4,scaling,norm
from svg_element import SVGElement

class SVGGroup (SVGElement) :
	"""
	container that group svg primitives
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGElement.__init__(self,parent,svgid)
		self._size=Vector3()
		self._elms=[]
	
	def size (self,) :
		return self._size
	
	def set_size (self, width, height, depth=0.) :
		self._size=Vector3(width,height,depth)
	
	def elements (self) :
		return iter(self._elms)
	
	def __iter__ (self) :
		return self.elements()
	
	def __len__ (self) :
		return len(self._elms)
	
	def __getitem__ (self, ind) :
		return self._elms[ind]
	
	def update_size (self, svggroupe) :
		if norm(svggroupe.size())<1e-6 :
			svggroupe.set_size(*self.size())
		for elm in svggroupe.elements() :
			if isinstance(elm,SVGGroup) :
				self.update_size(elm)

	def append( self, svgelm) :
		self._elms.append(svgelm)
		svgelm._parent_elm=self
		if isinstance(svgelm,SVGGroup) :
			self.update_size(svgelm)
	
	def get_id (self, svgid) :
		for elm in self.elements() :
			if elm.svgid()==svgid :
				return elm
			if isinstance(elm,SVGGroup) :
				finded=elm.get_id(svgid)
				if finded is not None :
					return finded
	
	def get_elm_transformation (self, elm) :
		tr=elm.global_transformation()
		dum=elm.parent()
		while (dum is not None) and (dum != self) :
			tr=dum.global_transformation(tr)
			dum=dum.parent()
		if dum is None :
			raise UserWarning("not a child of this node")
		else :
			return self.global_transformation(tr)
	##############################################
	#
	#		elements factory
	#
	##############################################
	def create_node (self, svgnode) :
		return svgnode.ownerDocument.createElement("created")
	
	def svg_element (self, svgnode) :
		if svgnode.nodeName=="#text" :#text node do nothing
			return None
		elif svgnode.nodeName=="defs" :
			return None
		elif svgnode.nodeName=="sodipodi:namedview" :
			return None
		elif svgnode.nodeName=="metadata" :
			return None
		elif svgnode.nodeName=="use" :
			return None
		elif svgnode.nodeName=="path" :#soit un path soit un cercle soit un connecteur
			svgtype=svgnode.getAttribute("sodipodi:type")
			if svgtype=="" : #c'est un path ou un connecteur
				if svgnode.getAttribute("inkscape:connector-type")=="" : #c'est un path
					return SVGPath(self)
				else : #c'est un connecteur
					return SVGConnector(self)
			elif svgtype=="arc" : #c'est un cercle
				return SVGSphere(self)
			else :
				raise UserWarning("node not recognized")
		elif svgnode.nodeName=="rect" :
			return SVGBox(self)
		elif svgnode.nodeName=="g" :#soit un groupe soit un layer
			if svgnode.getAttribute("inkscape:groupmode")=="layer" : #soit un layer soit un stack
				if svgnode.getAttribute("descr")=="stack" :
					return SVGStack(self)
				else :
					return SVGLayer(self)
			else :
				return SVGGroup(self)
		elif svgnode.nodeName=="image" :
			return SVGImage(self)
		else :
			return None
	##############################################
	#
	#		xml interface
	#
	##############################################
	def real_pos (self, svgx, svgy) :
		x,y=self.real_vec(svgx,svgy)
		w,h,d=self.size()
		return x,y+h
	
	def svg_pos (self, x, y) :
		w,h,d=self.size()
		return self.svg_vec(x,y-h)
	
	def real_transformation (self, matrix) :
		w,h,d=self.size()
		return Matrix4.translation( (0,h,0) )*self.real_matrix(matrix)*Matrix4.translation( (0,-h,0) )
	
	def svg_transformation (self, matrix) :
		w,h,d=self.size()
		return Matrix4.translation( (0,h,0) )*self.svg_matrix(matrix)*Matrix4.translation( (0,-h,0) )
	
	def load (self, svgnode) :
		#modification atttributs de style
		if self.fill is None :
			self.fill=Color3(255,255,255)
		if self.parent() is None :
			w,h,d=0,0,0
		else :
			w,h,d=self.parent().size()
		width=float(self.get_default(svgnode,"width",w))
		height=float(self.get_default(svgnode,"height",h))
		depth=float(self.get_default(svgnode,"depth",d))
		self.set_size(width,height,depth)
		#common attributes
		SVGElement.load(self,svgnode)
		#recherche des elements du groupe
		for node in svgnode.childNodes :
			svgelm=self.svg_element(node)
			if svgelm is not None :
				svgelm.load(node)
				self.append(svgelm)
	
	def save (self, svgnode) :
		SVGElement.save(self,svgnode)
		self.set_node_type(svgnode,"g")
		w,h,d=self.size()
		svgnode.setAttribute("width",str(w))
		svgnode.setAttribute("height",str(h))
		svgnode.setAttribute("depth",str(d))
		#enregistrement des elements du groupe
		for svgelm in self.elements() :
			node=self.create_node(svgnode)
			svgnode.appendChild(node)
			svgelm.save(node)
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def _hack_pgl2D_group (self, pglshape) :
		try :
			for shp in pglshape._shape_list :
				shp.geometry=self.pgl_transfo2D(shp.geometry)
				self._hack_pgl2D_group(shp)
		except AttributeError :
			pass
	
	def to_pgl2D (self, pglshape) :
		shp_list=[]
		for svgelm in self.elements() :
			shp=Shape()
			svgelm.to_pgl2D(shp)
			shp.geometry=self.pgl_transfo2D(shp.geometry)
			self._hack_pgl2D_group(shp)
			shp_list.append(shp)
		pglshape._shape_list=shp_list#TODO Hack for fucking plantgl
		w,h,d=self.size()
		pglshape.geometry=Polyline([(0,0,0),(w,0,0),(w,h,0),(0,h,0),(0,0,0)])
		SVGElement.to_pgl2D(self,pglshape)
	
	def _hack_pgl3D_group (self, pglshape) :
		try :
			for shp in pglshape._shape_list :
				shp.geometry=self.pgl_transfo3D(shp.geometry)
				self._hack_pgl3D_group(shp)
		except AttributeError :
			pass
	
	def to_pgl3D (self, pglshape) :
		shp_list=[]
		for svgelm in self.elements() :
			shp=Shape()
			svgelm.to_pgl3D(shp)
			shp.geometry=self.pgl_transfo3D(shp.geometry)
			self._hack_pgl3D_group(shp)
			shp_list.append(shp)
		pglshape._shape_list=shp_list#TODO Hack for fucking plantgl
		w,h,d=self.size()
		pglshape.geometry=Polyline([(0,0,0),(w,0,0),(w,0,d),(w,h,d),(w,h,0),(0,h,0),(0,0,0)])
		SVGElement.to_pgl3D(self,pglshape)
	
	def pgl_3D (self, svgelm) :
		shp=Shape()
		svgelm.to_pgl3D(shp)
		dum=svgelm.parent()
		while (dum is not None) and (dum != self) :
			shp.geometry=dum.pgl_transfo3D(shp.geometry)
			dum=dum.parent()
		if dum is None :
			raise UserWarning("not a child of this node")
		else :
			shp.geometry=self.pgl_transfo3D(shp.geometry)
			return shp

class SVGLayer (SVGGroup) :
	"""
	add a layer attribute to SVGGroup
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGGroup.__init__(self,parent,svgid)
		if svgid is None :
			self._name="lay"
		else :
			self._name=svgid
	
	def name (self) :
		return self._name
	
	def set_name (self, name) :
		self._name=name
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self, svgnode) :
		SVGGroup.load(self,svgnode)
		self.set_name(str(self.get_default(svgnode,"inkscape:label","lay")))
	
	def save (self, svgnode) :
		SVGGroup.save(self,svgnode)
		svgnode.setAttribute("inkscape:label",str(self.name()))
		svgnode.setAttribute("inkscape:groupmode","layer")

from svg_primitive import SVGBox,SVGSphere,SVGImage
from svg_path import SVGPath,SVGConnector
from svg_stack import SVGStack

