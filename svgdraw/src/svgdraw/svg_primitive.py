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
	"""Abstract class for SVGElements
	having a center
	"""
	
	def radius (self) :
		"""Retrieve the radial
		extension of this element.
		
		:Returns Type: float
		"""
		raise NotImplementedError()
	
	def center (self) :
		"""Retrieve the position of
		the center of this element.
		
		:Returns Type: float,float
		"""
		raise NotImplementedError()

class SVGBox (SVGCenteredElement) :
	"""A square or a box
	"""
	
	def __init__ (self, x, y, width, height, id=None) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x coordinate of the
		    top left corner of the box (in svg
		    coordinates)
		 - `y` (float) - y coordinate of the
		    top left corner of the box (in svg
		    coordinates)
		 - `width` (float) - actual width
		   of the box
		 - `height` (float) - actual height
		   of the box
		 - `id` (str) - unique id for this element
		"""
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
		"""Retrieve the radial
		extension of this element.
		
		:Returns Type: float
		"""
		return (self._width / 2.,
		        self._height / 2.)
	
	def center (self) :
		"""Retrieve the position of
		the center of this element.
		
		:Returns Type: float,float
		"""
		return (self._x + self._width / 2.,
		        self._y + self._height / 2.)
	
	def pos (self) :
		"""Retrieve coordinates of
		the top left corner of the box
		in svg coordinates.
		
		:Returns Type: float,float
		"""
		return (self._x,self._y)
	
	def size (self) :
		"""Retrieve spatial extension
		of the box.
		
		:Returns Type: float,float
		"""
		return (self._width,self._height)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		SVGCenteredElement.load(self)
		self._width = read_float(self.get_default("width","0") )
		self._height = read_float(self.get_default("height","0") )
		self._x = read_float(self.get_default("x","0") )
		self._y = read_float(self.get_default("y","0") )
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("width","%f" % self._width )
		self.set_attribute("height","%f" % self._height )
		self.set_attribute("x","%f" % self._x )
		self.set_attribute("y","%f" % self._y )
		SVGCenteredElement.save(self)

class SVGSphere (SVGCenteredElement) :
	"""Both circle and ellipse
	"""
	
	def __init__ (self, cx, cy, rx, ry, id=None) :
		"""Constructor
		
		:Parameters:
		 - `cx` (float) - x coordinate of the
		    center (in svg coordinates)
		 - `cy` (float) - y coordinate of the
		    center (in svg coordinates)
		 - `rx` (float) - radius along Ox
		 - `ry` (float) - radius along Oy
		 - `id` (str) - unique id for this element
		"""
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
		"""Retrieve the radial
		extension of this element.
		
		:Returns Type: float
		"""
		return (self._rx,self._ry)
	
	def center (self) :
		"""Retrieve the position of
		the center of this element.
		
		:Returns Type: float,float
		"""
		return (self._cx,self._cy)
	
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
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
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("rx","%f" % self._rx)
		self.set_attribute("ry","%f" % self._ry)
		self.set_attribute("cx","%f" % self._cx)
		self.set_attribute("cy","%f" % self._cy)
		SVGCenteredElement.save(self)

class SVGImage (SVGBox) :
	"""An image stored in an external file
	and displayed in a box.
	"""
	
	def __init__ (self, x, y, width, height, filename, id=None) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x coordinate of the
		    top left corner of the image
		    (in svg coordinates)
		 - `y` (float) - y coordinate of the
		    top left corner of the image
		    (in svg coordinates)
		 - `width` (float) - actual width
		   of the image
		 - `height` (float) - actual height
		   of the image
		 - `id` (str) - unique id for this element
		"""
		SVGBox.__init__(self,x,y,width,height,id)
		self.set_nodename("svg:image")
		self._filename = filename
	
	##############################################
	#
	#		attributes
	#
	##############################################
	def filename (self) :
		"""Retrieve filename of image data
		
		:Returns Type: str
		"""
		return self._filename
	
	def set_filename (self, filename) :
		"""Set filename of image data
		
		:Parameters:
		 - `filename` (str)
		"""
		self._filename = filename
	
	def absfilename (self) :
		"""Retrieve absolute filename
		of image data.
		
		:Returns Type: str
		"""
		return self.abs_path(self.filename() )
	
	def load_image (self) :
		"""Try to load the image to find
		both width and height.
		
		.. warning:: This method use module `PIL`
		"""
		import Image
		try :
			im = Image.open(self.absfilename() )
			self._width,self._height = im.size
		except IOError :
			raise UserWarning("Image filename do not exists: %s" % self.absfilename() )
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
		SVGBox.load(self)
		self.set_filename(str(self.get_default("xlink:href","") ) )
	
	def save (self) :
		"""Save SVG attributes as XML attributes
		"""
		self.set_attribute("xlink:href",self.filename() )
		SVGBox.save(self)

