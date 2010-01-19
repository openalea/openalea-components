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
#norm : http://www.w3.org/TR/SVG/paths.html
sep = r"\s*,?\s*"
coord = r"([-]?\d+[.]?\d*)"
point = coord + sep + coord
remaining = r"(.*)$"

mM_data = re.compile(sep + point + remaining)

#staight lines
lL_data = re.compile(sep + point + remaining)
hH_data = re.compile(sep + coord + remaining)
vV_data = re.compile(sep + coord + remaining)

#curves
cC_data = re.compile(sep + point
                   + sep + point
                   + sep + point
                   + remaining)

sS=sep+"([sS])"+sep+point+sep+point
qQ=sep+"([qQ])"+sep+point+sep+point
tT=sep+"([tT])"+sep+point
aA=sep+"([aA])"+sep+point+sep+coord+sep+"([01])"+sep+"([01])"+sep+point

cmd_typ = re.compile(sep + "([mMzZlLhHvVcC])" + remaining)

class SVGPathCommand (object) :
	"""
	a abstraction of svg path commands
	voir : http://wiki.svg.org/Path
	"""
	def __init__ (self, relative = False) :
		self._relative = relative
	
	def is_relative (self) :
		return self._relative
	
	def set_relative (self, relative) :
		self._relative = relative
	
	def copy (self) :
		"""Create a new copy of this command.
		
		Usefull for implicit declarations
		in SVG files.
		"""
		return SVGPathCommand(self._relative)
	
	def from_string (self, txt) :
		"""Fill the relevant parameters
		from the given string
		
		Return the string without the
		consumed elements
		"""
		return txt
	
	def to_string (self) :
		"""Construct a string representation
		of this command.
		"""
		return ""
	
	def polyline_ctrl_points (self, last_point = None) :
		"""List of ctrl points.
		
		The element of path represented
		by this command is seen as a polyline.
		"""
		return []
	
	def nurbs_ctrl_points (self, last_point = None) :
		"""List of ctrl points.
		
		The element of path represented
		by this command is seen as a nurbs.
		Default, return polyline_ctrl_points
		"""
		return self.polyline_ctrl_points(last_point)

class SVGPathMoveToCommand (SVGPathCommand) :
	"""A displacement of the current point.
	"""
	
	def __init__ (self, x, y, relative = False) :
		SVGPathCommand.__init__(self,relative)
		self._x = x
		self._y = y
	
	def copy (self) :
		return SVGPathMoveToCommand(self._x,self._y,self.is_relative() )
	
	def from_string (self, txt) :
		match = mM_data.match(txt)
		if match is None :
			raise UserWarning("unable to find MoveTo parameters in %s" % txt)
		x,y,ret = match.groups()
		self._x = float(x)
		self._y = float(y)
		return ret
	
	def to_string (self) :
		if self.is_relative() :
			txt = "m"
		else :
			txt = "M"
		txt += " %f" % self._x
		txt += " %f" % self._y
		
		return txt
	
	def polyline_ctrl_points (self, last_point = None) :
		if (last_point is None) or (not self.is_relative() ) :
			return [(self._x,self._y)]
		else :
			return [(last_point[0] + self._x,last_point[1] + self._y)]

class SVGPathCloseCommand (SVGPathCommand) :
	"""Close a path
	"""
	
	def __init__ (self) :
		SVGPathCommand.__init__(self)
	
	def copy (self) :
		return SVGPathCloseCommand()
	
	def to_string (self) :
		return "z"

class SVGPathLineToCommand (SVGPathCommand) :
	"""A straight line.
	"""
	
	def __init__ (self, x, y, relative = False) :
		SVGPathCommand.__init__(self,relative)
		self._x = x
		self._y = y
	
	def copy (self) :
		return SVGPathLineToCommand(self._x,self._y,self.is_relative() )
	
	def from_string (self, txt) :
		match = lL_data.match(txt)
		if match is None :
			raise UserWarning("unable to find LineTo parameters in %s" % txt)
		x,y,ret = match.groups()
		self._x = float(x)
		self._y = float(y)
		return ret
	
	def to_string (self) :
		if self.is_relative() :
			txt = "l"
		else :
			txt = "L"
		txt += " %f" % self._x
		txt += " %f" % self._y
		
		return txt
	
	def polyline_ctrl_points (self, last_point = None) :
		if (last_point is None) or (not self.is_relative() ) :
			return [(self._x,self._y)]
		else :
			return [(last_point[0] + self._x,last_point[1] + self._y)]

class SVGPathHorizontalCommand (SVGPathCommand) :
	"""A straight horizontal line.
	"""
	
	def __init__ (self, x, relative = False) :
		SVGPathCommand.__init__(self,relative)
		self._x = x
	
	def copy (self) :
		return SVGPathHorizontalCommand(self._x,self.is_relative() )
	
	def from_string (self, txt) :
		match = hH_data.match(txt)
		if match is None :
			raise UserWarning("unable to find HorizontalLineTo parameters in %s" % txt)
		x,ret = match.groups()
		self._x = float(x)
		return ret
	
	def to_string (self) :
		if self.is_relative() :
			txt = "h"
		else :
			txt = "H"
		txt += " %f" % self._x
		
		return txt
	
	def polyline_ctrl_points (self, last_point = None) :
		if self.is_relative() :
			if last_point is None :
				return  [(self._x,0)]
			else :
				return [(last_point[0] + self._x,last_point[1])]
		else :
			return [(self._x,last_point[1])]

class SVGPathVerticalCommand (SVGPathCommand) :
	"""A straight vertical line.
	"""
	
	def __init__ (self, y, relative = False) :
		SVGPathCommand.__init__(self,relative)
		self._y = y
	
	def copy (self) :
		return SVGPathVerticalCommand(self._y,self.is_relative() )
	
	def from_string (self, txt) :
		match = vV_data.match(txt)
		if match is None :
			raise UserWarning("unable to find VerticalLineTo parameters in %s" % txt)
		y,ret = match.groups()
		self._y = float(y)
		return ret
	
	def to_string (self) :
		if self.is_relative() :
			txt = "v"
		else :
			txt = "V"
		txt += " %f" % self._y
		
		return txt
	
	def polyline_ctrl_points (self, last_point = None) :
		if self.is_relative() :
			if last_point is None :
				return [(0,self._y)]
			else :
				return [(last_point[0],last_point[1] + self._y)]
		else :
			return [(last_point[0],self._y)]

class SVGPathCurveToCommand (SVGPathCommand) :
	"""A curved line (nurbs).
	"""
	
	def __init__ (self, pt1, pt2, pt3, relative = False) :
		SVGPathCommand.__init__(self,relative)
		self._pt1 = pt1
		self._pt2 = pt2
		self._pt3 = pt3
	
	def copy (self) :
		return SVGPathCurveToCommand(self._pt1,
		                             self._pt2,
		                             self._pt3,
		                             self.is_relative() )
	
	def from_string (self, txt) :
		match = cC_data.match(txt)
		if match is None :
			raise UserWarning("unable to find CurveTo parameters in %s" % txt)
		x1,y1,x2,y2,x3,y3,ret = match.groups()
		self._pt1 = (float(x1),float(y1) )
		self._pt2 = (float(x2),float(y2) )
		self._pt3 = (float(x3),float(y3) )
		return ret
	
	def to_string (self) :
		if self.is_relative() :
			txt = "c"
		else :
			txt = "C"
		for pt in (self._pt1,self._pt2,self._pt3) :
			txt += " %f %f" % pt
		
		return txt
	
	def polyline_ctrl_points (self, last_point = None) :
		if (last_point is None) or (not self.is_relative() ) :
			return [self._pt1,self._pt2,self._pt3]
		else :
			return [(last_point[0] + x,last_point[1] + y) \
			        for x,y in (self._pt1,self._pt2,self._pt3)]
	
	def nurbs_ctrl_points (self, last_point = None) :
		if (last_point is None) or (not self.is_relative() ) :
			return [self._pt1,self._pt2,self._pt3]
		else :
			return [(last_point[0] + x,last_point[1] + y) \
			        for x,y in (self._pt1,self._pt2,self._pt3)]


def cmd_factory (typ) :
	relative = typ.islower()
	typ = typ.lower()
	
	if typ == "m" :
		return SVGPathMoveToCommand(None,None,relative)
	elif typ == "z" :
		return SVGPathCloseCommand()
	elif typ == "l" :
		return SVGPathLineToCommand(None,None,relative)
	elif typ == "h" :
		return SVGPathHorizontalCommand(None,relative)
	elif typ == "v" :
		return SVGPathVerticalCommand(None,relative)
	elif typ == "c" :
		return SVGPathCurveToCommand(None,None,None,relative)
	else :
		raise NotImplementedError("path command type not recognized : % s" % typ)

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
	
	def clear (self) :
		self._commands = []
	
	def close (self) :
		"""Close the path.
		"""
		cmd = SVGPathCloseCommand()
		self._commands.append(cmd)
	
	def move_to (self, x, y, relative = False) :
		"""Move pen to a given location.
		"""
		cmd = SVGPathMoveToCommand(x,y,relative)
		self._commands.append(cmd)
	
	def line_to (self, x, y, relative = False) :
		"""Trace a straight line up to the
		given location.
		"""
		cmd = SVGPathLineToCommand(x,y,relative)
		self._commands.append(cmd)
	
	def curve_to (self, pt1, pt2, pt3, relative = False) :
		"""Trace a curved line between the
		given control points.
		"""
		cmd = SVGPathCurveToCommand(pt1,pt2,pt3,relative)
		self._commands.append(cmd)
	
	def is_closed (self) :
		for cmd in self.commands() :
			if isinstance(cmd,SVGPathCloseCommand) :
				return True
		return False
	
	##################################################
	#
	#		txt interface
	#
	##################################################
	def from_string (self, txt) :
		self.clear()
		last_cmd = None
		while len(txt) > 0 :
			#find command type
			match = cmd_typ.match(txt)
			if match is None :#use last command
				cmd = last_cmd.copy()
			else :
				typ,txt = (v for v in match.groups() if v is not None)
				cmd = cmd_factory(typ)
			
			#fill command with parameters
			txt = cmd.from_string(txt)
			self._commands.append(cmd)
			
			last_cmd = cmd
	
	def to_string (self) :
		txt = ""
		for cmd in self.commands() :
			txt += cmd.to_string()
		
		return txt
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
			self.move_to(x1,y1,False)
			self.line_to(x2,y2,False)
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
		last_point = (0,0)
		for cmd in self.commands() :
			pts = cmd.polyline_ctrl_points(last_point)
			for pt in pts :
				yield pt
			if len(pts) > 0 :
				last_point = pts[-1]
	
	def nurbs_ctrl_points (self) :#TODO
		"""Return a list of control points from this path
		"""
		last_point = (0,0)
		for cmd in self.commands() :
			pts = cmd.nurbs_ctrl_points(last_point)
			for pt in pts :
				yield pt
			if len(pts) > 0 :
				last_point = pts[-1]
	
	def nurbs (self, ctrl_pts=None, degree=3, uniform=False) :
		raise NotImplementedError
#		#control point
#		if ctrl_pts is None :
#			ctrl_pts=list(self.nurbs_ctrl_points())
#		#knot vector
#		nb_pts=len(ctrl_pts)
#		nb_arc=(nb_pts-1)/degree
#		nb_knots=degree+nb_pts
#		p=0.
#		param=[p]
#		for i in xrange(nb_arc) :
#			if uniform :
#				p+=1
#			else :
#				p+=norm(ctrl_pts[degree*i]-ctrl_pts[degree*(i+1)])
#			param.append(p)
#		kv=[param[0]]
#		for p in param :
#			for j in xrange(degree) :
#				kv.append(p)
#		kv.append(param[-1])
#		#curve
#		return NurbsCurve2D([Vector3(v[0],v[1],1.) for v in ctrl_pts],kv,degree,60)

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

