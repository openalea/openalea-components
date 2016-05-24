# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2011 - 2013 INRIA - CIRAD - INRA
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
__revision__ = " $Id$ "

import warnings, numpy as np
from property_graph import *

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
        self.nb_time_points += 1
        for g, m in zip(graphs[1:],mappings):
            self.append(g,m)
            self.nb_time_points += 1

        if time_steps is not None:
            assert len(graphs) == len(time_steps)
            self.add_graph_property('time_steps',time_steps)

        return self._old_to_new_ids


    def append(self, graph, mapping=None):
        """
        Append a (spatial) graph to the tpg structure with respect to a given temporal mapping.
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

        def use_sub_lineage(mother, daughters, on_ids_source, on_ids_target):
            found_sub_lineage=False; tmp_daughters = []
            for d in daughters:
                if iterable(d):
                    found_sub_lineage=True; tmp_d = []
                    if "sub_lineage" not in self.graph_properties():
                        self.add_graph_property("sub_lineage")
                    for sub_d in d:
                        if iterable(sub_d):
                            use_sub_lineage(mother, sub_d, on_ids_source, on_ids_target)
                        else:
                            tmp_d.append(on_ids_target[0][sub_d])
                    tmp_daughters.append(tmp_d)
                else:
                    tmp_daughters.append(on_ids_target[0][d])
            if found_sub_lineage:
                self.graph_property("sub_lineage").update({on_ids_source[0][mother]:tmp_daughters})

        def flatten(l):
            """
            Flatten everything that's a list!
            (i.e. [[1,2],3] -> [1,2,3])
            """
            import collections
            for el in l:
                if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
                    for sub in flatten(el):
                        yield sub
                else:
                    yield el

        if mapping:
            unused_lineage = {}
            on_ids_source, on_ids_target = self._old_to_new_ids[-2:]
            for k, l in mapping.iteritems():
                l_flat = list(flatten(l)) # flatten the lineage (i.e. [[1,2],3] -> [1,2,3])
                # Check if the mother cell and ALL daugthers are present in their respective graph : WE DON'T WANT TO CREATE A PARTIAL LINEAGE !!!!
                if on_ids_source[0].has_key(k) and ( sum([on_ids_target[0].has_key(v) for v in l_flat]) == len(l_flat) ):
                    use_sub_lineage(k, l, on_ids_source, on_ids_target)
                    for v in l_flat:
                        eid = self.add_edge(on_ids_source[0][k], on_ids_target[0][v])
                        edge_types[eid] = self.TEMPORAL
                else:
                    unused_lineage.update({k:l})
            if unused_lineage != {}:
                print "Un-used lineage info to avoid partial lineage, t{} to t{}: {}".format(current_index-1,current_index,unused_lineage)
                print "It is most likely that you are trying to add lineage between non-existant vertex in your spatial graphs!"
                print "Check if you are not using an out-dated graph and erase temporary files (TPG creation...)."
                print "Or maybe the lignage is detected as 'incomplete' because some cells have been removed before topological-graph computation."

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

    def vertex_temporal_index(self, vid):
        """ Return the temporal index of a vid `self.vertex_property('index')[vid]`."""
        if isinstance(vid, list):
            return [self.vertex_temporal_index(v) for v in vid]
        else:
            return self.vertex_property('index')[vid]

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

    def descendants(self, vids, n = None):
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
        elif n==1 :
            for vid in vids:
                neighbs |= (self.out_neighbors(vid, edge_type) | set([vid]))
            return neighbs
        else :
            if n is None :
                n = self.nb_time_points-1
            for vid in vids :
                neighbs |= (self.descendants(self.out_neighbors(vid, edge_type), n-1) | set([vid]))
                if list(neighbs)==self._vertices.keys():
                    return neighbs
        return neighbs

    def iter_descendant(self, vids, n = None):
        """ Return the 0, 1, ..., nth descendants of the vertex vid

        :Parameters:
        - `vids` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the 0, 1, ..., nth descendants of the vertex vid
        """
        return iter(self.descendant(vids, n))

    def rank_descendants(self, vid, rank=1):
        """ Return the descendants of the vertex vid only at a given rank
        :Parameters:
        - `vid` : a vertex id or a set of vertex id
        :Returns:
        - `descendant_list` : the set of the rank-descendant of the vertex vid or a list of set
        """
        if isinstance(vid,list):
            return [self.rank_descendants(v,rank) for v in vid]
        else:
            return self.descendants(vid,rank)- self.descendants(vid,rank-1)

    def has_descendants(self, vid, rank=1):
        """
        Return True if the vid `vid` has at least a descendant at `rank`.
        """
        return self.rank_descendants(vid,rank) != set()

    def ancestors(self, vids, n = None):
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
        elif n==1 :
            for vid in vids:
                neighbs |= (self.in_neighbors(vid, edge_type) | set([vid]))
            return neighbs
        else :
            if n is None:
                n = self.nb_time_points-1
            for vid in vids :
                neighbs |= (self.ancestors(self.in_neighbors(vid, edge_type), n-1) | set([vid]))
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

    def rank_ancestors(self, vid, rank=1):
        """ Return the ancestor of the vertex vid only at a given rank
        :Parameters:
        - `vid` : a vertex id or a set of vertex id
        :Returns:
        - `descendant_list` : the set of the rank-ancestor of the vertex vid or a list of set
        """
        if isinstance(vid,list):
            return [self.rank_ancestors(v,rank) for v in vid]
        else:
            return self.ancestors(vid,rank)- self.ancestors(vid,rank-1)

    def has_ancestors(self, vid, rank=1):
        """
        Return True if the vid `vid` has at least an ancestor at `rank`.
        """
        return self.rank_ancestors(vid,rank) != set()


    def _lineaged_as_ancestor(self, time_point=None, rank=1):
        """ Return a list of vertex lineaged as ancestors."""
        if time_point is None:
            return [k for k in self.vertices() if self.has_descendants(k,rank)]
        else:
            return [k for k,v in self.vertex_property('index').iteritems() if v==time_point and self.has_descendants(k,rank)]

    def _lineaged_as_descendant(self, time_point=None, rank=1):
        """ Return a list of vertex lineaged as descendants."""
        if time_point is None:
            return [k for k in self.vertices() if self.has_ancestors(k,rank)]
        else:
            return [k for k,v in self.vertex_property('index').iteritems() if v==time_point and self.has_ancestors(k,rank)]

    def _fully_lineaged_vertex(self, time_point=None):
        """
        Return a list of fully lineaged vertex (from a given `time_point` if not None), i.e. lineaged from start to end.
        """
        from vplants.tissue_analysis.temporal_graph_analysis import exist_all_relative_at_rank
        rank = self.nb_time_points-1
        flv = self.descendants([k for k in self.vertex_at_time(0) if exist_all_relative_at_rank(self, k, rank)], rank)
        if time_point is None:
            return flv
        else:
            return [vid for vid in flv if self.vertex_temporal_index(vid)==time_point]

    def lineaged_vertex(self, fully_lineaged=False, as_ancestor=False, as_descendant=False, lineage_rank=1):
        """
        Return ids of lineaged vertices, with differents type of lineage possible:
         - a full lineage, i.e. only vids with a lineage from the first to the last time-point (fully_lineaged=True);
         - a lineage over several ranks, i.e. only vids with a lineage from the vid to the vid+lineage_rank time-point (fully_lineaged=False, lineage_rank=int);
         - an 'ancestors' based lineage (as_ancestor = True), i.e. only vids lineaged as ancestor (over lineage_rank if not None);
         - an 'descendants' based lineage (as_ancestor = True), i.e. only vids lineaged as descendants (over lineage_rank if not None).

        :Parameter:
         - `fully_lineaged` (bool) : if True (and lineage_rank is None), return vertices lineaged from the first to the last time-point (or from vid_time_point to vid_time_point + lineage_rank), otherwise return vertices having at least a parent or a child(ren);
         - `as_parent` (bool) : if True, return vertices lineaged as parents;
         - `as_children` (bool) : if True, return vertices lineaged as children;
         - 'lineage_rank' (int): usefull if you want to check the lineage for a different rank than the rank-1 temporal neighborhood.
        """
        from vplants.tissue_analysis.temporal_graph_analysis import exist_all_relative_at_rank
        if as_ancestor:
            vids_anc = self._lineaged_as_ancestor(time_point=None, rank=lineage_rank)
        else:
            vids_anc = self.vertices()
        if as_descendant:
            vids_desc = self._lineaged_as_descendant(time_point=None, rank=lineage_rank)
        else:
            vids_desc = self.vertices()

        if fully_lineaged:
            vids = self._fully_lineaged_vertex(time_point=None)
        else:
            vids = [k for k in self.vertices() if (exist_all_relative_at_rank(self, k, lineage_rank) or exist_all_relative_at_rank(self, k, -lineage_rank))]
        return list( set(vids) & set(vids_anc) & set(vids_desc) )


    def _all_vertex_at_time(self, time_point):
        """ Return a list containing all vertex assigned to a given `time_point`."""
        return [k for k,v in self.vertex_property('index').iteritems() if v==time_point]

    def vertex_at_time(self, time_point, lineaged=False, fully_lineaged=False, as_ancestor=False, as_descendant=False, lineage_rank=1):
        """
        Return vertices ids corresponding to a given time point in the TPG.
        Optional parameters can be used to filter the list of vertices ids returned.

        :Parameters:
         - `time_point` (int) : integer giving which time point should be considered;
         - `lineaged` (bool) : if True, return vertices having at least a parent or a child(ren);
         - 'lineage_rank' (int): usefull if you want to check the lineage for a different rank than the rank-1 temporal neighborhood;
         - `fully_lineaged` (bool) : if True, return vertices linked from the beginning to the end of the graph;
         - `as_parent` (bool) : if True, return vertices lineaged as parents;
         - `as_children` (bool) : if True, return vertices lineaged as children.
        """
        if lineaged or fully_lineaged:
            vids = self.lineaged_vertex(fully_lineaged, as_ancestor, as_descendant, lineage_rank)
            return list(set(vids) & set(self._all_vertex_at_time(time_point)))
        else:
            return self._all_vertex_at_time(time_point)


    def vertex_property_at_time(self, vertex_property, time_point, lineaged=False, fully_lineaged=False, as_ancestor=False, as_descendant=False, lineage_rank=1):
        """
        Return the `vertex_property``for a given `time_point`.
        May be conditionned by extra temporal property: `lineaged`, `fully_lineaged`, `as_parent`, `as_children`.

        :Parameters:
         - `vertex_property` (str): a string refering to an existing 'graph.vertex_property' to extract;
         - `time_point` (int) : integer giving which time point should be considered;
         - `lineaged` (bool) : if True, return vertices having at least a parent or a child(ren);
         - 'lineage_rank' (int): usefull if you want to check the lineage for a different rank than the rank-1 temporal neighborhood;
         - `fully_lineaged` (bool) : if True, return vertices linked from the beginning to the end of the graph;
         - `as_parent` (bool) : if True, return vertices lineaged as parents;
         - `as_children` (bool) : if True, return vertices lineaged as children.
        """
        vids = self.vertex_at_time(time_point, lineaged, fully_lineaged, as_ancestor, as_descendant)
        return dict([(k,self.vertex_property(vertex_property)[k]) for k in vids if self.vertex_property(vertex_property).has_key(k)])


    def vertex_property_with_image_labels(self, vertex_property, time_point, lineaged=False, fully_lineaged=False, as_ancestor=False, as_descendant=False, lineage_rank=1):
        """
        Return a subpart of graph.vertex_property(`vertex_property`) with relabelled keys into "images labels" thanks to the dictionary graph.vertex_property('old_labels').
        Since "images labels" can be similar (not unique), it is mandatory to give a `time_point`.
        Additional parameters can be given and are related to the 'self.vertex_property_at_time' parameters.

        :Parameters:
         - `vertex_property` (str): a string refering to an existing 'graph.vertex_property' to extract;
         - `time_point` (int): time-point for which to return the `vertex_property`;
         - `lineaged` (bool) : if True, return vertices having at least a parent or a child(ren);
         - 'lineage_rank' (int): usefull if you want to check the lineage for a different rank than the rank-1 temporal neighborhood;
         - `fully_lineaged` (bool) : if True, return vertices linked from the beginning to the end of the graph;
         - `as_parent` (bool) : if True, return vertices lineaged as parents;
         - `as_children` (bool) : if True, return vertices lineaged as children.
        :Returns:
         - *key_ vertex/cell label, *values_ `vertex_property`

        :Examples:
         graph.vertex_property_with_image_labels('volume', 0)

        """
        from vplants.tissue_analysis.temporal_graph_analysis import translate_keys_Graph2Image
        return translate_keys_Graph2Image(self, self.vertex_property_at_time(vertex_property, time_point, lineaged, fully_lineaged, as_ancestor, as_descendant))


    def edge_property_at_time(self, edge_property, time_point):
        """
        Return a subpart of graph.edge_property(`edge_property`) with relabelled key-pair into "images labelpairs" thanks to the dictionary graph.vertex_property('old_labels').

        :Parameters:
         - `vertex_property` (str): a string refering to an existing 'graph.edge_property' to extract;
         - `time_point` (int): time-point for which to return the `edge_property`;

        :Examples:
         graph.edge_property_with_image_labelpairs('wall_area', 0)
        """
        from vplants.tissue_analysis.temporal_graph_from_image import edge2vertexpair_map
        eid2vidpair = edge2vertexpair_map(self, time_point)
        #~ return dict([(tuple(sorted([label1,label2])),self.edge_property(edge_property)[eid]) for eid,(label1,label2) in eid2vidpair.iteritems() if self.edge_property(edge_property).has_key(eid)])
        tmp_dict = {}
        for eid,(label1,label2) in eid2vidpair.iteritems():
            if self.edge_property(edge_property).has_key(eid):
                tmp_dict[tuple(sorted([label1,label2]))] = self.edge_property(edge_property)[eid]

        return tmp_dict


    def edge_property_with_image_labelpairs(self, edge_property, time_point):
        """
        Return a subpart of graph.edge_property(`edge_property`) with relabelled key-pair into "images labelpairs" thanks to the dictionary graph.vertex_property('old_labels').

        :Parameters:
         - `vertex_property` (str): a string refering to an existing 'graph.edge_property' to extract;
         - `time_point` (int): time-point for which to return the `edge_property`;

        :Examples:
         graph.edge_property_with_image_labelpairs('wall_area', 0)
        """
        from vplants.tissue_analysis.temporal_graph_from_image import edge2labelpair_map
        eid2labelpair = edge2labelpair_map(self, time_point)
        return dict([(tuple(sorted([label1,label2])),self.edge_property(edge_property)[eid]) for eid,(label1,label2) in eid2labelpair.iteritems() if self.edge_property(edge_property).has_key(eid)])


    def region_vids(self, region_name):
        """
        Return a list of vids (TPG vertex id type) that belong to the region `region_name` according to graph.
        :Parameters:
         - `region_name` (str) : the nama of a previously defined region via `self.add_vertex_to_region()`
        """
        if 'regions' in list(self.vertex_properties()):
            return sorted(list(set([k for k,v in self.vertex_property('regions').iteritems() for r in v if r==region_name])))
        else:
            print "No property 'regions' added to the graph yet!"
            return None


def iterable(obj):
    try :
        iter(obj)
        return True
    except TypeError,te:
        return False
