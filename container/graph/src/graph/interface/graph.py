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
This module provide a graph interface
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

class InvalidEdge (Exception) :
	"""
	exception raised when a wrong edge id is provided
	"""
	def __init__ (self, *arg) :
		raise RuntimeError()

class InvalidVertex (Exception) :
	"""
	exception raised when a wrong vertex id is provided
	"""
	def __init__ (self, *arg) :
		raise RuntimeError()

class Graph (object):
	"""
	directed graph with multiple links
	"""
	
	def __init__(self, graph=None):
		"""
		constructor 
		if graph is not none make a copy of the topological structure of graph
		(i.e. don't use the same id)
		
		:param graph: the graph to copy, default=None
		:type graph: Graph
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def target(self, eid):
		"""
		retrieve the target of an edge
		
		:param eid: id of the edge
		:type eid: eid
		:rtype: vid
		"""
		raise RuntimeError()
	
	def __contains__(self, vid):
		"""
		test wether a vertex belong to the graph, see `has_vertex`
		
		:param vid: vertex id to test
		:type vid: vid
		:rtype: bool
		"""
		raise RuntimeError()
	
	def has_vertex(self,vid):
		"""
		test wether a vertex belong to the graph
		
		:param vid: vertex id to test
		:type vid: vid
		:rtype: bool
		"""
		raise RuntimeError()
	
	def has_edge(self,eid):
		"""
		test wether an edge belong to the graph
		
		:param eid: edge id to test
		:type eid: eid
		:rtype: bool
		"""
		raise RuntimeError()
	
	def is_valid(self):
		"""
		test the validity of the graph
		
		:rtype: bool
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def remove_vertex(self, vid):
		"""
		remove a specified vertex of the graph
		remove all the edges attached to it
		
		:param vid: the id of the vertex to remove
		:type vid: vid
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def remove_edge(self,eid):
		"""
		remove a specified edge from the graph
		
		:param eid: id of the edge to remove
		:type eid: eid
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def extend(self, graph):
		"""
		add the specified graph to self, create new vid and eid
		
		:param graph: the graph to add
		:type graph: Graph
		:return: two dictionnary specifying correspondence between graph id and self id
		:rtype: ({vid:vid},{eid:eid})
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
	def __iter__ (self) :
		"""
		magic function for `vertices`
		
		:rtype: iter of vid
		"""
		raise RuntimeError()
	
	def nb_vertices(self):
		"""
		return the total number of vertices
		
		:rtype: int
		"""
		raise RuntimeError()
	
	def __len__(self):
		"""
		magic function for `nb_vertices`
		
		:rtype: int
		"""
		raise RuntimeError()
	
	def in_neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		where edges are directed from neighbor to vid
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		raise RuntimeError()
	
	def out_neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		where edges are directed from vid to neighbor
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		raise RuntimeError()
	
	def neighbors(self, vid):
		"""
		iterator on the neighbors of vid
		regardless of the orientation of the edge
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: iter of vid
		"""
		raise RuntimeError()
	
	def nb_in_neighbors(self, vid):
		"""
		number of neighbors such as edges are directed from neighbor to vid
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		raise RuntimeError()
	
	def nb_out_neighbors(self, vid):
		"""
		number of neighbors such as edges are directed from vid to neighbor
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		raise RuntimeError()
	
	def nb_neighbors(self, vid):
		"""
		number of neighbors regardless of the orientation of the edge
		
		:param vid: id of the reference vertex
		:type vid: vid
		:rtype: int
		"""
		raise RuntimeError()
	
	# ##########################################################
	#
	# Edge List Graph Concept
	#
	# ##########################################################
	def edges(self, vid= None):
		"""
		retrieve the edges linked to a specified vertex,
		all if vid is None
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
	def nb_edges(self, vid= None):
		"""
		number of edges linked to a specified vertex,
		total number if vid is None
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
	def in_edges(self, vid):
		"""
		retrieve the edges linked to a specified vertex,
		oriented inside the vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
	def out_edges(self, vid):
		"""
		retrieve the edges linked to a specified vertex,
		oriented outside the vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
	def nb_in_edges(self, vid):
		"""
		number of edges linked to a specified vertex,
		oriented inside vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
	def nb_out_edges(self, vid):
		"""
		number of edges linked to a specified vertex,
		oriented outside vertex
		
		:param vid: id of the reference vertex, default=None
		:type vid: vid
		:rtype: iter of eid
		"""
		raise RuntimeError()
	
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
		raise RuntimeError()
	
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
		raise RuntimeError()

