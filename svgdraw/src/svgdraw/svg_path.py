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
from svg_element import SVGElement,read_float

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
	"""An abstraction of svg path
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, id=None) :
		SVGElement.__init__(self,id,None,"svg:path")
		self._commands = []
	
	##################################################
	#
	#		command list
	#
	##################################################
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
	
	##################################################
	#
	#		txt interface
	#
	##################################################
	def from_string (self, command_str) :
		self._commands = []
		ref_x = 0
		ref_y = 0
		for match in readpath.finditer(command_str) :
			cmd = [v for v in match.groups() if v is not None]
			typ = cmd[0]
			pth_cmd = SVGPathCommand(typ)
			if typ == 'M' :
				x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ == 'm' :
				dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (dx,dy) )
				ref_x += dx
				ref_y += dy
			elif typ in ('Z','z') :
				pass
			elif typ == 'L' :
				x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ == 'l' :
				dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (dx,dy) )
				ref_x += dx
				ref_y += dy
			elif typ in ('H','h') :
				dx, = (float(val) for val in cmd[1:])
				pth_cmd.append( (dx,0) )
				ref_x += dx
			elif typ in ('V','v') :
				dy, = (float(val) for val in cmd[1:])
				pth_cmd.append( (0,dy) )
				ref_y += dy
			elif typ == 'C' :
				x1,y1,x2,y2,x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x1,y1) )
				pth_cmd.append( (x2,y2) )
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ=='c' :
				x1,y1,x2,y2,dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (x1,y1) )
				pth_cmd.append( (x2,y2) )
				pth_cmd.append( (dx,dy) )
				ref_x += dx
				ref_y += dy
			elif typ=='S' :
				x2,y2,x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x2,y2) )
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ=='s' :
				x2,y2,dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (x2,y2) )
				pth_cmd.append( (x,y) )
				ref_x += dx
				ref_y += dy
			elif typ == 'Q' :
				x1,y1,x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x1,y1) )
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ=='q' :
				x1,y1,dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (x1,y1) )
				pth_cmd.append( (dx,dy) )
				ref_x += dx
				ref_y += dy
			elif typ=='T' :
				x,y = (float(val) for val in cmd[1:])
				pth_cmd.append( (x,y) )
				ref_x = x
				ref_y = y
			elif typ=='t' :
				dx,dy = (float(val) for val in cmd[1:])
				pth_cmd.append( (dx,dy) )
				ref_x += dx
				ref_y += dy
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
			self._commands.append(pth_cmd)
	
	def to_string (self) :
		path_txt = ""
		for command in self.commands() :
			typ = command.type()
			if typ == 'M' :
				pos, = command.parameters()
				path_txt += "M %f %f" % pos
			elif typ == 'm' :
				vec, = command.parameters()
				path_txt += "m %f %f" % vec
			elif typ in ('Z','z') :
				path_txt += "%s" % typ
			elif typ == 'L' :
				pos, = command.parameters()
				path_txt += "L %f %f" % pos
			elif typ == 'l' :
				vec, = command.parameters()
				path_txt += "l %f %f" % vec
			elif typ in ('H','h') :
				vec, = command.parameters()
				path_txt += "%s %f" % ( (typ,) + vec)
			elif typ in ('V','v') :
				vec, = command.parameters()
				path_txt += "%s %f" % ( (typ,) + vec)
			elif typ == 'C' :
				v1,v2,pos = command.parameters()
				path_txt += "C %f %f %f %f %f %f" % (v1 + v2 + pos)
			elif typ == 'c' :
				v1,v2,vec = command.parameters()
				path_txt += "c %f %f %f %f %f %f" % (v1 + v2 + vec)
			elif typ == 'S' :
				v2,pos = command.parameters()
				path_txt += "S %f %f %f %f" % (v2 + pos)
			elif typ == 's' :
				v2,vec = command.parameters()
				path_txt += "s %f %f %f %f" % (v2 + vec)
			elif typ == 'Q' :
				v1,pos = command.parameters()
				path_txt += "Q %f %f %f %f" % (v1 + pos)
			elif typ == 'q' :
				v1,vec = command.parameters()
				path_txt += "q %f %f %f %f" % (v1 + vec)
			elif typ == 'T' :
				pos, = command.parameters()
				path_txt += "T %f %f" % pos
			elif typ == 't' :
				vec, = command.parameters()
				path_txt += "t %f %f" % vec
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
		if self.nodename() == "line" :
			x1 = read_float(self.get_default("x1","0") )
			y1 = read_float(self.get_default("y1","0") )
			x2 = read_float(self.get_default("x2","0") )
			y2 = read_float(self.get_default("y2","0") )
			self.append('M',[(x1,y1)])
			self.append('L',[(x2,y2)])
		elif self.nodename() in ("polyline","polygone") :
			raise NotImplementedError("polyline to path still need to be done :)")
		else :
			path_txt = self.get_default("d","")
			self.from_string(path_txt)
	
	def save (self) :
		path_txt = self.to_string()
		self.set_attribute("d",path_txt)
		SVGElement.save(self)
	##############################################
	#
	#		geometry interface
	#
	##############################################
	def polyline_ctrl_points (self) :
		"""Return a list of control points
		to view this path as a polyline
		"""
		ref_x = 0
		ref_y = 0
		for command in self.commands() :
			typ = command.type()
			if typ == 'M' :
				pos, = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 'm' :
				vec, = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ in ('Z','z') :
				pass
			elif typ == 'L' :
				pos, = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 'l' :
				vec, = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ in ('H','h') :
				vec, = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ in ('V','v') :
				vec, = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ == 'C' :
				v1,v2,pos = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 'c' :
				v1,v2,vec = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ == 'S' :
				v2,pos = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 's' :
				v2,vec = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ == 'Q' :
				v1,pos = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 'q' :
				v1,vec = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			elif typ == 'T' :
				pos, = command.parameters()
				ref_x,ref_y = pos
				yield (ref_x,ref_y)
			elif typ == 't' :
				vec, = command.parameters()
				ref_x += vec[0]
				ref_y += vec[1]
				yield (ref_x,ref_y)
			else :
				raise NotImplementedError("path command type not recognized : % s" % typ)
	
	def nurbs_ctrl_points (self) :#TODO
		"""Return a list of control points from this path
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

class SVGConnector (SVGPath) :
	def __init__ (self, source, target, id=None) :
		SVGPath.__init__(self,id)
		self.set_attribute("inkscape:connector-type","polyline")
		self._source = source
		self._target = target
	
	##############################################
	#
	#		attributes
	#
	##############################################
	def source (self) :
		return self._source
	
	def target (self) :
		return self._target
	
	def set_source (self, svg_elm_id) :
		self._source = svg_elm_id
	
	def set_target (self, svg_elm_id) :
		self._target = svg_elm_id
	
	##############################################
	#
	#		path modification
	#
	##############################################
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

