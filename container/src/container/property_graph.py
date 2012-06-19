# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Fred Theveny <frederic.theveny@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
################################################################################
"""This module provide a set of concepts to add properties to graph elements"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from interface.property_graph import IPropertyGraph, PropertyError
from graph import Graph, InvalidVertex, InvalidEdge

VertexProperty, EdgeProperty, GraphProperty = range(3)
VertexIdType, EdgeIdType, ValueType = range(3)

class PropertyGraph(IPropertyGraph, Graph):
    """
    Simple implementation of IPropertyGraph using
    dict as properties and two dictionaries to
    maintain these properties
    """
    metavidtypepropertyname = "valueproperty_as_vid"
    metaeidtypepropertyname = "valueproperty_as_eid"
    
    def __init__(self, graph=None, **kwds):
        self._vertex_property = {}
        self._edge_property = {}
        self._graph_property = {}
        Graph.__init__(self, graph, **kwds)

    def vertex_property_names(self):
        """todo"""
        return self._vertex_property.iterkeys()
    vertex_property_names.__doc__ = IPropertyGraph.vertex_property_names.__doc__

    def vertex_properties(self):
        """todo"""
        return self._vertex_property
    # vertex_properties.__doc__ = IPropertyGraph.vertex_properties.__doc__

    def vertex_property(self, property_name):
        """todo"""
        try:
            return self._vertex_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on vertices"
                                % property_name)
    vertex_property.__doc__=IPropertyGraph.vertex_property.__doc__

    def edge_property_names(self):
        """todo"""
        return self._edge_property.iterkeys()
    edge_property_names.__doc__ = IPropertyGraph.edge_property_names.__doc__

    def edge_properties(self):
        """todo"""
        return self._edge_property
    #  edge_properties.__doc__ = IPropertyGraph. edge_properties.__doc__

    def edge_property(self, property_name):
        """todo"""
        try:
            return self._edge_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on edges"
                                % property_name)
    edge_property.__doc__ = IPropertyGraph.edge_property.__doc__

    def graph_property(self, property_name):
        """todo"""
        try:
            return self._graph_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on graph"
                                % property_name)
    graph_property.__doc__ = IPropertyGraph.graph_property.__doc__
                                
    def graph_properties(self):
        return self._graph_property
    
    
    def graph_property_names(self):
        """todo"""
        return self._graph_property.iterkeys()

    def add_vertex_property(self, property_name, values = None):
        """todo"""
        if property_name in self._vertex_property:
            raise PropertyError("property %s is already defined on vertices"
                                % property_name)
        if values is None: values = {}                                
        self._vertex_property[property_name] = values
    add_vertex_property.__doc__ = IPropertyGraph.add_vertex_property.__doc__

    def remove_vertex_property(self, property_name):
        """todo"""
        try:
            del self._vertex_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on vertices"
                                % property_name)
    remove_vertex_property.__doc__ = IPropertyGraph.remove_vertex_property.__doc__

    def add_edge_property(self, property_name, values =  None):
        """todo"""
        if property_name in self._edge_property:
            raise PropertyError("property %s is already defined on edges"
                                % property_name)
        if values is None: values = {}                                
        self._edge_property[property_name] = values
    add_edge_property.__doc__ = IPropertyGraph.add_edge_property.__doc__

    def remove_edge_property(self, property_name):
        """todo"""
        try:
            del self._edge_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on edges"
                                % property_name)
    remove_edge_property.__doc__ = IPropertyGraph.remove_edge_property.__doc__

    def add_graph_property(self, property_name, values = None):
        """todo"""
        if property_name in self._graph_property:
            raise PropertyError("property %s is already defined on graph"
                                % property_name)
        if values is None: values = {}
        self._graph_property[property_name] = values

    def remove_graph_property(self, property_name):
        """todo"""
        try:
            del self._graph_property[property_name]
        except KeyError:
            raise PropertyError("property %s is undefined on graph"
                                % property_name)

    def remove_vertex(self, vid):
        """todo"""
        for prop in self._vertex_property.itervalues():
            prop.pop(vid, None)
        Graph.remove_vertex(self, vid)
    remove_vertex.__doc__ = Graph.remove_vertex.__doc__

    def clear(self):
        """todo"""
        for prop in self._vertex_property.itervalues():
            prop.clear()
        for prop in self._edge_property.itervalues():
            prop.clear()
        for prop in self._graph_property.itervalues():
            prop.clear()
        Graph.clear(self)
    clear.__doc__ = Graph.clear.__doc__

    def remove_edge(self, eid):
        """todo"""
        for prop in self._edge_property.itervalues():
            prop.pop(eid, None)
        Graph.remove_edge(self, eid)
    remove_edge.__doc__ = Graph.remove_edge.__doc__

    def clear_edges(self):
        """todo"""
        for prop in self._edge_property.itervalues():
            prop.clear()
        Graph.clear_edges(self)
    clear_edges.__doc__ = Graph.clear_edges.__doc__

    @staticmethod
    def _translate_property(values, trans_vid, trans_eid, key_translation = ValueType, value_translation = ValueType):
        # translation function
        from copy import deepcopy
        
        id_value = lambda value: value
        
        trans_vid = deepcopy(trans_vid)
        trans_vid[None] = None
        def translate_vid(vid): 
            if isinstance(vid, list): return [trans_vid[i]  for i in vid]
            if isinstance(vid, tuple): return tuple([trans_vid[i]  for i in vid])
            return trans_vid[vid]
        
        trans_eid = deepcopy(trans_eid)
        trans_eid[None] = None
        def translate_eid(eid):
            if isinstance(eid, list): return [trans_eid[i]  for i in eid]
            if isinstance(eid, tuple): return tuple([trans_eid[i]  for i in eid])
            return trans_eid[eid]

        translator = { ValueType : id_value, VertexIdType :  translate_vid, EdgeIdType : translate_eid }

        key_translator = translator[key_translation]
        value_translator = translator[value_translation]

        # translate vid and value
        return dict([(key_translator(vid),value_translator(val)) for vid, val in values.iteritems()])


    def _relabel_and_add_vertex_edge_properties(self,graph, trans_vid, trans_eid):
        
        # update properties on vertices
        for prop_name in graph.vertex_property_names():
            if prop_name not in self._vertex_property:
                self.add_vertex_property(prop_name)
            value_translator = graph.get_property_value_type(prop_name,VertexProperty)

            # import property into self. translate vid and value
            self.vertex_property(prop_name).update(self._translate_property(graph.vertex_property(prop_name), trans_vid, trans_eid, VertexIdType, value_translator))

        # update properties on edges
        for prop_name in graph.edge_property_names():
            if prop_name not in self._edge_property:
                self.add_edge_property(prop_name)
            
            # Check what type of translation is required for value of the property
            value_translator = graph.get_property_value_type(prop_name,EdgeProperty)
            
            # import property into self. translate vid and value
            self.edge_property(prop_name).update(self._translate_property(graph.edge_property(prop_name), trans_vid, trans_eid, EdgeIdType, value_translator))

    def translate_graph_property(self, prop_name, trans_vid, trans_eid):
        """ Translate a graph property according to meta info """
        old_prop = self.graph_property(prop_name)
        
        key_translator = self.get_graph_property_key_type(prop_name)
        value_translator = self.get_property_value_type(prop_name, GraphProperty)
        print 'translate_graph_property',prop_name, key_translator, value_translator
        
        return self._translate_property(old_prop, trans_vid, trans_eid, key_translator, value_translator)
    
    
    def extend(self, graph):
        """todo"""
        
        # add and translate the vertex and edge ids of the second graph
        trans_vid, trans_eid = Graph.extend(self,graph)
        
        # relabel the edge and vertex property
        self.__relabel_and_add_vertex_edge_properties(graph, trans_vid, trans_eid)
        
        # update properties on graph
        gproperties = self.graph_property()
        newgproperties = {}
        for pname, prop in graph.graph_property_names():
            newgproperty = graph.translate_graph_property(pname,trans_vid, trans_eid)
            newgproperties[pname] = newgproperty
            
        prop.update(newgproperties)

        return trans_vid, trans_eid
        
    extend.__doc__ = Graph.extend.__doc__
    
    
    def set_property_value_to_vid_type(self, propertyname, property_type = VertexProperty):
        """ Give meta info on property value type. Associate it to Vertex Id type """
        if not self._graph_property.has_key(self.metavidtypepropertyname):
            self.add_graph_property(self.metavidtypepropertyname,([],[],[],[]))
        prop = self.graph_property(self.metavidtypepropertyname)[property_type]
        prop.append(propertyname)
    
    def set_property_value_to_eid_type(self, propertyname,  property_type = VertexProperty):
        """ Give meta info on property value type. Associate it to Edge Id type """
        if not self._graph_property.has_key(self.metaeidtypepropertyname):
            self.add_graph_property(self.metaeidtypepropertyname,([],[],[],[]))
        prop = self.graph_property(self.metaeidtypepropertyname)[property_type]
        prop.append(propertyname)
        
    def set_graph_property_key_to_vid_type(self, propertyname):
        """ Give meta info on graph property key type. Associate it to Vertex Id type"""
        self.set_property_value_to_vid_type(propertyname, 3)
    
    def set_graph_property_key_to_eid_type(self, propertyname):
        """ Give meta info on graph property key type.  Associate it to Edge Id type """
        self.set_property_value_to_eid_type(propertyname, 3)
    
    def get_property_value_type(self, propertyname, property_type = VertexProperty):
        """ Return meta info on property value type. Associate it to Edge Id type """
        try:
            prop = self.graph_property(self.metavidtypepropertyname)[property_type]
            if propertyname in prop : return VertexIdType
        except:
            pass
        try:
            prop = self.graph_property(self.metaeidtypepropertyname)[property_type]
            if propertyname in prop : return EdgeIdType
        except:
            return ValueType
    
    def get_graph_property_key_type(self, propertyname):
        """ Return meta info on graph property key type. Associate it to Vertex Id type"""
        return self.get_property_value_type(propertyname, 3)
    
    
    
    def __to_set(self, s):
        if not isinstance(s, set):
            if isinstance(s, list):
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
            neighbors_list=set([self.source(eid) for eid in self._vertices[vid][0] ])
        else:
            edge_type=self.__to_set(edge_type) 
            edge_type_property = self._edge_property['edge_type']
            neighbors_list=set([self.source(eid) for eid in self._vertices[vid][0] if edge_type_property[eid] in edge_type])
        return neighbors_list
  
    def iter_in_neighbors(self, vid, edge_type=None):
        """ Return the in vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterator` : an iterator on the set of parent vertices of the vertex vid
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
            neighbors_list=set([self.target(eid) for eid in self._vertices[vid][1] ])
        else:
            edge_type=self.__to_set(edge_type) 
            edge_type_property = self._edge_property['edge_type']
            neighbors_list=set([self.target(eid) for eid in self._vertices[vid][1] if edge_type_property[eid] in edge_type])
        return neighbors_list
        
                    
    def iter_out_neighbors(self, vid, edge_type=None):
        """ Return the out vertices of the vertex vid
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider (can be a set)

        :Returns:
        - `iterator` : an iterator on the set of child vertices of the vertex vid
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

        if not edge_type:
            edge_list=set([eid for eid in self._vertices[vid][0]])
        else:
            edge_type=self.__to_set(edge_type)
            edge_type_property = self._edge_property['edge_type']
            edge_list=set([eid for eid in self._vertices[vid][0] if edge_type_property[eid] in edge_type])
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
        
        if edge_type==None:
            edge_list=set([eid for eid in self._vertices[vid][1]])
        else:
            edge_type=self.__to_set(edge_type)
            edge_type_property = self._edge_property['edge_type']
            edge_list=set([eid for eid in self._vertices[vid][1] if edge_type_property[eid] in edge_type])
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
        if vid==None:
            return set(self._edges.keys())       
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

    def neighborhood(self, vid, max_distance=1, edge_type=None):
        """ Return the neighborhood of the vertex vid at distance max_distance (the disc, not the circle)
        
        :Parameters:
        - `vid` : vertex id

        :Returns:
        - `neighbors_list` : the set of the vertices at distance below max_distance of the vertex vid (including vid)
        """
        dist=self.topological_distance(vid, edge_type=edge_type, max_depth=max_distance, full_dict=False)
        return set(dist.keys())

    def iter_neighborhood(self, vid, n, edge_type=None):
        """ Return the neighborhood of the vertex vid at distance n (the disc, not the circle)
        
        :Parameters:
        - `vids` : a set of vertex id

        :Returns:
        - `iterator` : an iterator on the set of the vertices at distance n of the vertex vid
        """
        return iter(self.neighborhood(vid, n, edge_type))      

    def topological_distance(self, vid, edge_type = None, edge_dist = lambda x,y : 1, max_depth=float('inf'), full_dict=True):
        """ Return the distances of each vertices at the vertex vid according a cost function
        
        :Parameters:
        - `vid` : a vertex id
        - `edges_type` : type of edges we want to consider
        - `edge_dist` : the cost function
        - `max_depth` : the maximum depth that we want to reach
        - `full_dict` : if True this function will return the entire dictionary (with inf values)

        :Returns:
        - `dist_dict` : a dictionary of the distances, key : vid, value : distance
        """
        import numpy as np
        dist={}
        reduced_dist={}
        reduced_dist[vid]=0
        untreated=set()
        infinity = float('inf')
        for k in self._vertices.iterkeys():
            dist[k] = infinity
            untreated.add(k)

        treated=set()
        dist[vid]=0
        modif=True
        
        while (len(untreated)>0 & modif):
            tmpDist=dist.copy()
            for k in treated:
                tmpDist.pop(k)
            actualVid=[k for k in tmpDist.keys()][np.argmin(tmpDist.values())]
            untreated-=set([actualVid])
            treated|=set([actualVid])
            for neighb in self.iter_neighbors(actualVid, edge_type):
                if ((dist[neighb] > dist[actualVid] + edge_dist(neighb, actualVid))
                    & (dist[actualVid] + edge_dist(neighb, actualVid) < max_depth+1 ) ):
                    dist[neighb]=dist[actualVid] + edge_dist(neighb, actualVid)
                    reduced_dist[neighb]=dist[actualVid] + edge_dist(neighb, actualVid)
            modif=tmpDist!=dist
        return (reduced_dist, dist)[full_dict]


    def _add_vertex_to_region(self, vids, region_name):
        """
        add a set of vertices to a region
        """
        for vid in vids:
            if self._vertex_property["regions"].has_key(vid):
                self._vertex_property["regions"][vid].append(region_name)
            else:
                self._vertex_property["regions"][vid]=[region_name]

            self._graph_property[region_name].append(vid)

    def _remove_vertex_from_region(self, vids, region_name):
        """
        remove a set of vertices to a region
        """
        for vid in vids:
            self._vertex_property["regions"][vid].remove(region_name)
            if self._vertex_property["regions"][vid]==[]:
                self._vertex_property["regions"].pop(vid)
                
            self._graph_property[region_name].remove(vid)
        

    def add_vertex_to_region(self, vids, region_name):
        """
        add a set of vertices to a region
        """
        if not region_name in self._graph_property:
            raise PropertyError("property %s is not defined on graph"
                                % region_name)
        
        self._add_vertex_to_region(self.__to_set(vids), region_name)

    def remove_vertex_from_region(self, vids, region_name):
        """
        remove a set of vertices to a region
        """
        if not region_name in self._graph_property:
            raise PropertyError("property %s is not defined on graph"
                                % region_name)
        self._remove_vertex_from_region(self.__to_set(vids), region_name)


    def add_region(self, func, region_name):
        """ Create a region of vertices according a function
        
        :Parameters:
        - `func` : the function to make the region (might return True or False)
        - `region_name` : the name of the region
        
        """
        
        if region_name in self._graph_property:
            raise PropertyError("property %s is already defined on graph"
                                % region_name)
        self._graph_property[region_name]=[]
        if not "regions" in self._vertex_property.keys():
            self.add_vertex_property("regions")
        for vid in self._vertices.keys():
            if func(self, vid):
                self._add_vertex_to_region(set([vid]), region_name)


    def iter_region(self, region_name):
        if not region_name in self._graph_property:
            raise PropertyError("property %s is not defined on graph"
                                % region_name)
        return iter(self._graph_property[region_name])

    def remove_region(self, region_name):
        """ Remove a region 
        
        :Parameters:
        - `region_name` : the name of the region
        
        """
        if not region_name in self._graph_property:
            raise PropertyError("property %s is not defined on graph"
                                % region_name)

        for vid in self.iter_region(region_name):
            self._vertex_property["regions"][vid].remove(region_name)
            if self._vertex_property["regions"][vid]==[]:
                self._vertex_property["regions"].pop(vid)

        return self._graph_property.pop(region_name)

    def is_connected_region(self, region_name, edge_type=None):
        """
        Return True if a region is connected
        """
        if not region_name in self._graph_property:
            raise PropertyError("property %s is not defined on graph"
                                % region_name)
        region_sub_graph=Graph.sub_graph(self, self._graph_property[region_name])
        distances=region_sub_graph.topological_distance(region_sub_graph._vertices.keys()[0], edge_type=edge_type)
        return not float('inf') in distances.values()
