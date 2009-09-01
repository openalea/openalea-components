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
This module defines an abstract svg element
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

import re
from os.path import join,dirname
from math import sin,cos,acos,asin
from openalea.plantgl.scenegraph import Material,Color3,\
								Translated,Scaled,AxisRotated,Transformed
from openalea.plantgl.math import Vector3,Matrix3,Matrix4,eulerRotationZYX,scaling,norm
from xml_element import XMLElement,SVG_ELEMENT_TYPE

Ox = Vector3(1,0,0)
Oy = Vector3(0,1,0)
Oz = Vector3(0,0,1)

#to read svg transformations or values
#norm : http://www.w3.org/TR/SVG/coords.html#TransformAttribute
sep = r"\s*,?\s*"
digit = r"([-]?\d+[.]?\d*e?[+-]?\d?)"
float_re = re.compile(digit+r"(em)?(ex)?(px)?(pt)?(pc)?(cm)?(mm)?(in)?(\%)?")

matrix_re = re.compile("matrix\("+digit+sep+digit+sep+digit+sep+digit+sep+digit+sep+digit+"\)")
translate_re = re.compile("translate\("+digit+sep+digit+"?\)")
scale_re = re.compile("scale\("+digit+sep+digit+"?\)")

def read_color (color_str) :
	if color_str == "none" :
		return None
	else : #assert haxedecimal definition
	       #of the color col = #rrggbb
		col_str = color_str.lower()[1:]#remove '#'
		red = int(col_str[:2],16)
		green = int(col_str[2:4],16)
		blue = int(col_str[4:],16)
		return Color3(red,green,blue)

def write_color (color) :
	if color is None :
		return "none"
	else :
		return "#%.2x%.2x%.2x" % (color.red,color.green,color.blue)

def read_float (val_str) :
	if val_str == "none" :
		return None
	else :
		res = float_re.match(val_str)
		return float(res.groups()[0])

def write_float (val) :
	return "%f" % val

class SVGElement (XMLElement) :
	"""
	base class for all SVG element
	store attribute of geometry and style
	"""
	
	type = "base"
	
	def __init__ (self, nodeid=None, parent=None, nodename="svg") :
		XMLElement.__init__(self,parent,SVG_ELEMENT_TYPE,nodename,nodeid)
		
		#graphic style
		self._style = {}
		
		#transformation
		self._transform = Matrix4()#transformation matrix expressed
		                           #in parent frame
		                           #pos_Rparent = transform * pos_Rlocal
		
		#filename for abs path
		self._svgfilename = None
	
	##############################################
	#
	#		access to style elements
	#
	##############################################
	def get_style (self, key) :
		"""Return style associated with this key.
		"""
		return self._style[key]
	
	def set_style (self, key, str_val) :
		"""Set the style associated with this key.
		"""
		self._style[key] = str_val
	
	def displayed (self) :
		"""Tells wether this element is visible or not.
		"""
		if "display" in self._style :
			return self._style["display"] != "none"
		else :
			return False
	
	def set_display (self, display) :
		"""Set the visibility of this element.
		"""
		if display :
			self._style["display"] = "true"
		else :
			self._style["display"] = "none"
	
	def fill (self) :
		"""Return color used to fill the element.
		"""
		if "fill" in self._style :
			return read_color(self._style["fill"])
		else :
			return None
	
	def set_fill (self, color) :
		"""Set the color used to fill the element.
		"""
		self._style["fill"] = write_color(color)
	
	def stroke (self) :
		"""Return color used to paint border of the element.
		"""
		if "stroke" in self._style :
			return read_color(self._style["stroke"])
		else :
			return None
	
	def set_stroke (self, color) :
		"""Set the color used to paint the border.
		"""
		self._style["stroke"] = write_color(color)
	
	def stroke_width (self) :
		"""Return size of the border.
		"""
		if "stroke-width" in self._style :
			width = read_float (self._style["stroke-width"])
			if width is None :
				return 0.
			else :
				return width
		else :
			return 0.
	
	def set_stroke_width (self, width) :
		"""Set the size of the border.
		"""
		self._style["stroke-width"] = write_float(width)
	##############################################
	#
	#		change of referential
	#
	##############################################
	def global_transformation (self, matrix=Matrix4() ) :
		return self._transform * matrix
	
	def global_pos (self, pos=Vector3() ) :
		return self._transform * pos
	
	def global_vec (self, vec=Vector3() ) :
		return Matrix3(self._transform) * vec
	
	def global_scale (self, scale=(1,1,1) ) :
		return tuple(scale[i] * self._transform[i,i] for i in xrange(3))
	
	def local_pos (self, pos=Vector3() ) :
		return self._transform.inverse() * pos
	
	def local_vec (self, vec=Vector3() ) :
		return Matrix3(self._transform.inverse() ) * vec
	
	def local_scale (self, scale=(1,1,1)) :
		return tuple(scale[i] / self._transform [i,i] for i in xrange(3) )
	
	def abs_pos (self, pos=Vector3() ) :
		ppos = self.global_pos(pos)
		if self.parent() is None :
			return ppos
		else :
			return self.parent().abs_pos(ppos)
	
	def abs_scaling (self, size=Vector3() ) :
		gsca = self.global_scale(size)
		if self.parent() is None :
			return gsca
		else :
			return self.parent().abs_scaling(gsca)
	##############################################
	#
	#		modify transformation
	#
	##############################################
	def set_transformation (self, matrix) :
		self._transform = matrix
	
	def transform (self, matrix) :
		self._transform = matrix * self._transform
	
	def translate (self, vec) :
		self._transform = Matrix4.translation(vec) * self._transform
	
	def rotate (self, angle) :
		self._transform = Matrix4(eulerRotationZYX( (angle,0,0) ) ) * self._transform
	
	def scale (self, scale) :
		self._transform = Matrix4(scaling(scale) ) * self._transform
	##############################################
	#
	#		SVG frame
	#
	##############################################
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
		m = matrix
		return Matrix4( (m[0,0],-m[0,1],0,m[0,3],
		                 -m[1,0],m[1,1],0,-m[1,3]) )
	
	def svg_matrix (self, matrix) :
		m = matrix
		return Matrix4( (m[0,0],-m[0,1],0,m[0,3],
		                 -m[1,0],m[1,1],0,-m[1,3]) )
	
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
	
	def load_style (self) :
		style = {}
		for style_elm in self.get_default("style","").split(";") :
			if ":" in style_elm :
				key,val = style_elm.split(":")
				style[key] = val
		return style
	
	def load_transformation (self) :
		#transformation
		if self.has_attribute("transform") :
			tr = self.attribute("transform")
			if "matrix" in tr :
				x11,x21,x12,x22,x13,x23 = (float(val) for val in matrix_re.match(tr).groups() )
				m = Matrix4( (x11,x12,0,x13,
				              x21,x22,0,x23) )
				self.transform(self.real_transformation(m) )
			elif "translate" in tr :
				xtr,ytr = translate_re.match(tr).groups()
				x = float(xtr)
				if ytr is None :
					y = x
				else :
					y = float(ytr)
				x,y = self.real_vec(x,y)
				self.translate( (x,y,0) )
			elif "scale" in tr :
				xtr,ytr = scale_re.match(tr).groups()
				x = float(xtr)
				if ytr is None :
					y = x
				else :
					y = float(ytr)
				self.scale( (x,y,0) )
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
		self._style.update(self.load_style() )
		self.load_transformation()
	
	def save_style (self) :
		style = self.load_style()
		style.update(self._style)
		self.set_attribute("style",";".join(["%s:%s" % it for it in style.iteritems()]) )
	
	def save_transformation (self) :
		tr = self.svg_transformation(self._transform)
		transform = "matrix(%f %f %f %f %f %f)" % (tr[0,0],tr[1,0],tr[0,1],tr[1,1],tr[0,3],tr[1,3])
		self.set_attribute("transform",transform)
		
	def save (self) :
		XMLElement.save(self)
		self.save_style()
		self.save_transformation()
	##############################################
	#
	#		PGL interface #TODO deprecated
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

