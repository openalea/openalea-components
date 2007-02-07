"""un mesh topologique relie les elements de deux ensembles distincts
E1 et E2 et defini un voisinage implicite entre les element d'un ensemble
E1 comme l'ensemble des elements de E1 qui partagent le meme element de E2

Les liens ne sont pas explicitement definis. Il est cependant aise d'utiliser
le tuple (source,target) comme clef pour une map sur les liens implicites"""
from sets import Set

class InvalidCell (Exception) :
	"""exception raised when a wrong cell id is provided"""
	def __init__ (self, cid) :
		Exception.__init__(self,"cell %d does not exist" % cid)

class InvalidPoint (Exception) :
	"""exception raised when a wrong point id is provided"""
	def __init__ (self, pid) :
		Exception.__init__(self,"point %d does not exist" % pid)

class InvalidLink (Exception) :
	"""exception raised when a link between a cell and a point odes not exist"""
	def __init__ (self, cid, pid) :
		Exception.__init__(self,"the link betwwen cell %d and point %d does not exist" % (cid,pid))

class TopologicalMesh (object) :
	
	def __init__ (self) :
		self._cells={}
		self._points={}
		self._cid_max=0
		self._pid_max=0
	
	########################################################################
	#
	#		Mesh concept
	#
	########################################################################
	def is_valid (self) :
		"""test wether the mesh fulfill all mesh properties"""
		return False
	
	def has_point (self, pid) :
		"""return true if pid in mesh"""
		return pid in self._points
	
	def has_cell (self, cid) :
		"""return true if cid in mesh"""
		return cid in self._cells
	
	########################################################################
	#
	#		Cell list concept
	#
	########################################################################
	def _cells_around_point (self, pid) :
		"""iterator on cells around a given point"""
		try :
			return iter(self._points[pid])
		except KeyError :
			raise InvalidPoint(pid)
	
	def cells (self, pid=None) :
		"""iterator on cells linked to a given point or all cells if None"""
		if pid is not None : return self._cells_around_point(pid)
		return self._cells.iterkeys()
	
	def nb_cells (self, pid=None) :
		"""number of cells around a point or total number of cell if None"""
		if pid is not None :
			try :
				return len(self._points[pid])
			except KeyError :
				raise InvalidPoint(pid)
		return len(self._cells)
	
	def cell_neighbors (self, cid) :
		"""iterator on all implicit neighbors of a cell"""
		already_viewed=[cid]
		try :
			for pid in self._cells[cid] :
				for ncid in self._points[pid] :
					if ncid not in already_viewed :
						already_viewed.append(ncid)
						yield ncid
		except KeyError :
			raise InvalidCell(cid)
	
	def nb_cell_neighbors (self, cid) :
		"""nb of implicit neighbors of a cell"""
		s=Set()
		try :
			for pid in self._cells[cid] :
				s.union(self._points[pid])
			return len(s)-1
		except KeyError :
			raise InvalidCell(cid)
	
	#########################################################################
	#
	#		Point list concept
	#
	#########################################################################
	def _points_around_cell (self, cid) :
		"""iterator on all points around a cell"""
		try :
			return iter(self._cells[cid])
		except KeyError :
			raise InvalidCell(cid)
	
	def points (self, cid=None) :
		"""iterator on point around a given cell or all points if None"""
		if cid is not None : return self._points_around_cell(cid)
		return self._points.iterkeys()
	
	def nb_points (self, cid=None) :
		"""number of cells around a point or total number of points if None"""
		if cid is not None :
			try :
				return len(self._cells[cid])
			except KeyError :
				raise InvalidCell(cid)
		return len(self._points)
	
	def point_neighbors (self, pid) :
		"""iterator on all implicit neighbors of a point"""
		already_viewed=[pid]
		try :
			for cid in self._points[pid] :
				for npid in self._cells[cid] :
					if npid not in already_viewed :
						already_viewed.append(npid)
						yield npid
		except KeyError :
			raise InvalidPoint(pid)
	
	def nb_point_neighbors (self, pid) :
		"""number of implicit neighbors of a point"""
		s=Set()
		try :
			for cid in self._points[pid] :
				s.union(self._cells[cid])
			return len(s)-1
		except KeyError :
			raise InvalidPoint(pid)

	#######################################################################
	#
	#		Alias functions
	#
	#######################################################################
	def neighbors (self, cell=None, point=None) :
		"""iterator on implicit neighbors"""
		if cell is not None : return self.cell_neighbors(cell)
		if point is not None : return self.point_neighbors(point)
		raise UserWarning("you must specify a cell or a point")
	
	def nb_neighbors (self, cell=None, point=None) :
		"""nb of implicit neighbors"""
		if cell is not None : return self.nb_cell_neighbors(cell)
		if point is not None : return self.nb_point_neighbors(point)
		raise UserWarning("you must specify a cell or a point")
	
	########################################################################
	#
	#		Mutable mesh concept
	#
	########################################################################
	def add_cell (self, cid=None) :
		"""add a new cell connected to nothing"""
		if cid is None :
			cid=self._cid_max
			self._cid_max+=1
		else :
			if cid in self._cells : return cid
			else : self._cid_max=max(self._cid_max,cid+1)
		self._cells[cid]=Set()
		return cid
	
	def add_point (self, pid=None) :
		"""add a new point connected to nothing"""
		if pid is None :
			pid=self._pid_max
			self._pid_max+=1
		else :
			if pid in self._points : return pid
			else : self._pid_max=max(self._pid_max,pid+1)
		self._points[pid]=Set()
		return pid
	
	def add_link (self, cid, pid) :
		"""add a link between a cell and a point
		do not create existing entities if absent"""
		try :
			cell_set=self._cells[cid]
		except KeyError :
			raise InvalidCell(cid)
		try :
			self._points[pid].add(cid)
			cell_set.add(pid)
		except KeyError :
			raise InvalidPoint(pid)
	
	def remove_cell (self, cid) :
		"""remove a cell and all the references to attached points"""
		try :
			for pid in self._cells[cid] :
				self._points[pid].remove(cid)
			del self._cells[cid]
		except KeyError :
			raise InvalidCell(cid)
	
	def remove_point (self, pid) :
		"""remove a point and all the references to attached cells"""
		try :
			for cid in self._points[pid] :
				self._cells[cid].remove(pid)
			del self._points[pid]
		except KeyError :
			raise InvalidPoint(pid)
	
	def remove_link (self, cid, pid) :
		"""remove a link between a cell and a point"""
		try :
			cell_set=self._cells[cid]
		except KeyError :
			raise InvalidCell(cid)
		try :
			point_set=self._points[pid]
		except KeyError :
			raise InvalidPoint(pid)
		try :
			cell_set.remove(pid)
			point_set.remove(cid)
		except KeyError :
			raise InvalidLink(cid,pid)

if __name__=='__main__' :
	m=TopologicalMesh()
	for i in xrange(9) : m.add_point()
	for i in xrange(4) : m.add_cell()
	for cid,l in enumerate([[0,1,3,4],[1,2,4,5],[3,4,6,7],[4,5,7,8]]) :
		for pid in l : m.add_link(cid,pid)
	print "points",list(m.points())
	print "cells",list(m.cells())
	print "points around 0",list(m.points(0))
	print "cells around 0",list(m.cells(0))
	print "cells around 4",list(m.cells(4))
	print "neighbors of cell 0",list(m.neighbors(cell=0))
	print "neighbors of point 0",list(m.neighbors(point=0))
	print "neighbors of point 4",list(m.neighbors(point=4))

	
