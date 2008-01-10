from openalea.plantgl.scenegraph import Scene,Shape,Material,FaceSet,Polyline,Group,Translated,Scaled,Transformed
from svg_group import SVGGroup

class SVGScene (SVGGroup) :
	"""
	maintain a list of svg elms
	"""
	def __init__ (self) :
		SVGGroup.__init__(self,None,"pglscene")
	
	#plantgl like
	def add (self, svgelm) :
		self.append(svgelm)
	##############################################
	#
	#		svg interface
	#
	##############################################
	def save (self, svgnode) :
		SVGGroup.save(self,svgnode)
		self.set_node_type(svgnode,"svg")
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
