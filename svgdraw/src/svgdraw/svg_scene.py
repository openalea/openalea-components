from openalea.plantgl.scenegraph import Scene,Shape,Material,FaceSet,Polyline,Group,Translated,Scaled,Transformed
from svg_group import SVGGroup,SVGLayer

class SVGScene (SVGGroup) :
	"""
	maintain a list of svg elms
	"""
	def __init__ (self) :
		SVGGroup.__init__(self,"pglscene",None)
		self.set_nodename("svg:svg")
		self.set_attribute("xmlns:dc","http://purl.org/dc/elements/1.1/")
		self.set_attribute("xmlns:cc","http://web.resource.org/cc/")
		self.set_attribute("xmlns:rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		self.set_attribute("xmlns:svg","http://www.w3.org/2000/svg")
		self.set_attribute("xmlns:xlink","http://www.w3.org/1999/xlink")
		self.set_attribute("xmlns:inkscape","http://www.inkscape.org/namespaces/inkscape")
		self.set_attribute("xmlns:sodipodi","http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
	
	def get_layer (self, layer_name) :
		"""
		walk among childrens to find the first layer with the given name
		"""
		for elm in self.elements() :
			if isinstance(elm,SVGLayer) :
				if elm.attribute("inkscape:label")==layer_name :
					return elm
	##############################################
	#
	#		pgl interface
	#
	##############################################
	def _hack_pgl_group (self, group_shape, scene) :
		try :
			for shp in group_shape._shape_list :
				scene.add(shp)
				self._hack_pgl_group(shp,scene)
		except AttributeError :
			pass
	
	def to_pgl2D (self) :
		scene=Scene()
		border=Shape()
		SVGGroup.to_pgl2D(self,border)
		scene.add(border)
		self._hack_pgl_group(border,scene)
		return scene
	
	def to_pgl3D (self) :
		scene=Scene()
		border=Shape()
		SVGGroup.to_pgl3D(self,border)
		scene.add(border)
		self._hack_pgl_group(border,scene)
		return scene
