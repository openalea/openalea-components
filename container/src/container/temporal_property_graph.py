# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2011 - 2012 INRIA - CIRAD - INRA
#
#       File author(s): Jonathan Legrand <jonathan.legrand@ens-lyon.fr>
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
import warnings
from openalea.container.temporal_graph_analysis import translate_ids_Image2Graph, translate_keys_Graph2Image

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
        self.nb_time_points = 0


    def extend(self, graphs, mappings, time_steps = None):
        """ Extend the structure with graphs and mappings.
        Each graph contains structural edges. 
        Mapping define dynamic edges between two graphs.

        :Parameters:
            - graphs - a list of PropertyGraph
            - mappings - a list defining the dynamic or temporal edges between two graphs.
            - time_steps - time corresponding to each graph

        :warning:: len(graphs) == len(mappings)-1
        """

        assert len(graphs) == len(mappings)+1

        self.append(graphs[0])
        #~ self.add_graph_property('nb_time_points')
        #~ len(mappings) = self.graph_property('nb_time_points')
        for g, m in zip(graphs[1:],mappings):
            self.append(g,m)
            self.nb_time_points += 1

        if time_steps is not None:
            assert len(graphs) == len(time_steps)
            self.add_graph_property('time_steps',time_steps)

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

        # add and translate the vertex and edge ids of the second graph
        relabel_ids = Graph.extend(self,graph)
        old_to_new_vids, old_to_new_eids = relabel_ids
        # relabel the edge and vertex property
        self._relabel_and_add_vertex_edge_properties(graph, old_to_new_vids, old_to_new_eids)

        # update properties on graph
        temporalgproperties = self.graph_properties()

        # while on a property graph, graph_property are just dict of dict, 
        # on a temporal property graph, graph_property are dict of list of dict
        # to keep the different values for each time point.

        for gname in graph.graph_property_names():
            if gname in [self.metavidtypepropertyname,self.metavidtypepropertyname]:
                temporalgproperties[gname] = graph.graph_property(gname)
            else:
                newgproperty = graph.translate_graph_property(gname, old_to_new_vids, old_to_new_eids)            
                temporalgproperties[gname] = temporalgproperties.get(gname,[])+[newgproperty]

        self._old_to_new_ids.append(relabel_ids)

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
                # Check if the mother cell and ALL daugthers are present in their respective graph : WE DON'T WANT TO CREATE A PARTIAL LINEAGE !!!!
                if on_ids_source[0].has_key(k) and ( sum([on_ids_target[0].has_key(v) for v in l]) == len(l) ):
                    for v in l:
                        eid = self.add_edge(on_ids_source[0][k], on_ids_target[0][v])
                        edge_types[eid] = self.TEMPORAL

        return relabel_ids

    def clear(self):
        PropertyGraph.clear(self)
        self._old_to_new_ids = []

    def __to_set(self, s):
        if not isinstance(s, set):
            if isinstance(s, list):
                s=set(s)
            else:
                s=set([s])
        return s

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

    def has_children(self, vid):
        """
        Return True if the vid `vid` has a child or children.
        """
        if self.children(vid) != set():
            return True
        else:
            return False

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

    def has_parent(self, vid):
        """
        Return True if the vid `vid` has a parent.
        """
        if self.parent(vid) != set():
            return True
        else:
            return False

    def sibling(self, vid):
        """ Return sibling of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `sibling_list` : the set of sibling of the vertex vid
        """
        if self.parent(vid):
            return self.children(self.parent(vid).pop())-set([vid])
        else:
            return None

    def iter_sibling(self, vid):
        """ Return of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id

        :Returns:
        - `iterator` : an iterator on the set of sibling of the vertex vid
        """
        return iter(self.sibling(vid))    

    def descendants(self, vids, n):
        """ Return the 0, 1, ..., nth descendants of the vertex vid
        
        :Parameters:
        - `vids` : a set of vertex id

        :Returns:
        - `descendant_list` : the set of the 0, 1, ..., nth descendant of the vertex vid
        """
        edge_type='t'
        neighbs=set()
        vids=self.__to_set(vids)
        if n==0 :
            return vids
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
        - `vids` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the 0, 1, ..., nth descendants of the vertex vid
        """
        return iter(self.descendant(vids, n))

    def ancestors(self, vids, n):
        """Return the 0, 1, ..., nth ancestors of the vertex vid
        
        :Parameters:
        - `vids` : a set of vertex id
        
        :Returns:
        - `anestors_list` : the set of the 0, 1, ..., nth ancestors of the vertex vid
        """
        edge_type='t'
        neighbs=set()
        vids=self.__to_set(vids)
        if n==0 :
            return vids
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
        - `vids` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the 0, 1, ..., nth ancestors of the vertex vid
        """
        return iter(self.ancestors(vids, n))

    def vertex_ids_at_time(self, time_point, only_lineaged = False, as_mother = False, as_daughter = False):
        """
        Return vertices ids corresponding to a given time point in the TPG.
        """
        if as_mother or as_daughter:
            only_lineaged = True
        
        if only_lineaged:
            return [ k for k in self.vertices() if (self.vertex_property('index')[k]==time_point) and
             ( ((self.out_edges(k, 't') != set()) if as_mother else False ) or ( (self.in_edges(k, 't') != set()) if as_daughter else False ) ) ]
        else:
            return [k for k in self.vertices() if self.vertex_property('index')[k]==time_point]


    def vertex_property_with_image_labels(self, vertex_property, image_labels2keep = None, graph_labels2keep = None):
        """
        Return a dictionary extracted from the graph.vertex_property(`vertex_property`) with relabelled keys thanks to the dictionary graph.vertex_property('old_labels').
        
        :Parameters:
        - `vertex_property` : can be an existing 'graph.vertex_property' or a string refering to an existing graph.vertex_property to extract.
        - `image_labels2keep` (int|list) : a list of "image type" labels (i.e. from SpatialImages/PropertyGraphs) to return in the `relabelled_dictionnary`
        - `graph_labels2keep` (int|list) : a list of "graph type" labels (i.e. from SpatialImages/PropertyGraphs) to return in the `relabelled_dictionnary`

        :Returns:
        - a dictionary with relabelled keys to "images labels" (i.e. from SpatialImages/PropertyGraphs), key : vertex/cell label, value : `vertex_property`
        
        :Examples:
        graph.vertex_property_with_image_labels( graph.vertex_property('volume') )
        graph.vertex_property_with_image_labels( 'volume' )
        graph.vertex_property_with_image_labels( 'volume' , SpatialImageAnalysis.L1() )
        
        """
        if isinstance(vertex_property,str):
            vertex_property = self.vertex_property(vertex_property)
        
        if (graph_labels2keep is not None) and (image_labels2keep is not None):
            warnings.warn("You can't specify both image_labels2keep AND graph_labels2keep!")
        
        if (graph_labels2keep is None) and (image_labels2keep is None):
            warnings.warn('You have asked for all labels from the TemporalPropertyGraph to be returned!')
            warnings.warn('Mistakes will be presents in the returned dictionary.')
        
        if (graph_labels2keep is not None):
            return translate_keys_Graph2Image(self, dict( (k,vertex_property[k]) for k in vertex_property if k in graph_labels2keep)) 
        
        if (image_labels2keep is not None):
            return translate_keys_Graph2Image(self, dict( (k,vertex_property[k]) for k in vertex_property if k in translate_ids_Image2Graph(image_labels2keep))) 


