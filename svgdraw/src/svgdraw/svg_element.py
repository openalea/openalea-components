import re
from os.path import join,dirname
from math import sin,cos,acos,asin
from openalea.plantgl.scenegraph import Material,Color3,\
								Translated,Scaled,AxisRotated,Transformed
from openalea.plantgl.math import Vector3,Matrix3,Matrix4,eulerRotationZYX,scaling,norm
from xml_element import XMLElement,SVG_ELEMENT_TYPE

Ox=Vector3(1,0,0)
Oy=Vector3(0,1,0)
Oz=Vector3(0,0,1)

#to read svg transformations or values
#norm : http://www.w3.org/TR/SVG/coords.html#TransformAttribute
sep=r"\s*,?\s*"
digit=r"([-]?\d+[.]?\d*e?[+-]?\d?)"
val_re=re.compile(digit+r"(em)?(ex)?(px)?(pt)?(pc)?(cm)?(mm)?(in)?(\%)?")

matrix_re=re.compile("matrix\("+digit+sep+digit+sep+digit+sep+digit+sep+digit+sep+digit+"\)")
translate_re=re.compile("translate\("+digit+sep+digit+"?\)")
scale_re=re.compile("scale\("+digit+sep+digit+"?\)")

matrix_re3D=re.compile("matrix\("+sep+digit+sep+digit+sep+digit+sep+digit
								 +sep+digit+sep+digit+sep+digit+sep+digit
								 +sep+digit+sep+digit+sep+digit+sep+digit+sep+"\)")

translate_re3D=re.compile("translate\("+digit+sep+digit+"?"+sep+digit+"?\)")
scale_re3D=re.compile("scale\("+digit+sep+digit+"?"+sep+digit+"?\)")

class SVGElement (XMLElement) :
	"""
	base class for all styles associated with geometrical elements
	store all attributes that cannot be stored in a plantgl scene
	"""
	type="style"
	def __init__ (self, id=None, parent=None, nodename="svg") :
		XMLElement.__init__(self,parent,SVG_ELEMENT_TYPE,nodename)
		self._id=id
		#graphic style
		self.display=True
		self.fill=None
		self.stroke=None
		self.stroke_width=1.
		#transformation2D
		self._transform2D=Matrix4()#matrice de transformation
								#de la base locale vers la base du parent
								#parent_pos=transform*local_pos
		#transformation3D
		self._absolute_3D=False#transformation relative to 2D transfo or not
		self._transform3D=Matrix4()#matrice 3D de transformation
								#de la base locale vers la base du parent
		#filename for abs path
		self._svgfilename=None
	
	def id (self) :
		return self._id
	
	def set_id (self, id) :
		self._id=id
	##############################################
	#
	#		3D change of referential
	#
	##############################################
	def is_absolute (self) :
		return self._absolute_3D
	
	def global_transformation (self, matrix=Matrix4()) :
		gtr=self._transform3D*matrix
		if self.is_absolute() :
			return gtr
		else :
			return self.global_transformation2D(gtr)
	
	def global_pos (self, pos=Vector3()) :
		gpos=self._transform3D*pos
		if self.is_absolute() :
			return gpos
		else :
			return self.global_pos2D(gpos)
	
	def global_vec (self, vec=Vector3()) :
		gvec=Matrix3(self._transform3D)*vec
		if self.is_absolute() :
			return gvec
		else :
			return self.global_vec2D(gvec)
	
	def global_scale (self, scale=(1,1,1)) :
		gsca=tuple(scale[i]*self._transform3D[i,i] for i in xrange(3))
		if self.is_absolute() :
			return gsca
		else :
			return self.global_scale2D(gsca)
	
	def local_pos (self, pos=Vector3()) :
		lpos=self._transform3D.inverse()*pos
		if self.is_absolute() :
			return lpos
		else :
			return self.local_pos2D(lpos)
	
	def local_vec (self, vec=Vector3()) :
		lvec=Matrix3(self._transform3D.inverse())*vec
		if self.is_absolute() :
			return lvec
		else :
			return self.local_vec2D(lvec)
	
	def local_scale (self, scale=(1,1,1)) :
		lsca=tuple(scale[i]/self._transform3D[i,i] for i in xrange(3))
		if self.is_absolute() :
			return lsca
		else :
			return self.local_scale2D(lsca)
	
	def abs_pos (self, pos=Vector3()) :
		ppos=self.global_pos(pos)
		if self.parent() is None :
			return ppos
		else :
			return self.parent().abs_pos(ppos)
	##############################################
	#
	#		2D change of referential
	#
	##############################################
	def global_transformation2D (self, matrix=Matrix4()) :
		return self._transform2D*matrix
	
	def global_pos2D (self, pos=Vector3()) :
		return self._transform2D*pos
	
	def global_vec2D (self, vec=Vector3()) :
		return Matrix3(self._transform2D)*vec
	
	def global_scale2D (self, scale=(1,1,1)) :
		return tuple(scale[i]*self._transform2D[i,i] for i in xrange(3))
	
	def local_pos2D (self, pos=Vector3()) :
		return self._transform2D.inverse()*pos
	
	def local_vec2D (self, vec=Vector3()) :
		return Matrix3(self._transform2D.inverse())*vec
	
	def local_scale2D (self, scale=(1,1,1)) :
		return tuple(scale[i]/self._transform2D[i,i] for i in xrange(3))
	
	def abs_pos2D (self, pos=Vector3()) :
		ppos=self.global_pos2D(pos)
		if self.parent() is None :
			return ppos
		else :
			return self.parent().abs_pos2D(ppos)
	##############################################
	#
	#		change of referential
	#
	##############################################
	def set_transformation (self, matrix) :
		self._transform3D=matrix
	
	def transform (self, matrix) :
		self._transform3D=matrix*self._transform3D
	
	def translate (self, vec) :
		self._transform3D=Matrix4.translation(vec)*self._transform3D
	
	def rotate (self, ZYXangles) :
		self._transform3D=Matrix4(eulerRotationZYX(ZYXangles))*self._transform3D
	
	def scale (self, scale) :
		self._transform3D=Matrix4(scaling(scale))*self._transform3D
	
	def set_transformation2D (self, matrix) :
		self._transform2D=matrix
	
	def transform2D (self, matrix) :
		self._transform2D=matrix*self._transform2D
	
	def translate2D (self, vec) :
		self._transform2D=Matrix4.translation(vec)*self._transform2D
	
	def rotate2D (self, angle) :
		self._transform2D=Matrix4(eulerRotationZYX((angle,0,0)))*self._transform2D
	
	def scale2D (self, scale) :
		self._transform2D=Matrix4(scaling(scale))*self._transform2D
	##############################################
	#
	#		SVG interface
	#
	##############################################
	def abs_path (self, filename) :
		if self.parent() is None :
			if self._svgfilename is None :
				return filename
			else :
				return join(dirname(self._svgfilename),filename)
		else :
			return self.parent().abs_path(filename)
	
	def real_vec (self, svgx, svgy) :
		return svgx,-svgy
	
	def svg_vec (self, x, y) :
		return x,-y
	
	def real_pos (self, svgx, svgy) :
		if self.parent() is None :
			return self.real_vec(svgx,svgy)
		else :
			return self.parent().real_pos(svgx,svgy)
	
	def svg_pos (self, x, y) :
		if self.parent() is None :
			return self.svg_vec(x,y)
		else :
			return self.parent().svg_pos(x,y)
	
	def real_matrix (self, matrix) :
		m=matrix
		return Matrix4((m[0,0],-m[0,1],0,m[0,3],-m[1,0],m[1,1],0,-m[1,3]))
	
	def svg_matrix (self, matrix) :
		m=matrix
		return Matrix4((m[0,0],-m[0,1],0,m[0,3],-m[1,0],m[1,1],0,-m[1,3]))
	
	def real_transformation (self, matrix) :
		if self.parent() is None :
			return self.real_matrix(matrix)
		else :
			return self.parent().real_transformation(matrix)
	
	def svg_transformation (self, matrix) :
		if self.parent() is None :
			return self.svg_matrix(matrix)
		else :
			return self.parent().svg_transformation(matrix)
	
	def read_color (self, color_str) :
		if color_str=="none" :
			return None
		else :
			col_str=color_str.lower()[1:]
			red=int(col_str[:2],16)
			green=int(col_str[2:4],16)
			blue=int(col_str[4:],16)
			return Color3(red,green,blue)
	
	def read_value (self, val_str) :
		if val_str=="none" :
			return None
		else :
			res=val_re.match(val_str)
			return float(res.groups()[0])
	
	def load_style (self) :
		#colors
		if self.has_attribute("style") :
			style=self.attribute("style")
			for style_elm in style.split(";") :
				key,val=style_elm.split(":")
				if key=="fill" :
					self.fill=self.read_color(val)
				elif key=="stroke" :
					self.stroke=self.read_color(val)
				elif key=="stroke-width" :
					self.stroke_width=self.read_value(val)
				elif key=="display" :
					self.display= (val!="none")
	
	def load_transformation2D (self) :
		#transformation
		if self.has_attribute("transform") :
			tr=self.attribute("transform")
			if "matrix" in tr :
				x11,x21,x12,x22,x13,x23=(float(val) for val in matrix_re.match(tr).groups())
				m=Matrix4( (x11,x12,0,x13,x21,x22,0,x23) )
				self.transform2D(self.real_transformation(m))
			elif "translate" in tr :
				xtr,ytr=translate_re.match(tr).groups()
				x=float(xtr)
				if ytr is None :
					y=x
				else :
					y=float(ytr)
				x,y=self.real_vec(x,y)
				self.translate2D( (x,y,0) )
			elif "scale" in tr :
				xtr,ytr=scale_re.match(tr).groups()
				x=float(xtr)
				if ytr is None :
					y=x
				else :
					y=float(ytr)
				self.scale2D( (x,y,0) )
			elif "rotate" in tr :
				raise NotImplementedError
			elif "skewX" in tr :
				raise NotImplementedError
			elif "skewY" in tr :
				raise NotImplementedError
			else :
				raise UserWarning("don't know how to translate this transformation :\n %s" % tr)
	
	def load_transformation3D (self) :
		#transformation3D
		if self.has_attribute("transform3D") :
			tr=self.attribute("transform3D")
			if tr[0].lower()=='a' :
				self._absolute_3D=True
				tr=tr[1:]
			else :
				self._absolute_3D=False
			if "matrix" in tr :
				x11,x21,x31,x12,x22,x32,x13,x23,x33,x14,x24,x34=(float(val) for val in matrix_re3D.match(tr).groups())
				m=Matrix4( (x11,x12,x13,x14,x21,x22,x23,x24,x31,x32,x33,x34) )
				self.transform(m)
			elif "translate" in tr :
				x,y,z=(float(val) for val in translate_re3D.match(tr).groups())
				self.translate( (x,y,z) )
			elif "scale" in tr :
				x,y,z=(float(val) for val in scale_re3D.match(tr).groups())
				self.scale( (x,y,z) )
			elif "rotate" in tr :
				raise NotImplementedError
			elif "skewX" in tr :
				raise NotImplementedError
			elif "skewY" in tr :
				raise NotImplementedError
			else :
				raise UserWarning("don't know how to translate this transformation :\n %s" % tr)
	
	def load (self) :
		XMLElement.load(self)
		if self.has_attribute("id") :
			self.set_id(self.attribute("id"))
		self.load_style()
		self.load_transformation2D()
		self.load_transformation3D()
	
	def save_style (self) :
		style="opacity:1"
		if self.fill is None :
			style+=";fill:none"
		else :
			c=self.fill
			style+=";fill:#%.2x%.2x%.2x" % (c.red,c.green,c.blue)
		if self.stroke is None :
			style+=";stroke:none"
		else :
			c=self.stroke
			style+=";stroke:#%.2x%.2x%.2x" % (c.red,c.green,c.blue)
		style+=";stroke-width:%f" % self.stroke_width
		if not self.display :
			style+=";display:none"
		self.set_attribute("style",style)
	
	def save_transformation2D (self) :
		tr=self.svg_transformation(self._transform2D)
		transform="matrix(%f %f %f %f %f %f)" % (tr[0,0],tr[1,0],tr[0,1],tr[1,1],tr[0,3],tr[1,3])
		self.set_attribute("transform",transform)
	
	def save_transformation3D (self) :
		tr=self._transform3D
		transform="matrix(%f %f %f %f %f %f %f %f %f %f %f %f)" % (tr[0,0],tr[1,0],tr[2,0],tr[0,1],tr[1,1],tr[2,1],tr[0,2],tr[1,2],tr[2,2],tr[0,3],tr[1,3],tr[2,3])
		if self.is_absolute() :
			self.set_attribute("transform3D","a%s" % transform)
		else :
			self.set_attribute("transform3D",transform)
	
	def save (self) :
		XMLElement.save(self)
		if self.id() is not None :
			self.set_attribute("id",self.id())
		self.save_style()
		self.save_transformation2D()
		self.save_transformation3D()
	##############################################
	#
	#		PGL interface
	#
	##############################################
	def primitive (self, geom) :
		while isinstance(geom,Transformed) :
			geom=geom.geometry
		return geom
	
	def pgl_transfo2D (self, geom) :
		scaling,rotation,trans=self._transform2D.getTransformationB()
		if scaling[0]!=1 or scaling[1]!=1 :
			geom=Scaled(scaling,geom)
		if rotation[0]!=0 :
			geom=AxisRotated(Oz,rotation[0],geom)
		if trans[0]!=0 or trans[1]!=0 :
			geom=Translated(trans,geom)
		return geom
	
	def pgl_style (self, pglshape) :
		#style
		if pglshape.appearance is None :
			mat=Material()
		else :
			mat=pglshape.appearance
		if self.fill is None :
			if self.stroke is not None :
				mat.ambient=self.stroke
		else :
			mat.ambient=self.fill
		pglshape.appearance=mat
	
	def to_pgl2D (self, pglshape) :
		#style
		self.pgl_style(pglshape)
		#transformation
		pglshape.geometry=self.pgl_transfo2D(pglshape.geometry)
	
	def pgl_transfo3D (self, geom) :
		if self.is_absolute() :
			mat=self._transform3D
		else :
			mat=self._transform2D*self._transform3D
		scaling,rotation,trans=mat.getTransformationB()
		#scaling
		if scaling[0]!=1 or scaling[1]!=1 or scaling[2]!=1 :
			geom=Scaled(scaling,geom)
		#la rotation peut etre fausse
		#implementation perso
		mat=Matrix3(mat)
		col=[mat.getColumn(i) for i in xrange(3)]
		scal=[v.normalize() for v in col]
		mat=Matrix3(*col)
		ca=(mat.trace()-1.)/2.
		if abs(ca-1)>1e-6 :#angle!=0
			if abs(ca+1.)<1e-3 :#angle=pi
				angle=acos(ca)
				axis=Vector3(mat[2,1],mat[0,2],mat[1,0])
				if norm(axis)<1e-3 :#rotation suivant un axe du repere
					axis=Vector3()
					for i in xrange(3) :
						if mat[i,i]>0 :
							axis[i]=1
			else :
				n=mat-mat.transpose()
				if n[2,2]>0. :
					angle=acos(ca)
				else :
					angle=-acos(ca)
				n/=(2*sin(angle))
				axis=Vector3(n[2,1],n[0,2],n[1,0])
			geom=AxisRotated(axis,angle,geom)
		"""if rotation[2]!=0 :
			geom=AxisRotated(Ox,rotation[2],geom)
		if rotation[1]!=0 :
			geom=AxisRotated(Oy,rotation[1],geom)
		if rotation[0]!=0 :
			geom=AxisRotated(Oz,rotation[0],geom)"""
		#translation
		if norm(trans)>0 :
			geom=Translated(trans,geom)
		return geom
	
	def to_pgl3D (self, pglshape) :
		#style
		self.pgl_style(pglshape)
		#transformation
		pglshape.geometry=self.pgl_transfo3D(pglshape.geometry)

