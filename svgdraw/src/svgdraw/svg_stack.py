from os.path import join,normpath
from openalea.plantgl.math import Vector3,Matrix4,eulerRotationZYX,translation,scaling
from svg_group import SVGGroup,SVGLayer
from svg_primitive import SVGImage

class SVGStackVariant (object) :
	def __init__ (self, name=None, scale=1., rep=None) :
		self._name=name
		self._scale=scale
		self._rep=rep
	
	def scale (self) :
		return self._scale
	
	def set_scale (self, scale) :
		self._scale=scale
	
	def name (self) :
		return self._name
	
	def set_name (self, name) :
		self._name=str(name)
		if self._rep is None :
			self._rep=str(name)
	
	def rep (self) :
		return self._rep
	
	def set_rep (self, rep) :
		self._rep=str(rep)
		if self._name is None :
			self._name=str(rep)

class SVGStack (SVGLayer) :
	"""
	object used to manipulate a stack of images
	"""
	def __init__ (self, parent=None, svgid=None) :
		SVGLayer.__init__(self,parent,svgid)
		self.display=False
		self._variants=[]
		self._variant_used=None
		self._masked=[]
	
	def resolution (self) :
		return self._transform3D.getTransformationB()[0]
	
	def add_image (self, image_name, width, height, masked=False) :
		ind=len(self)
		gr=SVGLayer(self,"gslice%.4d" % ind)
		self.append(gr)
		gr.set_size(width,height)
		gr.translate( (0,0,ind) )
		gr.display=False
		im=SVGImage(gr,"slice%.4d" % ind)
		gr.append(im)
		im.set_filename(image_name)
		im.scale2D( (width,height,0) )
		self._masked.append(masked)
	
	def image (self, ind) :
		return self[ind][0]
	
	def images (self) :
		for i in xrange(len(self)) :
			yield self.image(i)
	
	def nb_images (self) :
		return len(self)
	
	def display_image (self, ind, visible=True) :
		self[ind].display=visible
	
	def variants (self) :
		return iter(self._variants)
	
	def nb_variants (self) :
		return len(self._variants)
	
	def add_variant (self, name, scale=1, rep=None) :
		var=SVGStackVariant(name,scale,rep)
		var.set_name(name)
		self._variants.append(var)
		return len(self._variants)-1
	
	def variant_used (self) :
		if self._variant_used is None :
			return None
		else :
			return self._variants[self._variant_used]
	
	def use_variant (self, variant=None) :
		if self._variant_used!=variant :
			#retrait de l'ancien
			if self._variant_used is not None :
				var=self.variant_used()
				var_sca=1./var.scale()
				#self._transform3D*=Matrix4(scaling((var_sca,var_sca,1.)))
				var_pth=var.rep()
				for elm in self.elements() :
					svgim=elm[0]
					impth=normpath(svgim.filename().replace(var_pth,""))
					svgim.set_filename(impth)
			self._variant_used=variant
			#ajout du nouveau
			if self._variant_used is not None :
				var=self.variant_used()
				var_sca=var.scale()
				#self._transform3D*=Matrix4(scaling((var_sca,var_sca,1.)))
				var_pth=var.rep()
				for elm in self.elements() :
					svgim=elm[0]
					svgim.set_filename(join(var_pth,svgim.filename()))
	##############################################
	#
	#		xml interface
	#
	##############################################
	def load (self, svgnode) :
		SVGLayer.load(self,svgnode)
		if self.nb_images()>0 :
			w,h,d=self.size()
			self.set_size(w,h,self.nb_images()-1)
		dx=float(self.get_default(svgnode,"dx",1.))
		dy=float(self.get_default(svgnode,"dy",1.))
		dz=float(self.get_default(svgnode,"dz",1.))
		self._transform3D*=Matrix4(scaling((dx,dy,dz)))
		#variants
		for node in svgnode.childNodes :
			if node.nodeName=="variant" :
				name=self.get_default(node,"name",None)
				if name is not None :
					name=str(name)
				scale=float(self.get_default(node,"scale",1.))
				rep=self.get_default(node,"rep",None)
				if rep is not None :
					rep=str(rep)
				self.add_variant(name,scale,rep)
		#masked images
		self._masked=[]
		for im in self.images() :
			name=im.filename()
			if name[-1]=="X" :
				self._masked.append(True)
				im.set_filename(name[:-1])
			else :
				self._masked.append(False)
	
	def save (self, svgnode) :
		var_mem=self._variant_used
		self.use_variant(None)
		#variants
		for var in self._variants :
			node=self.create_node(svgnode)
			self.set_node_type(node,"variant")
			svgnode.appendChild(node)
			node.setAttribute("name",var.name())
			node.setAttribute("scale",str(var.scale()))
			node.setAttribute("rep",var.rep())
		#node
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		dx,dy,dz=self.resolution()
		self._transform3D*=Matrix4(scaling(tuple(inv(r) for r in (dx,dy,dz))))
		#masked
		for i in xrange(len(self)) :
			im=self.image(i)
			if self._masked[i] :
				im.set_filename("%sX" % im.filename())
		SVGLayer.save(self,svgnode)
		svgnode.setAttribute("descr","stack")
		svgnode.setAttribute("dx","%f" % dx)
		svgnode.setAttribute("dy","%f" % dy)
		svgnode.setAttribute("dz","%f" % dz)
		self._transform3D*=Matrix4(scaling((dx,dy,dz)))
		#masked
		for i in xrange(len(self)) :
			im=self.image(i)
			if self._masked[i] :
					im.set_filename(im.filename()[:-1])
		#variant
		self.use_variant(var_mem)
	##############################################
	#
	#		pgl interface
	#
	##############################################

