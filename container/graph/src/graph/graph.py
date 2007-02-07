# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Graph : graph package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provide a simple pure python implementation
for a graph interface
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

from interface import graph
from id_generator import IdGenerator

class InvalidEdge (Exception) :
	"""
	exception raised when a wrong edge id is provided
	"""
	def __init__ (self, *args, **kwds) :
		Exception.__init__(self,*args,**kwds)

class InvalidVertex (Exception) :
	"""
	exception raised when a wrong vertex id is provided
	"""
	def __init__ (self, *args, **kwds) :
		Exception.__init__(self,*args,**kwds)

class Graph (graph.Graph):
	"""
	directed graph with multiple links
	in this implementation :
		- vertices are tuple of edge_in,edge_out
		- edges are tuple of source,target
	"""
	
	def __init__(self, graph=None):
		"""
		constructor 
		if graph is not none make a copy of the topological structure of graph
		(i.e. don't use the same id)
		
		:param graph: the graph to copy, default=None
		:type graph: Graph
		"""
		self._vertices={}
		self._edges={}
		self._vid_generator=IdGenerator()
		self._eid_generator=IdGenerator()
		if graph is not None : dummy=self.extend(graph)

	
	# ##########################################################
	#
	# Graph concept
	#
	# ##########################################################
	def source(self, eid):
		"""
		retrieve the source of an edge
		
		:param eid: id of the edge
		:type eid: eid
		:rtype: vid
		"""
		try :
			return self._edges[eid][0]
		except KeyError :
			raise InvalidEdge(eid)
	
	def target(self, eid):
		"""
		retrieve the target of an edge
		
		:param eid: id of the edge
		:type eid: eid
		:rtype: vid
		"""
		try :
			return self._edges[eid][1]
		except KeyError :
			raise InvalidEdge(eid)
	
	def __contains__(self, vid):
		"""
		test wether a vertex belong to the graph, see `has_vertex`
		
		:param vid: vertex id to test
		:type vid: vid
		:rtype: bool
		"""
		return self.has_vertex(vid)
	
	def has_vertex(self,vid):
		"""
		test wether a vertex belong to the graph
		
		:param vid: vertex id to test
		:type vid: vid
		:rtype: bool
		"""
		return self._vertices.has_key(vid)
	
	def has_edge(self,eid):
		"""
		test wether an edge belong to the graph
		
		:param eid: edge id to test
		:type eid: eid
		:rtype: bool
		"""
		return self._edges.has_key(eid)
	
	def is_valid(self):
		"""
		test the validity of the graph
		
		:rtype: bool
		"""
		return True
	
	# ##########################################################
	#
	# Mutable Grap concept
	#
	# ##########################################################
	def add_vertex(self, vid=None):
		"""
		add a vertex to the graph, if vid is not provided create a new vid
		
		:param vid: the id of the vertex to add, default=None
		:type vid: vid
		:return: the id of the created vertex
		:rtype: vid
		"""
		vid=self._vid_generator.get_id(vid)
		self._vertices[vid]=(set(),set())
		return vid
	
	def remove_vertex(self, vid):
		"""
		remove a specified vertex of the graph
		remove all the edges attached to it
		
		:param vid: the id of the vertex to remove
		:type vid: vid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		link_in,link_out=self._vertices[vid]
		for edge in list(link_in) : self.remove_edge(edge)
		for edge in list(link_out) : self.remove_edge(edge)
		del self._vertices[vid]
		self._vid_generator.release_id(vid)
	
	def add_edge(self, edge= (None,None), eid= None):
		"""
		add an edge to the graph, if eid is not provided create a new eid
		
		:Parameters:
			- `edge` : a tuple (vertex source,vertex target)
			- `eid` : the id of the created edge
		:Types:
			- `edge` : (vid,vid)
			- `eid` : eid
		:return: the id of the newly created edge
		:rtype: eid
		"""
		vs,vt=edge
		if vs not in self :
			raise InvalidVertex(vs)
		if vt not in self :
			raise InvalidVertex(vt)
		eid=self._eid_generator.get_id(eid)
		self._edges[eid]=(vs,vt)
		self._vertices[vs][1].add(eid)
		self._vertices[vt][0].add(eid)
		return eid
	
	def remove_edge(self,eid):
		"""
		remove a specified edge from the graph
		
		:param eid: id of the edge to remove
		:type eid: eid
		"""
		if not self.has_edge(eid) :
			raise InvalidEdge(eid)
		vs,vt=self._edges[eid]
		self._vertices[vs][1].remove(eid)
		self._vertices[vt][0].remove(eid)
		del self._edges[eid]
		self._eid_generator.release_id(eid)
	
	def clear(self):
		"""
		remove all vertices and edges
		don't change references to objects
		"""
		raise RuntimeError()
	
	def clear_edges(self):
		"""
		remove all the edges of the graph
		don't change references to objects
		"""
		self._vertices.clear()
		self._edges.clear()
		self._vid_generator=IdGenerator()
		self._eid_generator=IdGenerator()
	
	def extend(self, graph):
		"""
		add the specified graph to self, create new vid and eid
		
		:param graph: the graph to add
		:type graph: Graph
		:return: two dictionnary specifying correspondence between graph id and self id
		:rtype: ({vid:vid},{eid:eid})
		"""
		#vertex adding
		trans_vid={}
		for vid in graph.vertices() :
			trans_vid[vid]=self.add_vertex()
		
		#edge adding
		trans_eid={}
		for eid in graph.edges() :
			sid=trans_vid[graph.source(eid)]
			tid=trans_vid[graph.target(eid)]
			trans_eid[eid]=self.add_edge(edge=(sid,tid))
		
		return trans_vid,trans_eid

	
	# ##########################################################
	#
	# Vertex List Graph Concept
	#
	# ##########################################################
	def vertices(self):
		"""
		iterator on vertices
		
		:rtype: iter of vid
		"""
		return iter(self._vertices)
	
	def __iter__ (self) :
		"""
		magic function for `vertices`
		
		:rtype: iter of vid
		"""
		return iter(self._vertices)
	
	def nb_vertices(self):
		"""
		return the total number of vertices
		
		:rtype: int
		"""
		return len(self._vertices)
	
	def __len__(self):
		"""
		magic function for `nb_vertices`
		
		:rtype: int
		"""
		return self.nb_vertices()
	
	def in_neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		where edges are directed from neighbor to vid
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		neighbors_list=[self.source(eid) for eid in self._vertices[vid][0] ]
		return iter(set(neighbors_list))

	
	def out_neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		where edges are directed from vid to neighbor
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		neighbors_list=[self.target(eid) for eid in self._vertices[vid][1] ]
		return iter(set(neighbors_list))
	
	def neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		regardless of the orientation of the edge
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		neighbors_list=list(self.in_neighbors(vid))
		neighbors_list.extend(self.out_neighbors(vid))
		return iter(set(neighbors_list))
	
	def nb_in_neighbors(self, vid):
		"""
		number of neighbors such as edges are directed from neighbor to vid
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		neighbors_set=list(self.in_neighbors(vid))
		return len(neighbors_set)
	
	def nb_out_neighbors(self, vid):
		"""
		number of neighbors such as edges are directed from vid to neighbor
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		neighbors_set=list(self.out_neighbors(vid))
		return len(neighbors_set)
	
	def nb_neighbors(self, vid):
		"""
		number of neighbors regardless of the orientation of the edge
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		neighbors_set=list(self.neighbors(vid))
		return len(neighbors_set)
	
	# ##########################################################
	#
	# Edge List Graph Concept
	#
	# ##########################################################
	def _edges (self, vid) :
		"""
		internal function that perform 'edges' with vid not None
		"""
		link_in,link_out=self._vertices[vid]
		for eid in link_in : yield eid
		for eid in link_out : yield eid
	
	def edges(self, vid=None):
		"""
		retrieve the edges linked to a specified vertex,
		all if vid is None
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid is None :
			return iter(self._edges)
		if vid not in self :
			raise InvalidVertex(vid)
		return self._edges(vid)
	
	def nb_edges(self, vid=None):
		"""
		number of edges linked to a specified vertex,
		total number if vid is None
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid is None :
			return len(self._edges)
		if vid not in self :
			raise InvalidVertex(vid)
		return len(self._vertices[vid][0])+len(self._vertices[vid][1])
	
	def in_edges(self, vid):
		"""
		retrieve the edges linked to a specified vertex,
		oriented inside the vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		for eid in self._vertices[vid][0] : yield eid
	
	def out_edges(self, vid):
		"""
		retrieve the edges linked to a specified vertex,
		oriented outside the vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		for eid in self._vertices[vid][1] : yield eid
	
	def nb_in_edges(self, vid):
		"""
		number of edges linked to a specified vertex,
		oriented inside vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		return len(self._vertices[vid][0])
	
	def nb_out_edges(self, vid):
		"""
		number of edges linked to a specified vertex,
		oriented outside vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		if vid not in self :
			raise InvalidVertex(vid)
		return len(self._vertices[vid][1])
	
	def edge(self, source, target) :
		"""
		find the matching edge with same source and same target
		return None if it don't succeed
		
		:Parameters:
			- `source` : id of the source vertex
			- `target` : id of the target vertex
		:Types:
			- `source` : vid
			- `target` : vid
		:rtype: eid|None
		"""
		edge_comp=(source,target)
		for eid,edge in self._edges.iteritems() :
			if edge==edge_comp :
				return eid
		return None
	
	# ##########################################################
	#
	# Copy graph concept
	#
	# ##########################################################
	def copy(self):
		"""
		make a shallow copy of the graph,
		for a deep copy use the constructor `__init__`
		"""
		raise NotImplementedError()

