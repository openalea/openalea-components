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

def test(display=False):
    import random
    g = TemporalPropertyGraph()

    p1, p2 = PropertyGraph(), PropertyGraph()
    vids = range(1,10)
    edges = []
    for i in vids:
        l = range((i+1),10)
        random.shuffle(l)
        for j in l[:3]:
            edges.append((i,j))
    mapping = dict((vid,[vid]) for vid in vids)

    for v in vids:
        p1.add_vertex(v)
        p2.add_vertex(v)
    for s,t in edges:
        p1.add_edge(s,t)
        p2.add_edge(s,t)
    
    g.extend([p1,p2],[mapping])

    nxg = g.to_networkx()

    gg = TemporalPropertyGraph().from_networkx(nxg)
    
    if display:
			import matplotlib.pyplot as plt
			nx.draw(nxg)
			plt.show()

    return g, gg, nxg
