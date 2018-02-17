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
__revision__=" $Id$ "

import re
from svg_element import SVGElement,sep,digit,read_float

#to read svg paths
#norm : http://www.w3.org/TR/SVG/paths.html
point = digit + sep + digit
remaining = r"(.*)$"

mM_data = re.compile(sep + point + remaining)

#staight lines
lL_data = re.compile(sep + point + remaining)
hH_data = re.compile(sep + digit + remaining)
vV_data = re.compile(sep + digit + remaining)

#curves
cC_data = re.compile(sep + point
                   + sep + point
                   + sep + point
                   + remaining)

sS=sep+"([sS])"+sep+point+sep+point
qQ=sep+"([qQ])"+sep+point+sep+point
tT=sep+"([tT])"+sep+point
aA=sep+"([aA])"+sep+point+sep+digit+sep+"([01])"+sep+"([01])"+sep+point

cmd_typ = re.compile(sep + "([mMzZlLhHvVcC])" + remaining)

class _SVGPathCommand (object) :
	"""An abstraction of svg path commands
	
	.. seealso:: <http://wiki.svg.org/Path>
	"""
	def __init__ (self, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		self._relative = relative
	
	def is_relative (self) :
		"""Tells wether coordinates are relative
		
		:Returns Type: bool
		"""
		return self._relative
	
	def set_relative (self, relative) :
		"""Set coordinate relative to
		previous point or not.
		
		:Parameters:
		 - `relative` (bool)
		"""
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
		
		:Parameters:
		 - `txt` (str) - string representation
		   of path commands
		
		:Return: the string without the
		         consumed elements
		
		:Returns Type: str
		"""
		return txt
	
	def to_string (self) :
		"""Construct a string representation
		of this command.
		
		:Returns Type: str
		"""
		return ""
	
	def polyline_ctrl_points (self, last_point = None) :
		"""List of ctrl points
		
		The different points the path go through
		when the path is seen as a polyline.
		
		:Parameters:
		 - `last_point` (float,float) - if
		   not None, coordinates of the last
		   point in the path before this command
		
		:Returns Type: list of (float,float)
		"""
		return []
	
	def nurbs_ctrl_points (self, last_point = None) :
		"""List of ctrl points.
		
		The different points the path go through
		when the path is seen as a nurbs.
		
		.. seealso: :func:`polyline_ctrl_points`
		
		:Parameters:
		 - `last_point` (float,float) - if
		   not None, coordinates of the last
		   point in the path before this command
		
		:Returns Type: list of (float,float)
		"""
		return self.polyline_ctrl_points(last_point)

class _SVGPathMoveToCommand (_SVGPathCommand) :
	"""A displacement of the current point
	"""
	
	def __init__ (self, x, y, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x displacement if relative
		               or new x coordinate
		 - `y` (float) - y displacement if relative
		               or new x coordinate
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		_SVGPathCommand.__init__(self,relative)
		self._x = x
		self._y = y
	
	def copy (self) :
		return _SVGPathMoveToCommand(self._x,self._y,self.is_relative() )
	
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

class _SVGPathCloseCommand (_SVGPathCommand) :
	"""Close a path
	"""
	
	def __init__ (self) :
		"""Constructor
		"""
		_SVGPathCommand.__init__(self)
	
	def copy (self) :
		return _SVGPathCloseCommand()
	
	def to_string (self) :
		return "z"

class _SVGPathLineToCommand (_SVGPathCommand) :
	"""A straight line
	"""
	
	def __init__ (self, x, y, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x displacement if relative
		   or x coordinate of end point of the line
		 - `y` (float) - y displacement if relative
		   or x coordinate of end point of the line
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		_SVGPathCommand.__init__(self,relative)
		self._x = x
		self._y = y
	
	def copy (self) :
		return _SVGPathLineToCommand(self._x,self._y,self.is_relative() )
	
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

class _SVGPathHorizontalCommand (_SVGPathCommand) :
	"""A straight horizontal line
	"""
	
	def __init__ (self, x, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `x` (float) - x displacement if relative
		   or x coordinate of end point of the line
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		_SVGPathCommand.__init__(self,relative)
		self._x = x
	
	def copy (self) :
		return _SVGPathHorizontalCommand(self._x,self.is_relative() )
	
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

class _SVGPathVerticalCommand (_SVGPathCommand) :
	"""A straight vertical line
	"""
	
	def __init__ (self, y, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `y` (float) - y displacement if relative
		   or y coordinate of end point of the line
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		_SVGPathCommand.__init__(self,relative)
		self._y = y
	
	def copy (self) :
		return _SVGPathVerticalCommand(self._y,self.is_relative() )
	
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

class _SVGPathCurveToCommand (_SVGPathCommand) :
	"""A curved line (nurbs)
	"""
	
	def __init__ (self, pt1, pt2, pt3, relative = False) :
		"""Constructor
		
		:Parameters:
		 - `pti` (float,float) - ith control point
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		_SVGPathCommand.__init__(self,relative)
		self._pt1 = pt1
		self._pt2 = pt2
		self._pt3 = pt3
	
	def copy (self) :
		return _SVGPathCurveToCommand(self._pt1,
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
	"""Factory
	
	Returns the right PathCommand object
	from its textual representation.
	
	:Returns Type: :class:`_SVGPathCommand`
	"""
	relative = typ.islower()
	typ = typ.lower()
	
	if typ == "m" :
		return _SVGPathMoveToCommand(None,None,relative)
	elif typ == "z" :
		return _SVGPathCloseCommand()
	elif typ == "l" :
		return _SVGPathLineToCommand(None,None,relative)
	elif typ == "h" :
		return _SVGPathHorizontalCommand(None,relative)
	elif typ == "v" :
		return _SVGPathVerticalCommand(None,relative)
	elif typ == "c" :
		return _SVGPathCurveToCommand(None,None,None,relative)
	else :
		raise NotImplementedError("path command type not recognized : % s" % typ)

class SVGPath (SVGElement) :
	"""An abstraction of svg path
	
	.. seealso:: <http://wiki.svg.org/Path>
	"""
	def __init__ (self, id=None) :
		"""Constructor
		
		:Parameters:
		 - `id` (str) - a unique id for this node
		"""
		SVGElement.__init__(self,id,None,"svg:path")
		self._commands = []
	
	##################################################
	#
	#		command list
	#
	##################################################
	def commands (self) :
		"""Iterate on commands in this path
		
		:Returns Type: iter of :class:`_SVGPathComand`
		"""
		return iter(self._commands)
	
	def clear (self) :
		"""Discard all commands in this path
		"""
		self._commands = []
	
	def close (self) :
		"""Close the path
		"""
		cmd = _SVGPathCloseCommand()
		self._commands.append(cmd)
	
	def move_to (self, x, y, relative = False) :
		"""Move pen to a given location
		
		:Parameters:
		 - `x` (float) - x displacement if relative
		               or new x coordinate
		 - `y` (float) - y displacement if relative
		               or new x coordinate
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		cmd = _SVGPathMoveToCommand(x,y,relative)
		self._commands.append(cmd)
	
	def line_to (self, x, y, relative = False) :
		"""Trace a straight line up to the
		given location.
		
		:Parameters:
		 - `x` (float) - x displacement if relative
		   or x coordinate of end point of the line
		 - `y` (float) - y displacement if relative
		   or x coordinate of end point of the line
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		cmd = _SVGPathLineToCommand(x,y,relative)
		self._commands.append(cmd)
	
	def curve_to (self, pt1, pt2, pt3, relative = False) :
		"""Trace a curved line between the
		given control points.
		
		:Parameters:
		 - `pti` (float,float) - ith control point
		 - `relative` (bool) - determines
		   if further points will be relative
		   to the previous one or absolute
		"""
		cmd = _SVGPathCurveToCommand(pt1,pt2,pt3,relative)
		self._commands.append(cmd)
	
	def is_closed (self) :
		"""Determines if this path is closed
		
		:Returns Type: bool
		"""
		for cmd in self.commands() :
			if isinstance(cmd,_SVGPathCloseCommand) :
				return True
		return False
	
	##################################################
	#
	#		txt interface
	#
	##################################################
	def from_string (self, txt) :
		"""Construct a path from a string
		representation
		
		:Parameters:
		 - `txt` (str)
		"""
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
			try :
				txt = cmd.from_string(txt)
			except UserWarning,e :
				raise UserWarning("path read fail for %s,\n %s" % (self.id(),e.message) )
			self._commands.append(cmd)
			
			if isinstance(cmd,_SVGPathMoveToCommand) :
				last_cmd = cmd_factory("l")
				last_cmd.set_relative(cmd.is_relative() )
			else :
				last_cmd = cmd
	
	def to_string (self) :
		"""Construct the string representation
		of a path
		
		:Returns Type: str
		"""
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
		"""Load SVG attributes from XML attributes
		"""
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
		"""Save SVG attributes as XML attributes
		"""
		path_txt = self.to_string()
		self.set_attribute("d",path_txt)
		SVGElement.save(self)
	
	##############################################
	#
	#		geometry interface
	#
	##############################################
	def polyline_ctrl_points (self) :
		"""Iterate over a list of control points
		to view this path as a polyline
		
		:Returns Type: iter of (float,float)
		"""
		last_point = (0,0)
		for cmd in self.commands() :
			pts = cmd.polyline_ctrl_points(last_point)
			for pt in pts :
				yield pt
			if len(pts) > 0 :
				last_point = pts[-1]
	
	def nurbs_ctrl_points (self) :#TODO
		"""Iterate over a list of control points
		to view this path as a nurbs
		
		:Returns Type: iter of (float,float)
		"""
		last_point = (0,0)
		for cmd in self.commands() :
			pts = cmd.nurbs_ctrl_points(last_point)
			for pt in pts :
				yield pt
			if len(pts) > 0 :
				last_point = pts[-1]

class SVGConnector (SVGPath) :
	"""Specific type of path that link
	two SVGElements
	"""
	
	def __init__ (self, source, target, id=None) :
		"""Constructor
		
		:Parameters:
		 - `source` (str) - id of source element
		 - `target` (str) - id of target element
		 - `id` (str) - a unique id for this node
		"""
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
		"""Retrieve id of the source
		
		:Returns Type: str
		"""
		return self._source
	
	def target (self) :
		"""Retrieve id of the target
		
		:Returns Type: str
		"""
		return self._target
	
	def set_source (self, svg_elm_id) :
		"""Set source element id
		
		:Parameters:
		 - `svg_elm_id` (str)
		"""
		self._source = svg_elm_id
	
	def set_target (self, svg_elm_id) :
		"""Set target element id
		
		:Parameters:
		 - `svg_elm_id` (str)
		"""
		self._target = svg_elm_id
	
	##############################################
	#
	#		path modification
	#
	##############################################
	def load (self) :
		"""Load SVG attributes from XML attributes
		"""
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
		"""Save SVG attributes as XML attributes
		"""
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

