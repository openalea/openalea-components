# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2011 INRIA - CIRAD - INRA
#
#       File author(s): Jonathan Legrand
#                       Christophe Pradal
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
################################################################################
"""This module provide a class that extends the PropertyGraph with different types of edges"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from property_graph import *
import networkx as nx


class TemporalPropertyGraph(PropertyGraph):
    """
    Simple implementation of PropertyGraph using
    dict as properties and two dictionaries to
    maintain these properties
    """
    STRUCTURAL = 's'
    TEMPORAL = 't'

    def __init__(self, graph=None, **kwds):
        PropertyGraph.__init__(self, graph, idgenerator='max',**kwds)
        self.add_edge_property('edge_type')

        # list of dict
        # each dict define the mapping between the new and the old vid.
        # old label define both graph index and local id.
        self.add_edge_property('old_label')
        self.add_vertex_property('old_label')
        self.add_vertex_property('index')
        self._old_to_new_ids = []

    def extend(self, graphs, mappings):
        """ Extend the structure with graphs and mappings.
        Each graph contains structural edges. 
        Mapping define dynamic edges between two graphs.

        :Parameters:
            - graphs - a list of PropertyGraph
            - mappings - a list defining the dynamic or temporal edges between two graphs.

        :warning:: len(graphs) == len(mappings)-1
        """

        assert len(graphs) == len(mappings)+1

        self.append(graphs[0])
        for g, m in zip(graphs[1:],mappings):
            self.append(g,m)

        return self._old_to_new_ids

    def append(self, graph, mapping=None):
        """

        """
        if mapping:
            assert len(self._old_to_new_ids) >= 1, 'You have to create temporal edges between two graphs. Add a graph first without mapping'

        current_index = len(self._old_to_new_ids)

        edge_types = self.edge_property('edge_type')
        old_edge_labels = self.edge_property('old_label')
        old_vertex_labels = self.vertex_property('old_label')
        indices = self.vertex_property('index')

        relabel_ids = PropertyGraph.extend(self,graph)
        self._old_to_new_ids.append(relabel_ids)

        old_to_new_vids = relabel_ids[0]
        old_to_new_eids = relabel_ids[1]

        # set edge_type property for structural edges
        for old_eid, eid in old_to_new_eids.iteritems():
            edge_types[eid] = self.STRUCTURAL
            old_edge_labels[eid] = old_eid

        for old_vid, vid in old_to_new_vids.iteritems():
            old_vertex_labels[vid] = old_vid
            indices[vid] = current_index

        if mapping:
            on_ids_source, on_ids_target = self._old_to_new_ids[-2:] 
            for k, l in mapping.iteritems():
                for v in l:
                    eid = self.add_edge(on_ids_source[0][k], on_ids_target[0][v])
                    edge_types[eid] = self.TEMPORAL

        return relabel_ids


    def clear(self):
        PropertyGraph.clear(self)
        self._old_to_new_ids = []


    def to_networkx(self):
        """ Return a NetworkX Graph from a graph.

        :Parameters: 

            - `g` - TemporalPropertyGraph 
                a dynamic property graph 
        
        :Returns: 

            - A NetworkX graph.

        """
        
        g = self

        graph = nx.Graph()
        graph.add_nodes_from(g.vertices())
        graph.add_edges_from(( (g.source(eid), g.target(eid)) for eid in g.edges()))

        # Add graph, vertex and edge properties
        for k, v in g.graph_property().iteritems():
            graph.graph[k] = v

        vp = g._vertex_property
        for prop in vp:
            for vid, value in vp[prop].iteritems():
                graph.node[vid][prop] = value
        
        ep = g._edge_property
        for eid in g.edges():
            graph.edge[g.source(eid)][g.target(eid)]['eid'] = eid

        for prop in ep:
            for eid, value in ep[prop].iteritems():
                graph.edge[g.source(eid)][g.target(eid)][prop] = value

        return graph 

    def from_networkx(self, graph):
        """ Return a Graph from a NetworkX Directed graph.

        :Parameters: 
            - `graph` : A NetworkX graph.

        :Returns: 
            - `g`: a :class:`~openalea.container.interface.Graph`.

        """
        self.clear()
        
        g = self

        if not graph.is_directed():
            graph = graph.to_directed()

        vp = self._vertex_property

        for vid in graph.nodes_iter():
            g.add_vertex(vid)
            d = graph.node[vid]
            for k, v in d.iteritems():
                vp.setdefault(k,{})[vid] = v


        ep = self._edge_property
        for source, target in graph.edges_iter():
            d = graph[source][target]
            eid = d.get('eid')
            eid = g.add_edge(source, target, eid)
            for k, v in d.iteritems():
                if k != 'eid':
                    ep.setdefault(k,{})[eid] = v

        gp = self._graph_property
        gp.update(graph.graph)

        return g
    
    def to_set(s):
        if not isinstance(s, set):
            if is_instance(s, list):
                s=set(s)
            else:
                s=set([s])
        return s

    def in_neighbors(self, vid, edge_type=None):
        """ Return the in vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `neighbors_list` : the set of parent vertices of the vertex vid
        """
        if vid not in self :
            raise InvalidVertex(vid)
        if edge_type==None:
            edge_type=set(self.edge_property('edge_type').itervalues())
        else:
            edge_type=to_set(edge_type) 
        tmp=self.edge_property('edge_type')
        neighbors_list=set()
        for k, v in tmp.iteritems():
            if ((v in edge_type) & (self._edges[k][1]==vid)):
                neighbors_list.add(self._edges[k][0])
        return neighbors_list
  
    def iter_in_neighbors(self, vid, edge_type=None):
        """ Return the in vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterartor` : an iterator on the set of parent vertices of the vertex vid
        """
        return iter(self.in_neighbors(vid, edge_type))
  
    def out_neighbors(self, vid, edge_type=None):
        """ Return the out vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `neighbors_list` : the set of child vertices of the vertex vid
        """
        if vid not in self :
            raise InvalidVertex(vid)
        if edge_type==None:
            edge_type=set(self.edge_property('edge_type').itervalues())
        else:
            edge_type=to_set(edge_type)
        tmp=self.edge_property('edge_type')
        neighbors_list=set()
        for k, v in tmp.iteritems():
            if ((v in edge_type) & (self._edges[k][0]==vid)):
                neighbors_list.add(self._edges[k][1])
        return neighbors_list
                    
    def iter_out_neighbors(self, vid, edge_type=None):
        """ Return the out vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterartor` : an iterator on the set of child vertices of the vertex vid
        """
        return iter(self.out_neighbors(vid, edge_type))
  
    def neighbors(self, vid, edge_type=None):
        """ Return the neighbors vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `neighbors_list` : the set of neighobrs vertices of the vertex vid
        """
        return self.in_neighbors(vid, edge_type) | self.out_neighbors(vid, edge_type)

    def iter_neighbors(self, vid, edge_type=None):
        """ Return the neighbors vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterartor` : iterator on the set of neighobrs vertices of the vertex vid
        """
        return iter(self.neighbors(vid, edge_type))
  

    def in_edges(self, vid, edge_type=None):
        """ Return in edges of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `edge_list` : the set of the in edges of the vertex vid
        """
        if vid not in self :
            raise InvalidVertex(vid)
        tmp=self.edge_property('edge_type')
        if edge_type==None:
            edge_type=set(self.edge_property('edge_type').itervalues())
        else:
            edge_type=to_set(edge_type)
        edge_list=set()
        for k , v in tmp.iteritems():
            if ((v in edge_type) & (self._edges[k][1]==vid)):
                edge_list.add(k)
        return  edge_list
        
    def iter_in_edges(self, vid, edge_type=None):
        """ Return in edges of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterator` : an iterator on the set of the in edges of the vertex vid
        """  
        return iter(self.in_edges(vid, edge_type))


    def out_edges(self, vid, edge_type=None):
        """ Return out edges of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `edge_list` : the set of the out edges of the vertex vid
        """
        if vid not in self :
            raise InvalidVertex(vid)
        tmp=self.edge_property('edge_type')
        if edge_type==None:
            edge_type=set(self.edge_property('edge_type').itervalues())
        else:
            edge_type=to_set(edge_type)
        edge_list=set()
        for k , v in tmp.iteritems():
            if ((v in edge_type) & (self._edges[k][0]==vid)):
                edge_list.add(k)
        return  edge_list

    def iter_out_edges(self, vid, edge_type=None):
        """ Return in edges of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider

        :Returns:
        - `iterator` : an iterator on the set of the in edges of the vertex vid
        """  
        return iter(self.out_edges(vid, edge_type))


    def edges(self, vid=None, edge_type=None):
        """ Return edges of the vertex vid
        If vid=None, return all edges of the graph
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider

        :Returns:
        - `edge_list` : the set of the edges of the vertex vid
        """
        return self.out_edges(vid, edge_type) | self.in_edges(vid, edge_type)

    def iter_edges(self, vid, edge_type=None):
        """ Return in edges of the vertex vid
        If vid=None, return all edges of the graph
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider

        :Returns:
        - `iterator` : an iterator on the set of the edges of the vertex vid
        """  
        return iter(self.edges(vid, edge_type))

    
    def children(self, vid):
        """ Return children of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `children_list` : the set of the children of the vertex vid
        """
        return self.out_neighbors(vid, 't')

    def iter_children(self, vid):
        """ Return children of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `iterator` : an iterator on the set of the children of the vertex vid
        """
        return iter(self.children(vid))

    def parent(self, vid):
        """ Return parents of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `parents_list` : the set of the parents of the vertex vid
        """
        return self.in_neighbors(vid, 't')

    def iter_parent(self, vid):
        """ Return parents of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `iterator` : the set of the children of the vertex vid
        """
        return iter(self.parent(vid))

    def sibling(self, vid):
        """ Return sibling of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `sibling_list` : the set of sibling of the vertex vid
        """
        return self.children(self.parent(vid))-set([vid])

    def iter_sibling(self, vid):
        """ Return of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `iterator` : an iterator on the set of sibling of the vertex vid
        """
        return iter(self.sibling(vid))

    
    def neighborhood(self, vids, n=1, edge_type=None):
        """ Return the neighborhood of the vertex vid at distance n (the disc, not the circle)
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `neighbors_list` : the set of the vertices at distance n of the vertex vid
        """
        neighbs=set()
        if n==1 :
            for vid in vids:
                neighbs |= (self.neighbors(vid, edge_type) | set([vid]))
            return neighbs
        else :
            for vid in vids :
                neighbs |= (self.neighborhood(self.neighbors(vid, edge_type), n-1, edge_type) | set([vid]))
                if list(neighbs)==self._vertices.keys():
                    return neighbs
        return neighbs

    def iter_neighborhood(self, vid, n, edge_type=None):
        """ Return the neighborhood of the vertex vid at distance n (the disc, not the circle)
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the vertices at distance n of the vertex vid
        """
        return iter(self.neighborhood(vid, n, edge_type))      
    

    def descendants(self, vids, n):
        """ Return the 0, 1, ..., nth descendants of the vertex vid
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `descendant_list` : the set of the 0, 1, ..., nth descendant of the vertex vid
        """
        edge_type='t'
        neighbs=set()
        if n==1 :
            for vid in vids:
                neighbs |= (self.out_neighbors(vid, 't') | set([vid]))
            return neighbs
        else :
            for vid in vids :
                neighbs |= (self.descendants(self.out_neighbors(vid, 't'), n-1) | set([vid]))
                if list(neighbs)==self._vertices.keys():
                    return neighbs
        return neighbs

    def iter_descendant(self, vids, n):
        """ Return the 0, 1, ..., nth descendants of the vertex vid
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the 0, 1, ..., nth descendants of the vertex vid
        """
        return iter(self.descendant(vids, n))
            

    def ancestors(self, vids, n):
        """ Return the 0, 1, ..., nth ancestors of the vertex vid
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `anestors_list` : the set of the 0, 1, ..., nth ancestors of the vertex vid
        """
        edge_type='t'
        neighbs=set()
        if n==1 :
            for vid in vids:
                neighbs |= (self.in_neighbors(vid, 't') | set([vid]))
            return neighbs
        else :
            for vid in vids :
                neighbs |= (self.ancestors(self.in_neighbors(vid, 't'), n-1) | set([vid]))
                if list(neighbs)==self._vertices.keys():
                    return neighbs
        return neighbs

    def iter_ancestors(self, vids, n):
        """ Return the 0, 1, ..., nth ancestors of the vertex vid
        
        :Parameters:
        - `vid` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the 0, 1, ..., nth ancestors of the vertex vid
        """
        return iter(self.ancestors(vids, n))
  
    def unity_dist(self, vid1, vid2):
        #if not vid2 in (self._vertices[vid1][0] | self._vertices[vid1][1]):
         #   print vid1, vid2
          #  raise InvalidVertex(vid1)
        return 1

    def topo_dist(self, vid, edge_type=None, func=None):
        """ Return the distances of each vertices at the vertex vid according a cost function
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider
        - `func` : the cost function, if it's None each edge has 1 for cost

        :Returns:
        - `dist_dict` : a dictionary of the distances, key : vid, value : distance
        """
        import numpy as np
        if func==None :
            func=self.unity_dist
        dist={}
        untreated=set()
        for k in self._vertices.iterkeys():
            dist[k]=float('inf')
            untreated.add(k)
        #untreated-=set([vid]).
        treated=set()
        dist[vid]=0
        modif=True
        while (len(untreated)>0):
            tmpDist=dist.copy()
            for k in treated:
                tmpDist.pop(k)
            actualVid=[k for k in tmpDist.keys()][np.argmin(tmpDist.values())]
            untreated-=set([actualVid])
            treated|=set([actualVid])
            modif=False 
            for neighb in self.iter_neighbors(actualVid, edge_type):
                if dist[neighb] > dist[actualVid] + func(neighb, actualVid):
                    dist[neighb]=dist[actualVid] + func(neighb, actualVid)
        return dist
        

    def sub_graph(self, vids):
        """
        """
        #ret=self.copy()
        

    def group_by(self, func):
        """ Return a cluster of the vertices according a function
        
        :Parameters:
        - `fund` : the function to make the clusters

        :Returns:
        - `cluster_dict` : a dictionary of the clusters, key : cluster, value : set of vid in this cluster
        """
        ret={}
        for k in self._vertices.keys():
            ret.setdefault(func(k)).append(k)
        return ret


def test(display=False):
    import random
    g = TemporalPropertyGraph()
    #
    p1, p2 = PropertyGraph(), PropertyGraph()
    vids = range(1,10)
    edges = []
    for i in vids:
        l = range((i+1),10)
        random.shuffle(l)
        for j in l[:3]:
            edges.append((i,j))
    mapping = dict((vid,[vid]) for vid in vids)
    #
    for v in vids:
        p1.add_vertex(v)
        p2.add_vertex(v)
    for s,t in edges:
        p1.add_edge(s,t)
        p2.add_edge(s,t)
    #
    g.extend([p1,p2],[mapping])
    #
    #nxg = g.to_networkx()
    #
    #gg = TemporalPropertyGraph().from_networkx(nxg)
    #
    #if display:
    #    import matplotlib.pyplot as plt
    #    nx.draw(nxg)
    #    plt.show()
    #
    return g
