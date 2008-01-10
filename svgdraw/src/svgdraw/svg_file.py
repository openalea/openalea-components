from xml.dom.minidom import parse,Document
from svg_scene import SVGScene

class SVGFileReader (object) :
	"""
	base class to read an svg file
	"""
	def __init__ (self, filename) :
		self._filename=filename
	
	def close (self) :
		pass
	
	def read (self) :
		doc=parse(self._filename)
		root=[node for node in doc.childNodes if node.nodeName=="svg"][0]
		sc=SVGScene()
		sc._svgfilename=self._filename
		sc.load(root)
		return sc

class SVGFileWriter (object) :
	"""
	base class to write an svg file
	"""
	def __init__ (self, filename) :
		self._filename=filename
		doc=Document()
		doc.appendChild(doc.createComment("created from python svgdraw module"))
		root=doc.createElement("svg")
		#TODO ajouter les xmnls
		root.setAttribute("xmlns","http://www.w3.org/2000/svg")
		root.setAttribute("xmlns:dc","http://purl.org/dc/elements/1.1/")
		root.setAttribute("xmlns:cc","http://web.resource.org/cc/")
		root.setAttribute("xmlns:rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		root.setAttribute("xmlns:svg","http://www.w3.org/2000/svg")
		root.setAttribute("xmlns:xlink","http://www.w3.org/1999/xlink")
		root.setAttribute("xmlns:inkscape","http://www.inkscape.org/namespaces/inkscape")
		root.setAttribute("xmlns:sodipodi","http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
		doc.appendChild(root)
		self._doc=doc
		self._root=root
	
	def flush (self) :
		f=open(self._filename,'w')
		f.write(self._doc.toprettyxml())
		f.close()
	
	def close (self) :
		self.flush()
	
	def write (self, svgscene) :
		svgscene.save(self._root)

def open_svg (filename, mode='r') :
	if mode=='r' :
		return SVGFileReader(filename)
	elif mode=='w' :
		return SVGFileWriter(filename)
	else :
		raise UserWarning ("mode %s not recognized" % str(mode))

