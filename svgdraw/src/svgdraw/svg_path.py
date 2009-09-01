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
This module defines a path svg element
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

import re
from openalea.plantgl.scenegraph import Polyline,Polyline2D,BezierCurve2D,NurbsCurve2D
from openalea.plantgl.math import Vector3,Vector2,norm
from svg_element import SVGElement

#to read svg paths
#I cannot for the moment repeat implicitly a command
#norm : http://www.w3.org/TR/SVG/paths.html
sep = r"\s*,?\s*"
coord = r"([-]?\d+[.]?\d*)"
point = coord + sep + coord

mM=sep+"([mM])"+sep+point
zZ=sep+"([zZ])"
#staight lines
lL=sep+"([lL])"+sep+point
hH=sep+"([hH])"+sep+coord
vV=sep+"([vV])"+sep+coord
#curves
cC=sep+"([cC])"+sep+point+sep+point+sep+point
sS=sep+"([sS])"+sep+point+sep+point
qQ=sep+"([qQ])"+sep+point+sep+point
tT=sep+"([tT])"+sep+point
aA=sep+"([aA])"+sep+point+sep+coord+sep+"([01])"+sep+"([01])"+sep+point

readpath = re.compile("|".join([mM,zZ,lL,hH,vV,cC,sS,qQ,tT,aA]))


class SVGPathCommand (object) :
	"""
	a abstraction of svg path commands
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, typ) :
		self._type=typ
		self._params = []
	
	def type (self) :
		return self._type
	
	def parameters (self) :
		return iter(self._params)
	
	def append (self, val) :
		self._params.append(val)

class SVGPath (SVGElement) :
	"""
	a abstraction of svg path
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, id=None, parent=None) :
		SVGElement.__init__(self,id,parent,"svg:path")
		self._commands = []
	
	def commands (self) :
		return iter(self._commands)
	
	def append (self, cmd_typ, cmd_args=[]) :
		cmd = SVGPathCommand(cmd_typ)
		for arg in cmd_args :
			cmd.append(arg)
		self._commands.append(cmd)
	
	def clear (self) :
		self._commands=[]
	
	def is_closed (self) :
		for command in self.commands() :
			if command.type().lower() == 'z' :
				return True
		return False
	
	def from_string (self, command_str) :
		self._commands = []
		ref_point = Vector2()
		for match in readpath.finditer(command_str) :
			cmd = [v for v in match.groups() if v is not None]
			typ = cmd[0]
			pth_cmd = SVGPathCommand(typ)
			if typ == 'M' :
				svgx,svgy = (float(val) for val in cmd[1:])
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(pos)
				ref_point = pos
			elif typ == 'm' :
				svgdx,svgdy = (float(val) for val in cmd[1:])
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(vec)
				ref_point += vec
			elif typ in ('Z','z') :
				pass
			elif typ == 'L' :
				svgx,svgy = (float(val) for val in cmd[1:])
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(pos)
				ref_point = pos
			elif typ == 'l' :
				svgdx,svgdy = (float(val) for val in cmd[1:])
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(vec)
				ref_point += vec
			elif typ in ('H','h') :
				svgdx, = (float(val) for val in cmd[1:])
				vec = Vector2(*self.real_vec(svgdx,0) )
				pth_cmd.append(vec)
				ref_point += vec
			elif typ in ('V','v') :
				svgdy, = (float(val) for val in cmd[1:])
				vec = Vector2(*self.real_vec(0,svgdy) )
				pth_cmd.append(vec)
				ref_point += vec
			elif typ == 'C' :
				svgx1,svgy1,svgx2,svgy2,svgx,svgy = (float(val) for val in cmd[1:])
				v1 = Vector2(*self.real_pos(svgx1,svgy1) )
				v2 = Vector2(*self.real_pos(svgx2,svgy2) )
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(v1)
				pth_cmd.append(v2)
				pth_cmd.append(pos)
				ref_point = pos
			elif typ=='c' :
				svgx1,svgy1,svgx2,svgy2,svgdx,svgdy = (float(val) for val in cmd[1:])
				v1 = Vector2(*self.real_vec(svgx1,svgy1) )
				v2 = Vector2(*self.real_vec(svgx2,svgy2) )
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(v1)
				pth_cmd.append(v2)
				pth_cmd.append(vec)
				ref_point += vec
			elif typ=='S' :
				svgx2,svgy2,svgx,svgy = (float(val) for val in cmd[1:])
				v2 = Vector2(*self.real_pos(svgx2,svgy2) )
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(v2)
				pth_cmd.append(pos)
				ref_point = pos
			elif typ=='s' :
				svgx2,svgy2,svgdx,svgdy = (float(val) for val in cmd[1:])
				v2 = Vector2(*self.real_vec(svgx2,svgy2) )
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(v2)
				pth_cmd.append(vec)
				ref_point += vec
			elif typ == 'Q' :
				svgx1,svgy1,svgx,svgy = (float(val) for val in cmd[1:])
				v1 = Vector2(*self.real_pos(svgx1,svgy1) )
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(v1)
				pth_cmd.append(pos)
				ref_point = pos
			elif typ=='q' :
				svgx1,svgy1,svgdx,svgdy =( float(val) for val in cmd[1:])
				v1 = Vector2(*self.real_vec(svgx1,svgy1) )
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(v1)
				pth_cmd.append(vec)
				ref_point += vec
			elif typ=='T' :
				svgx,svgy = (float(val) for val in cmd[1:])
				pos = Vector2(*self.real_pos(svgx,svgy) )
				pth_cmd.append(pos)
				ref_point = pos
			elif typ=='t' :
				svgdx,svgdy = (float(val) for val in cmd[1:])
				vec = Vector2(*self.real_vec(svgdx,svgdy) )
				pth_cmd.append(vec)
				ref_point += vec
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
			self._commands.append(pth_cmd)
	
	def to_string (self) :
		path_txt = ""
		for command in self.commands() :
			typ = command.type()
			if typ == 'M' :
				pos, = command.parameters()
				x,y = self.svg_pos(*pos)
				path_txt += "M %f %f" % (x,y)
			elif typ == 'm' :
				vec, = command.parameters()
				dx,dy = self.svg_vec(*vec)
				path_txt += "m %f %f" % (dx,dy)
			elif typ in ('Z','z') :
				path_txt += "%s" % typ
			elif typ == 'L' :
				pos, = command.parameters()
				x,y = self.svg_pos(*pos)
				path_txt += "L %f %f" % (x,y)
			elif typ == 'l' :
				vec, = command.parameters()
				dx,dy = self.svg_vec(*vec)
				path_txt += "l %f %f" % (dx,dy)
			elif typ in ('H','h') :
				vec, = command.parameters()
				dx,dy  =self.svg_vec(*vec)
				path_txt += "%s %f" % (typ,dx)
			elif typ in ('V','v') :
				vec, = command.parameters()
				dx,dy = self.svg_vec(*vec)
				path_txt += "%s %f" % (typ,dy)
			elif typ == 'C' :
				v1,v2,pos = command.parameters()
				x1,y1 = self.svg_pos(*v1)
				x2,y2 = self.svg_pos(*v2)
				x,y = self.svg_pos(*pos)
				path_txt += "C %f %f %f %f %f %f" % (x1,y1,x2,y2,x,y)
			elif typ == 'c' :
				v1,v2,vec = command.parameters()
				x1,y1 = self.svg_vec(*v1)
				x2,y2 = self.svg_vec(*v2)
				dx,dy = self.svg_vec(*vec)
				path_txt += "c %f %f %f %f %f %f" % (x1,y1,x2,y2,dx,dy)
			elif typ == 'S' :
				v2,pos = command.parameters()
				x2,y2 = self.svg_pos(*v2)
				x,y = self.svg_pos(*pos)
				path_txt += "S %f %f %f %f" % (x2,y2,x,y)
			elif typ == 's' :
				v2,vec = command.parameters()
				x2,y2 = self.svg_vec(*v2)
				dx,dy = self.svg_vec(*vec)
				path_txt += "s %f %f %f %f" % (x2,y2,dx,dy)
			elif typ == 'Q' :
				v1,pos = command.parameters()
				x1,y1 = self.svg_pos(*v1)
				x,y = self.svg_pos(*pos)
				path_txt += "Q %f %f %f %f" % (x1,y1,x,y)
			elif typ == 'q' :
				v1,vec = command.parameters()
				x1,y1 = self.svg_vec(*v1)
				dx,dy = self.svg_vec(*vec)
				path_txt += "q %f %f %f %f" % (x1,y1,dx,dy)
			elif typ == 'T' :
				pos, = command.parameters()
				x,y = self.svg_pos(*pos)
				path_txt += "T %f %f" % (x,y)
			elif typ == 't' :
				vec, = command.parameters()
				dx,dy = self.svg_vec(*vec)
				path_txt += "t %f %f" % (dx,dy)
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
		return path_txt
	##############################################
	#
	#		xml in out
	#
	##############################################
	def load (self) :
		SVGElement.load(self)
		path_txt = self.get_default("d","")
		self.from_string(path_txt)
	
	def save (self) :
		path_txt = self.to_string()
		self.set_attribute("d",path_txt)
		SVGElement.save(self)
	##############################################
	#
	#		pgl interface #TODO deprecated
	#
	##############################################
	def polyline_ctrl_points (self) :
		"""
		return a list of control points
		"""
		ref_point=Vector3()
		for command in self.commands() :
			typ=command.type()
			if typ=='M' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='m' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ in ('Z','z') :
				pass
			elif typ=='L' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='l' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ in ('H','h') :
				vec,=command.parameters()
				ref_point+=vec
				yield ref_point
			elif typ in ('V','v') :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='C' :
				v1,v2,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='c' :
				v1,v2,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='S' :
				v2,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='s' :
				v2,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='Q' :
				v1,pos=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='q' :
				v1,vec=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			elif typ=='T' :
				pos,=command.parameters()
				ref_point=pos
				yield ref_point
			elif typ=='t' :
				vec,=command.parameters()
				ref_point=ref_point+vec
				yield ref_point
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
	
	def nurbs_ctrl_points (self) :
		"""
		return a list of control points from this path
		"""
		ref_point=Vector2(0,0)
		for command in self.commands() :
			typ=command.type()
			if typ=='M' :
				ref_point,=command.parameters()
				yield ref_point
			elif typ=='m' :
				vec,=command.parameters()
				ref_point==vec
				yield ref_point
			elif typ in ('Z','z') :
				pass
			elif typ=='L' :
				ref_point,=command.parameters()
				yield ref_point
			elif typ=='l' :
				vec=command.parameters()
				ref_point+=vec
				yield ref_point
			elif typ=='C' :
				v1,v2,ref_point=command.parameters()
				yield v1
				yield v2
				yield ref_point
			elif typ=='c' :
				v1,v2,vec=command.parameters()
				yield ref_point+v1
				yield ref_point+v2
				ref_point+=vec
				yield ref_point
			else :
				raise UserWarning("command not available for nurbs %s" % typ)
	
	def polyline (self) :
		return Polyline2D(list(self.polyline_ctrl_points()))
	
	def nurbs (self, ctrl_pts=None, degree=3, uniform=False) :
		#control point
		if ctrl_pts is None :
			ctrl_pts=list(self.nurbs_ctrl_points())
		#knot vector
		nb_pts=len(ctrl_pts)
		nb_arc=(nb_pts-1)/degree
		nb_knots=degree+nb_pts
		p=0.
		param=[p]
		for i in xrange(nb_arc) :
			if uniform :
				p+=1
			else :
				p+=norm(ctrl_pts[degree*i]-ctrl_pts[degree*(i+1)])
			param.append(p)
		kv=[param[0]]
		for p in param :
			for j in xrange(degree) :
				kv.append(p)
		kv.append(param[-1])
		#curve
		return NurbsCurve2D([Vector3(v[0],v[1],1.) for v in ctrl_pts],kv,degree,60)
	
	def to_pgl2D (self,  pglshape) :
		geom=self.polyline()
		pglshape.geometry=geom
		return SVGElement.to_pgl2D(self,pglshape)
	
	def to_pgl3D (self, pglshape) :
		geom=self.polyline()
		pglshape.geometry=geom
		return SVGElement.to_pgl3D(self,pglshape)


class SVGConnector (SVGPath) :
	def __init__ (self, parent=None, svgid=None) :
		SVGPath.__init__(self,parent,svgid)
		self.set_attribute("inkscape:connector-type","polyline")
		self._source = None
		self._target = None
	
	def source (self) :
		return self._source
	
	def target (self) :
		return self._target
	
	def set_source (self, svg_elm_id) :
		self._source = svg_elm_id
	
	def set_target (self, svg_elm_id) :
		self._target = svg_elm_id
	
	def load (self) :
		SVGPath.load(self)
		if self.has_attribute("inkscape:connection-start") :
			self._source = str(self.attribute("inkscape:connection-start") )[1:]
		else :
			self._source = None
		if self.has_attribute("inkscape:connection-end") :
			self._target = str(self.attribute("inkscape:connection-end") )[1:]
		else :
			self._target = None
	
	def save (self) :
		SVGPath.save(self)
		if self._source is not None :
			self.set_attribute("inkscape:connection-start","#%s" % self._source)
		else :
			if self.has_attribute("inkscape:connection-start") :
				self.remove_attribute("inkscape:connection-start")
		if self._target is not None :
			self.set_attribute("inkscape:connection-end","#%s" % self._target)
		else :
			if self.has_attribute("inkscape:connection-end") :
				self.remove_attribute("inkscape:connection-end")

