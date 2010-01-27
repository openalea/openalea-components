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
This module defines read an write functions
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from xml.dom.minidom import parse,parseString,Document
from xml_element import XMLElement
from svg_scene import SVGScene

#######################################################
#
#		pure xml
#
#######################################################
class XMLReader (object) :
	"""Base class to read a serialized xml
	"""
	def __init__ (self) :
		pass
	
	def from_xml (self, data) :
		doc = parseString(data)
		elm = XMLElement()
		elm.load_xml(doc)
		return elm

class XMLFileReader (object) :
	"""Base class to read an xml file
	
	.. seealso: use :func:`open_xml` instead
	   of directly creating this object.
	"""
	def __init__ (self, filename) :
		self._filename = filename
	
	def close (self) :
		pass
	
	def read (self) :
		doc = parse(self._filename)
		elm = XMLElement()
		elm.load_xml(doc)
		return elm

class XMLWriter (object) :
	"""Base class to serialize an xml file
	"""
	def __init__ (self) :
		self._xml_doc = None
	
	def to_xml (self) :
		return self._xml_doc.toxml()

class XMLFileWriter (object) :
	"""Base class to write an xml file
	
	.. seealso: use :func:`open_xml` instead
	   of directly creating this object.
	"""
	def __init__ (self, filename) :
		self._filename = filename
		self._xml_doc = None
	
	def flush (self) :
		f = open(self._filename,'w')
		if self._xml_doc is not None :
			f.write(self._xml_doc.toxml() )
		f.close()
	
	def close (self) :
		self.flush()
	
	def write (self, doc_elm) :
		self._xml_doc = doc_elm.save_xml()

def open_xml (filename, mode='r') :
	"""Open an xml stream
	
	:Parameters:
	 - `filename` (str) - name of the stream
	 - `mode` ('r' or 'w') - open the stream
	   to read ('r') or write ('w') data
	
	:Returns Type: XMLStream
	"""
	if mode=='r' :
		return XMLFileReader(filename)
	elif mode=='w' :
		return XMLFileWriter(filename)
	else :
		raise UserWarning ("mode %s not recognized" % str(mode) )

#######################################################
#
#		svg
#
#######################################################
class SVGReader (XMLReader) :
	"""Base class to read svg data
	
	.. seealso: use :func:`from_xml` instead
	   of directly creating this object.
	"""
	def from_xml (self, data) :
		doc = XMLReader.from_xml(self,data)
		try :
			root = [node for node in doc.children() if node.nodename() == "svg:svg"][0]
		except IndexError :
			raise UserWarning("Old style svg file, you need to prefix node names with 'svg:'")
		sc = SVGScene()
		sc.from_node(root)
		sc.load()
		return sc

class SVGFileReader (XMLFileReader) :
	"""Base class to read an svg file
	
	.. seealso: use :func:`open_svg` instead
	   of directly creating this object.
	"""
	def read (self) :
		doc = XMLFileReader.read(self)
		try :
			root = [node for node in doc.children() if node.nodename() == "svg:svg"][0]
		except IndexError :
			raise UserWarning("Old style svg file, you need to prefix node names with 'svg:'")
		sc = SVGScene()
		sc._svgfilename = self._filename
		sc.from_node(root)
		sc.load()
		return sc

class SVGWriter (XMLWriter) :
	"""Base class to serialize an svg file
	
	.. seealso: use :func:`to_xml` instead
	   of directly creating this object.
	"""
	def __init__ (self, svgscene) :
		XMLWriter.__init__(self)
		doc = XMLElement(None,
		                 Document.DOCUMENT_NODE,
		                 "#document")
		comment = XMLElement(None,
		                     Document.COMMENT_NODE,
		                     "#comment")
		comment.set_attribute("data",
		                      "created from python svgdraw module")
		doc.add_child(comment)
		self._svg_doc = doc
		self._svg_scene = svgscene
		self._svg_doc.add_child(svgscene)
	
	def to_xml (self) :
		self._svg_scene.save()
		self._xml_doc = self._svg_doc.save_xml()
		return XMLWriter.to_xml(self)

class SVGFileWriter (XMLFileWriter) :
	"""Base class to write an svg file
	
	.. seealso: use :func:`open_svg` instead
	   of directly creating this object.
	"""
	def __init__ (self, filename) :
		XMLFileWriter.__init__(self,filename)
		doc = XMLElement(None,Document.DOCUMENT_NODE,"#document")
		comment = XMLElement(None,Document.COMMENT_NODE,"#comment")
		comment.set_attribute("data","created from python svgdraw module")
		doc.add_child(comment)
		self._svg_doc = doc
	
	def write (self, svgscene) :
		svgscene.save()
		self._svg_doc.add_child(svgscene)
		XMLFileWriter.write(self,self._svg_doc)

def open_svg (filename, mode='r') :
	"""Open a stream to read svg data
	
	:Parameters:
	 - `filename` (str) - name of the stream
	 - `mode` ('r' or 'w') - open the stream
	   to read ('r') or write ('w') data
	
	:Returns Type: SVGStream
	"""
	if mode=='r' :
		return SVGFileReader(filename)
	elif mode=='w' :
		return SVGFileWriter(filename)
	else :
		raise UserWarning ("mode %s not recognized" % str(mode))
def to_xml (svgscene) :
	"""Serialize a scene into a string
	
	.. seealso: :func:`from_xml`
	
	:Parameters:
	 - `svgscene` (:class:`SVGScene`)
	
	:Returns Type: str
	"""
	w = SVGWriter(svgscene)
	return w.to_xml()

def from_xml (data) :
	"""Deserialize a string into a scene
	
	.. seealso: :func:`to_xml`
	
	:Parameters:
	 - `data` (str) - xml representation
	   of a scene.
	
	:Returns Type: :class:`SVGScene`
	"""
	r = SVGReader()
	return r.from_xml(data)

