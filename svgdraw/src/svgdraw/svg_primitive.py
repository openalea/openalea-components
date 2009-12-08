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

from svg_element import SVGElement,read_float,write_float
from xml_element import XMLElement

class SVGCenteredElement (SVGElement) :
	def radius (self) :
		raise NotImplementedError()
	
	def center (self) :
		raise NotImplementedError()

class SVGBox (SVGCenteredElement) :
	"""
	a square or a box
	"""
	def __init__ (self, x, y, width, height, id=None) :
		SVGCenteredElement.__init__(self,id,None,"svg:rect")
		self._x = x
		self._y = y
		self._width = width
		self._height = height
	##############################################
	#
	#		attributes
	#
	##############################################
	def radius (self) :
		return (self._width / 2.,
		        self._height / 2.)
	
	def center (self) :
		return (self._x + self._width / 2.,
		        self._y + self._height / 2.)
	
	def pos (self) :
		return (self._x,self._y)
	
	def size (self) :
		return (self._width,self._height)
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGCenteredElement.load(self)
		self._width = read_float(self.get_default("width","0") )
		self._height = read_float(self.get_default("height","0") )
		self._x = read_float(self.get_default("x","0") )
		self._y = read_float(self.get_default("y","0") )
	
	def save (self) :
		self.set_attribute("width","%f" % self._width )
		self.set_attribute("height","%f" % self._height )
		self.set_attribute("x","%f" % self._x )
		self.set_attribute("y","%f" % self._y )
		SVGCenteredElement.save(self)

class SVGSphere (SVGCenteredElement) :
	"""Both circle or ellipse
	"""
	def __init__ (self, cx, cy, rx, ry, id=None) :
		SVGCenteredElement.__init__(self,id,None,"svg:ellipse")
		self._cx = cx
		self._cy = cy
		self._rx = rx
		self._ry = ry
	
	##############################################
	#
	#		attributes
	#
	##############################################
	def radius (self) :
		return (self._rx,self._ry)
	
	def center (self) :
		return (self._cx,self._cy)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGCenteredElement.load(self)
		self._rx = read_float(self.get_default("r",
		                      self.get_default("rx",
		                      self.get_default("sodipodi:rx","0") ) ) )
		self._ry = read_float(self.get_default("r",
		                      self.get_default("ry",
		                      self.get_default("sodipodi:ry","0") ) ) )
		self._cx = read_float(self.get_default("cx",
		                      self.get_default("sodipodi:cx","0") ) )
		self._cy = read_float(self.get_default("cy",
		                      self.get_default("sodipodi:cy","0") ) )
	
	def save (self) :
		self.set_attribute("rx","%f" % self._rx)
		self.set_attribute("ry","%f" % self._ry)
		self.set_attribute("cx","%f" % self._cx)
		self.set_attribute("cy","%f" % self._cy)
		SVGCenteredElement.save(self)

class SVGImage (SVGBox) :
	"""An image stored in an external file.
	"""
	def __init__ (self, x, y, width, height, filename, id=None) :
		SVGBox.__init__(self,x,y,width,height,id)
		self.set_nodename("svg:image")
		self._filename = filename
	
	##############################################
	#
	#		attributes
	#
	##############################################
	def filename (self) :
		return self._filename
	
	def set_filename (self, filename) :
		self._filename = filename
	
	def absfilename (self) :
		return self.abs_path(self.filename() )
	
	def load_image (self) :
		"""Try to load the image to find
		both width and height.
		"""
		import Image
		try :
			im = Image.open(self.absfilename() )
			self._width,self._height = im.size
		except IOError :
			raise UserWarning("image filename do not exists: %s" % self.absfilename() )
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGBox.load(self)
		self.set_filename(str(self.get_default("xlink:href","") ) )
	
	def save (self) :
		self.set_attribute("xlink:href",self.filename() )
		SVGBox.save(self)

