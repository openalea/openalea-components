from xml.dom.minidom import parse,Document
from xml_element import XMLElement
from svg_scene import SVGScene

class XMLFileReader (object) :
	"""
	base class to read an xml file
	"""
	def __init__ (self, filename) :
		self._filename=filename
	
	def close (self) :
		pass
	
	def read (self) :
		doc=parse(self._filename)
		elm=XMLElement()
		elm.load_xml(doc)
		return elm

class XMLFileWriter (object) :
	"""
	base class to write an xml file
	"""
	def __init__ (self, filename) :
		self._filename=filename
		self._xml_doc=None
	
	def flush (self) :
		f=open(self._filename,'w')
		if self._xml_doc is not None :
			f.write(self._xml_doc.toxml())
		f.close()
	
	def close (self) :
		self.flush()
	
	def write (self, doc_elm) :
		self._xml_doc=doc_elm.save_xml()

def open_xml (filename, mode='r') :
	if mode=='r' :
		return XMLFileReader(filename)
	elif mode=='w' :
		return XMLFileWriter(filename)
	else :
		raise UserWarning ("mode %s not recognized" % str(mode))

class SVGFileReader (XMLFileReader) :
	"""
	base class to read an svg file
	"""
	def read (self) :
		doc=XMLFileReader.read(self)
		root=[node for node in doc.children() if node.nodename()=="svg:svg"][0]
		sc=SVGScene()
		sc._svgfilename=self._filename
		sc.from_node(root)
		sc.load()
		return sc

class SVGFileWriter (XMLFileWriter) :
	"""
	base class to write an svg file
	"""
	def __init__ (self, filename) :
		XMLFileWriter.__init__(self,filename)
		doc=XMLElement(None,Document.DOCUMENT_NODE,"#document")
		comment=XMLElement(None,Document.COMMENT_NODE,"#comment")
		comment.set_attribute("data","created from python svgdraw module")
		doc.add_child(comment)
		self._svg_doc=doc
	
	def write (self, svgscene) :
		svgscene.save()
		self._svg_doc.add_child(svgscene)
		XMLFileWriter.write(self,self._svg_doc)

def open_svg (filename, mode='r') :
	if mode=='r' :
		return SVGFileReader(filename)
	elif mode=='w' :
		return SVGFileWriter(filename)
	else :
		raise UserWarning ("mode %s not recognized" % str(mode))

