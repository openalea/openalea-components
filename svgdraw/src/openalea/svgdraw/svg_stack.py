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
This module defines a svg element to store stacks of images
"""

#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO
#TODO

__license__= "Cecill-C"
__revision__=" $Id$ "

from os.path import join,normpath
from openalea.plantgl.math import Vector3,Matrix4,scaling
from svg_group import SVGGroup,SVGLayer
from svg_primitive import SVGImage
from xml_element import XMLElement,ELEMENT_TYPE

class SVGStackVariant (XMLElement) :
	def __init__ (self, parent=None) :
		XMLElement.__init__(self,parent,ELEMENT_TYPE,"variant")
		self._name=None
		self._scale=1.
		self._rep=None
	
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
	
	def load (self) :
		if self.has_attribute("rep") :
			self.set_rep(self.attribute("rep"))
		if self.has_attribute("name") :
			self.set_name(self.attribute("name"))
		if self.has_attribute("scale") :
			self._scale=float(self.attribute("scale"))
	
	def save (self) :
		if self._name is not None :
			self.set_attribute("name",self._name)
		self.set_attribute("scale","%f" % self._scale)
		if self._rep is not None :
			self.set_attribute("rep",self._rep)

class SVGStack (SVGLayer) :
	"""
	object used to manipulate a stack of images
	"""
	def __init__ (self, id=None, parent=None) :
		SVGLayer.__init__(self,id,parent)
		self.display=False
		self._variants=[]
		self._variant_used=None
		self._masked=[]
	
	def resolution (self) :
		return self._transform3D.getTransformationB()[0]
	
	def set_resolution (self, dx, dy, dz) :
		self._transform3D*=Matrix4(scaling((dx,dy,dz)))
	
	def add_image (self, image_name, width, height, masked=False, zreverse=False) :
		ind=len(self)
		gr=SVGLayer("gslice%.4d" % ind)
		self.append(gr)
		gr.set_size(width,height)
		if zreverse :
			gr.translate( (0,0,-ind) )
		else :
			gr.translate( (0,0,ind) )
		gr.display=False
		im=SVGImage("slice%.4d" % ind)
		gr.append(im)
		im.set_filename(image_name)
		im.scale2D( (width,height,1.) )
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
		var=SVGStackVariant()
		var.set_name(name)
		var.set_scale(scale)
		if rep is not None :
			var.set_rep(rep)
		self.add_child(var)
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
					while impth[0] in ("\\","/") :
						impth=impth[1:]
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
	def load (self) :
		SVGLayer.load(self)
		if self.nb_images()>0 :
			w,h,d=self.size()
			self.set_size(w,h,self.nb_images()-1)
		dx=float(self.get_default("dx",1.))
		dy=float(self.get_default("dy",1.))
		dz=float(self.get_default("dz",1.))
		self.set_resolution(dx,dy,dz)
		#variants
		for i in xrange(self.nb_children()) :
			if self.child(i).nodename()=="variant" :
				variant=SVGStackVariant()
				variant.from_node(self.child(i))
				self.set_child(i,variant)
				self._variants.append(variant)
				variant.load()
		#masked images
		self._masked=[]
		for im in self.images() :
			name=im.filename()
			if name[-1]=="X" :
				self._masked.append(True)
				im.set_filename(name[:-1])
			else :
				self._masked.append(False)
	
	def save (self) :
		var_mem=self._variant_used
		self.use_variant(None)
		#variants
		for var in self.variants() :
			var.save()
		#node
		inv=lambda x : 1./x if abs(x)>1e-6 else 0.
		dx,dy,dz=self.resolution()
		self._transform3D*=Matrix4(scaling(tuple(inv(r) for r in (dx,dy,dz))))
		#masked
		for i in xrange(len(self)) :
			im=self.image(i)
			if self._masked[i] :
				im.set_filename("%sX" % im.filename())
		SVGLayer.save(self)
		self.set_attribute("descr","stack")
		self.set_attribute("dx","%f" % dx)
		self.set_attribute("dy","%f" % dy)
		self.set_attribute("dz","%f" % dz)
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

