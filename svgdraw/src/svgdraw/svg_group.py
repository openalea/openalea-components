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
This module defines a group svg element
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.plantgl.scenegraph import Shape,Polyline,Color3
from openalea.plantgl.math import Vector3,Matrix3,Matrix4,scaling,norm
from svg_element import SVGElement,read_float,write_float

class SVGGroup (SVGElement) :
	"""
	container that group svg primitives
	"""
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:g")
		self._size = Vector3()
		self._elms = []
	
	def size (self,) :
		return self._size
	
	def set_size (self, width, height, dummy = 0) :
		self._size = Vector3(width,height,1.)
	
	def elements (self) :
		return iter(self._elms)
	
	def __iter__ (self) :
		return self.elements()
	
	def __len__ (self) :
		return len(self._elms)
	
	def __getitem__ (self, ind) :
		return self._elms[ind]
	
	def update_size (self, svggroupe) :
		if norm(svggroupe.size() ) < 1e-6 :
			svggroupe.set_size(*self.size() )
		for elm in svggroupe.elements() :
			if isinstance(elm,SVGGroup) :
				self.update_size(elm)
	
	def append (self, svgelm) :
		self.add_child(svgelm)
		self._elms.append(svgelm)
		if isinstance(svgelm,SVGGroup) :
			self.update_size(svgelm)
	
	def clear_elements (self) :
		for elm in self.elements() :
			self.remove_child(elm)
		self._elms=[]
	##################################################
	#
	#		elements access
	#
	##################################################
	def get_by_id (self, svgid) :
		"""
		return an element whose id is svgid
		recursively search in subgroups
		"""
		for elm in self.elements() :
			if elm.id() == svgid :
				return elm
		for elm in self.elements() :
			if isinstance(elm,SVGGroup) :
				finded = elm.get_by_id(svgid)
				if finded is not None :
					return finded
	
	def get_elm_transformation (self, elm) :
		tr = elm.global_transformation()
		dum = elm.parent()
		while (dum is not None) and (dum != self) :
			tr = dum.global_transformation(tr)
			dum = dum.parent()
		if dum is None :
			raise UserWarning("not a child of this node")
		else :
			return self.global_transformation(tr)
	##############################################
	#
	#		elements factory
	#
	##############################################
	def svg_element (self, xmlelm) :
		name = xmlelm.nodename()
		if name[:4] == "svg:" :
			name = name[4:]
		
		if name == "rect" :
			return SVGBox()
		elif name == "image" :
			return SVGImage()
		elif name == "text" :
			return SVGText()
		elif name == "circle" :
			return SVGSphere()
		elif name == "ellipse" :
			return SVGSphere()
		elif name == "path" :#either a path, a circle or a connector
			if xmlelm.has_attribute("sodipodi:type") :#may be a circle
				if xmlelm.attribute("sodipodi:type") == "arc" :#its a circle
					return SVGSphere()
				else :
					raise UserWarning("mode not recognized")
			else : #either a path or a connector
				if xmlelm.has_attribute("inkscape:connector-type") :#it's a connector
					return SVGConnector()
				else : #it's a simple path
					return SVGPath()
		elif name == "g" :#either a group or a layer
			if xmlelm.has_attribute("inkscape:groupmode") : #either a layer or a stack
				if xmlelm.has_attribute("descr") and xmlelm.attribute("descr") == "stack" :
					return SVGStack()
				else :
					return SVGLayer()
			else :
				return SVGGroup()
		else :
			return None
	##############################################
	#
	#		xml interface
	#
	##############################################
	def real_pos (self, svgx, svgy) :
		x,y = self.real_vec(svgx,svgy)
		w,h,d = self.size()
		return x,y+h
	
	def svg_pos (self, x, y) :
		w,h,d = self.size()
		return self.svg_vec(x,y-h)
	
	def real_transformation (self, matrix) :
		w,h,d = self.size()
		return Matrix4.translation( (0,h,0) ) * self.real_matrix(matrix) * Matrix4.translation( (0,-h,0) )
	
	def svg_transformation (self, matrix) :
		w,h,d = self.size()
		return Matrix4.translation( (0,h,0) ) * self.svg_matrix(matrix) * Matrix4.translation( (0,-h,0) )
	
	def load (self) :
		if self.parent() is None :
			w,h,d = 0,0,0
		else :
			w,h,d = self.parent().size()
		width = read_float(self.get_default("with",write_float(w) ) )
		height = read_float(self.get_default("height",write_float(h) ) )
		self.set_size(width,height)
		#element load after width and height to perform
		#correct real transformations
		SVGElement.load(self)
		#svg elements load
		for ind in xrange(self.nb_children() ) :
			svgelm = self.svg_element(self.child(ind) )
			if svgelm is not None :
				svgelm.from_node(self.child(ind) )
				self.set_child(ind,svgelm)
				self._elms.append(svgelm)
				svgelm.load()
	
	def save (self) :
		svgnode = SVGElement.save(self)
		w,h,d=self.size()
		self.set_attribute("width",str(w))
		self.set_attribute("height",str(h))
		#enregistrement des elements du groupe
		for svgelm in self.elements() :
			svgelm.save()
	##############################################
	#
	#		pgl interface #TODO deprecated
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
	def __init__ (self, id=None, parent=None) :
		SVGGroup.__init__(self,id,parent)
		if id is None :
			self._name = "lay"
		else :
			self._name = id
	
	def name (self) :
		return self._name
	
	def set_name (self, name) :
		self._name = name
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGGroup.load(self)
		self.set_name(self.get_default("inkscape:label","lay") )
	
	def save (self) :
		self.set_attribute("inkscape:label",self.name() )
		self.set_attribute("inkscape:groupmode","layer")
		SVGGroup.save(self)

from xml_element import XMLElement
from svg_primitive import SVGBox,SVGSphere,SVGImage
from svg_path import SVGPath,SVGConnector
from svg_stack import SVGStack
from svg_text import SVGText

