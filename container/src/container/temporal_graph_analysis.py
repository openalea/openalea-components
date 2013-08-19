# -*- python -
#
#       OpenAlea.Container
#
#       Copyright 2012 INRIA - CIRAD - INRA
#
#       File author(s):  Jonathan Legrand <jonathan.legrand@ens-lyon.fr>
#                        Frederic Boudon <frederic.boudon@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
################################################################################
"""This module helps to analyse TemporalPropertyGraph from Spatial Images."""

import warnings
import types
import numpy as np
import copy
from interface.property_graph import IPropertyGraph, PropertyError
import matplotlib.pyplot as plt

from scipy.sparse import csr_matrix
from numpy.linalg import svd, lstsq


def add_graph_vertex_property_from_dictionary(graph, name, dictionary):
    """ 
    Add a vertex property with name 'name' to the graph build from an image. 
    The values of the property are given as by a dictionary where keys are TemporalPropertyGraph vertex labels. 
    """
    if name in graph.vertex_properties():
        raise ValueError('Existing vertex property %s' % name)

    graph.add_vertex_property(name)
    graph.vertex_property(name).update( dictionary )


def keys_to_mother_id(graph, data, rank = 1):
    """
    Translate a dict with daughter ids as key, to a dict with mother ids as keys.
    :Parameters:
     - 'graph' (TPG): the TPG to be used for translation
     - 'data' (dict): the dictionary to translate
    """
    translated_dict = {}
    for vid in data.keys():
        if exist_relative_at_rank(graph,vid,-rank):
            mother = list(graph.ancestors(vid,rank)-graph.ancestors(vid,rank-1))[0]
            if not translated_dict.has_key(mother):
                translated_dict[mother] = data[vid]

    return translated_dict


def keys_to_daughter_id(graph, data, rank = 1):
    """
    Translate a dict with mother ids as key, to a dict with daughter ids as keys.
    :Parameters:
     - 'graph' (TPG): the TPG to be used for translation
     - 'data' (dict): the dictionary to translate
    """
    translated_dict = {}
    for vid in data.keys():
        if exist_relative_at_rank(graph,vid,rank):
            daughter = list(graph.descendants(vid,rank)-graph.descendants(vid,rank-1))
            for d in daughter:
                translated_dict[d] = data[vid]

    return translated_dict


def translate_ids_Graph2Image(graph, id_list):
    """
    Return a list which contains SpatialImage ids type translated from the TPG ids type `id_list`.
    
    :Parameters:
     - `graph` (TPG): the TemporalPropertyGraph containing the translation informations
     - `id_list` (list) - graphs ids type
    """
    if isinstance(id_list,int):
        return graph.vertex_property('old_label')[id_list]
    
    if not isinstance(id_list,list):
        raise ValueError('This is not an "int" or a "list" type variable.')

    return [graph.vertex_property('old_label')[k] for k in id_list]

def translate_ids_Image2Graph(graph, id_list, time_point):
    """
    Return a list which contains TPG ids type translated from the SpatialImage ids type `id_list`.
    
    :Parameters:
     - `graph` (TPG): the TemporalPropertyGraph containing the translation informations
     - `id_list` (list) - SpatialImage ids type
     - `time_point` (int) - index of the SpatialImage in the TemporalPropertyGraph
    
    :WARNING:
        `time_point` numbers starts at '0'
    """
    if (not isinstance(id_list,list)) and (not isinstance(id_list,int)):
        raise ValueError('This is not an "int" or a "list" type variable.')

    graph_labels_at_time_point = graph.vertex_ids_at_time(time_point)
    Image2Graph_labels_at_time_point = dict( (v,k) for k,v in graph.vertex_property('old_label').iteritems() if k in graph_labels_at_time_point )

    if isinstance(id_list,int):
        if id_list in Image2Graph_labels_at_time_point:
            return Image2Graph_labels_at_time_point[id_list]
        else:
            print 'Label {0} is not in the graph at t{1}'.format(id_list,time_point+1)
            return []

    Image2Graph_labels, Image_labels_not_found = [], []
    for k in id_list:
        if k in Image2Graph_labels_at_time_point.keys():
            Image2Graph_labels.append(Image2Graph_labels_at_time_point[k])
        else:
            Image_labels_not_found.append(k)

    if Image_labels_not_found != []:
        warnings.warn("The cell ids"+str(Image_labels_not_found)+"were not in the graph!")


    return Image2Graph_labels

def translate_keys_Graph2Image(graph, dictionary, time_point=None):
    """
    Return a dictionary which keys are SpatialImage ids type .
    Initial keys are graph ids type and need to be translated into SpatialImage ids type.
    
    :Parameters:
    - `dictionary` (dict) - keys are SpatialImage ids type;
    - `time_point` (int) - index of the SpatialImage in the TemporalPropertyGraph;
    
    :WARNING:
        `time_point` numbers starts at '0'
    """
    if not isinstance(dictionary,dict):
        raise ValueError('This is not a "dict" type variable.')

    translated_dict = {}
    if time_point is None:
        for k in dictionary:
            if not dictionary.has_key(k):
                translated_dict[graph.vertex_property('old_label')[k]] = dictionary[k]
            else:
                raise KeyError("The dictionary you want to translate contain label from more than one time point, found redundant keys!")

        return translated_dict
    else:
        return dict( (graph.vertex_property('old_label')[k], dictionary[k]) for k in dictionary if graph.vertex_property('index')[k] == time_point )

def translate_keys_Image2Graph(graph, dictionary, time_point):
    """
    Return a dictionary which keys are graph ids type .
    Initial keys are SpatialImage ids type and need to be translated into graph ids type.
    
    :Parameters:
    - `dictionary` (dict) - keys are graph ids type;
    - `time_point` (int) - index of the SpatialImage in the TemporalPropertyGraph;
    
    :WARNING:
        `time_point` numbers starts at '0'
    """
    if not isinstance(dictionary,dict):
        raise ValueError('This is not a "dict" type variable.')
    
    return dict( (k,dictionary[v]) for k,v in graph.vertex_property('old_label').iteritems() if (graph.vertex_property('index')[k] == time_point) and (v in dictionary) )


def __normalized_parameters(func):
    def wrapped_function(graph, vertex_property, vids = None, rank = 1 , verbose = False):
        """
        :Parameters:
        - 'graph' : a TPG.
        - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
        - 'vids' : by default a vertex id or a list of vertex ids. If 'vids=None' the mean absolute deviation will be computed for all ids present in the graph provided.
        - 'rank' : neighborhood at distance 'rank' will be used.

        :Return:
        - a single value if vids is an interger, or a dictionnary of *keys=vids and *values= "result of applyed fucntion `func`"
        """
        # if a name is given, we use vertex_property stored in the graph with this name.
        if isinstance(vertex_property,str):
            vertex_property = graph.vertex_property(vertex_property)

        # -- If no vids provided we compute the function for all keys present in the vertex_property
        if vids==None:
            vids = vertex_property.keys()

        # if an instancemethod is given, we use create a dictionary for the vids base ont the method.
        if isinstance(vertex_property,types.MethodType):
            tmp_vertex_property = {}
            for vid in graph.vertices():
                tmp_vertex_property[vid] = vertex_property(vid)
            vertex_property = tmp_vertex_property

        if type(vids)==int:
            # for single id, compute single result
            return func(graph, vertex_property, vids, rank)
        else:
            # for set of ids, we compute a dictionary of resulting values.
            l={}
            for k in vids:
                if verbose and k%10==0: print k,'/',len(vids)
                l[k] = func(graph, vertex_property, k, rank, edge_type='s')
            return l

    return  wrapped_function


@__normalized_parameters
def laplacian(graph, vertex_property, vid, rank, edge_type):
    """
    Sub-function computing the laplacian between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.

    :Return:
    - a single value = laplacian between vertex 'vid' and its neighbors at rank 'rank'.
    """
    if rank == 1:
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)
        vid_neighborhood.remove(vid)
    else: # if rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)-graph.neighborhood(vid,rank-1, edge_type)

    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + vertex_property[i]
        return ivalue - (result / float(nb_neighborhood))

@__normalized_parameters
def mean_abs_dev(graph, vertex_property, vid, rank, edge_type):
    """
    Sub-function computing the mean sum of absolute difference between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.

    :Return:
    - a single value = the mean absolute deviation between vertex 'vid' and its neighbors at rank 'rank'.
    """
    if rank == 1:
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)
        vid_neighborhood.remove(vid)
    else: # if rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)-graph.neighborhood(vid,rank-1, edge_type)

    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + abs(ivalue - vertex_property[i])
        return result / float(nb_neighborhood)


@__normalized_parameters
def change(graph, vertex_property, vid, rank, edge_type):
    """
    Sub-function computing the difference between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.

    :Return:
    - a single value = laplacian between vertex 'vid' and its neighbors at rank 'rank'.
    """
    if rank == 1:
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)
        vid_neighborhood.remove(vid)
    else: # if rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
        vid_neighborhood = graph.neighborhood(vid,rank, edge_type)-graph.neighborhood(vid,rank-1, edge_type)

    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + vertex_property[i]
        return result/float(nb_neighborhood) - ivalue


def __normalized_temporal_parameters(func):
    def wrapped_function(graph, vertex_property, vids = None, rank = 1, labels_at_t_n = False, check_exist_all_relative_at_rank = True, rank_lineage_check = None, verbose = False):
        """
        :Parameters:
        - 'graph' : a TPG.
        - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
        - 'vids' : by default a vertex id or a list of vertex ids. If 'vids=None' the function `func` will be computed for all ids present in the graph provided.
        - 'rank' : temporal neighborhood at distance 'rank' will be used.
        - 'rank_lineage_check' : usefull if you want to check the lineage for a different rank than the temporal neighborhood rank.
        
        :Example:
        VG12 = g.translate_keys_Graph2Image(relative_temporal_change(g, 'volume', rank = 1, rank_lineage_check = 4), 0 )
        VG15 = g.translate_keys_Graph2Image(relative_temporal_change(g, 'volume', rank = 4, rank_lineage_check = 4), 0 )
        This make sure that the same lineage is used for volumetric growth computation between t1-t2 and t1-t5.

        :Return:
        - a single value if vids is an interger, or a dictionnary of *keys=vids and *values= value computed by `func`
        """
        # -- If a name is given, we use vertex_property stored in the graph with this name.
        if isinstance(vertex_property,str):
            vertex_property = graph.vertex_property(vertex_property)

        # -- If no vids provided we compute the function for all keys present in the vertex_property
        no_warn = False
        if vids==None:
            vids = vertex_property.keys()
            no_warn = True
        if isinstance(vids,int):
            vids=[vids] # for single id, compute single result

        if rank<0:
            if not labels_at_t_n:
                rank = -rank
            else:
                raise ValueError("Rank should be positive if you want labels @t_n.")
        if rank_lineage_check == None:
            rank_lineage_check = rank

        try:
            graph.graph_property('time_steps')
        except:
            warnings.warn("You did not defined the `time_steps` when creating the TemporalPropertyGraph.")
            raise ValueError("Use graph.add_graph_property('time_steps',time_steps) to add it.")

        # -- For a list of ids, we create a dictionary of resulting values from temporal function `func`.
        temporal_func={}
        for n,vid in enumerate(vids):
            if verbose and n%10==0: print n,'/',len(vids)
            # -- We compute the `time_interval` each time in case `vids` have differents indexes:
            index_1 = graph.vertex_property('index')[vid]
            try:
                time_interval = graph.graph_property('time_steps')[index_1+rank]-graph.graph_property('time_steps')[index_1]
            except:
                continue #will go to the next `vid` if its 'index_1+rank' is out of range!
            if check_exist_all_relative_at_rank:
                if exist_all_relative_at_rank(graph, vid, rank_lineage_check): # Check if ALL descendants up to `rank_lineage_check` exists !
                    temporal_func[vid] = func(graph, vertex_property, vid, rank, time_interval)
            else:
                if exist_relative_at_rank(graph, vid, rank): # Check if there is at least one descendants for `vid` at `rank`!
                    temporal_func[vid] = func(graph, vertex_property, vid, rank, time_interval)

        # -- If there was any problems with some vis, we print it before returning the results:
        omit = list( set(vids) - set(temporal_func.keys()) )
        if omit != [] and not no_warn:
            if len(omit)<=20 or verbose:
                print "Some of the `vids` have been omitted: ", omit
            else:
                print "Some of the `vids` have been omitted."

        # -- Now we return the results of temporal differentiation function:
        if labels_at_t_n: 
            return temporal_func
        else:
            return translate_keys2daughters_ids(graph, temporal_func)

    return  wrapped_function
    

@__normalized_temporal_parameters
def temporal_rate(graph, vertex_property, vid, rank, time_interval):
    """
    Sub-function computing the temporal change between ONE vertex ('vid') and its descendants at rank 'rank'.
    
    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    
    :Return:
    - a single value = temporal change between vertex 'vid' and its neighbors at rank 'rank'.
    """
    if rank == 1:
        vid_descendants = graph.children(vid)
        vid_parent = vid
    # - If rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
    if rank > 1:
        vid_descendants = graph.descendants(vid,rank)-graph.descendants(vid,rank-1)
        vid_parent = vid
    
    parent_value = vertex_property[vid_parent]
    descendants_value = sum([vertex_property[id_descendant] for id_descendant in vid_descendants])
    
    return np.log2(descendants_value / parent_value) * 1. / float(time_interval)


@__normalized_temporal_parameters
def temporal_change(graph, vertex_property, vid, rank, time_interval):
    """
    Sub-function computing the temporal change between ONE vertex ('vid') and its descendants at rank 'rank'.
    
    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    
    :Return:
    - a single value = temporal change between vertex 'vid' and its neighbors at rank 'rank'.
    """
    if rank == 1:
        vid_descendants = graph.children(vid)
        vid_parent = vid
    # - If rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
    if rank > 1:
        vid_descendants = graph.descendants(vid,rank)-graph.descendants(vid,rank-1)
        vid_parent = vid
    
    parent_value = vertex_property[vid_parent]
    descendants_value = sum([vertex_property[id_descendant] for id_descendant in vid_descendants])
    
    return (descendants_value - parent_value) / float(time_interval)


@__normalized_temporal_parameters
def relative_temporal_change(graph, vertex_property, vid, rank, time_interval):
    """
    Sub-function computing the relative temporal change between ONE vertex ('vid') and its descendants at rank 'rank'.
    
    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    
    :Return:
    - a single value = relative temporal change between vertex 'vid' and its neighbors at rank 'rank'.
    """
    return temporal_change(graph, vertex_property, vid, rank, time_interval).values()[0] / float(vertex_property[vid])


def vertex_gaussian_curvature( graph ):
    """
    Gaussian curvature is the product of principal curvatures 'k1*k2'.
    """    
    return dict([ (vid, curv_values[0] * curv_values[0]) for vid, curv_values in graph.vertex_property('epidermis_wall_principal_curvature_values').iteritems()])

def division_rate(graph, rank=1, parent_ids = False):
    """
    :Parameters:
     - 'graph' (TGP) - a TPG.
     - 'rank' (int) - children at distance 'rank' will be used.
     - 'parent_ids' (bool) - specify if the division rate values returned should be associated with parent ids or children ids.
    
    :Return:
     - div_rate = temporal division rate between vertex 'vid' and its descendants at rank 'rank'.
    """
    if (rank > 1) and (parent_ids is False):
        raise ValueError("The translation function `translate_keys2daughters_ids` doesn't work for rank != 1.")

    div_rate = {}
    for vid in graph.vertices():
        index_1 = graph.vertex_property('index')[vid]
        try:
            time_interval = graph.graph_property('time_steps')[index_1+rank]-graph.graph_property('time_steps')[index_1]
        except:
            continue #will go to the next `vid` if its 'index_1+rank' is out of range!

        descendants=graph.descendants(vid,rank)-set([vid])
        if descendants == set([]):
            div_rate[vid] = 0
        else:
            div_rate[vid] = (len(descendants) - 1) / float(time_interval)

    if parent_ids: 
        return div_rate
    else:
        return translate_keys2daughters_ids(graph, div_rate)


def exist_relative_at_rank(graph, vid, rank):
    """
    Check if there is a relative (descendant or ancestor) of the 'vid' at 'rank'.
    :Parameters:
     - 'graph' (TPG): the TPG to be used for translation
     - 'vid' (int): the initial point to look-out for rank existence.
     - 'rank' (int): the rank to test.
    """
    if rank == 0 :
        return True
    if (rank > 0) :
        try :
            return graph.descendants(vid,rank)-graph.descendants(vid,rank-1) != set()
        except:
            return False
    if (rank < 0) :
        try :
            return graph.ancestors(vid,abs(rank))-graph.ancestors(vid,abs(rank)-1) != set()
        except:
            return False


def exist_all_relative_at_rank(graph, vid, rank):
    """
    Check if lineage is complete over several ranks. 
    i.e. every decendants cells from `vid` have a lineage up to rank `rank`.
    Suppose that the lineage has been correctly done: a lineage is given to the graph only if we are sure to have all the daugthers from a mother.
    
    :Parameters:
    - `graph` TPG to browse;
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    """
    if rank == 0 or not exist_relative_at_rank(graph, vid, rank):
        return False

    if rank == 1 or rank == -1:
        return exist_relative_at_rank(graph, vid, rank)

    if (rank > 0):
        descendants_at_rank = {}
        descendants_at_rank[1] = graph.children(vid)
        for r in xrange(2,rank+1):
            for v in descendants_at_rank[r-1]:
                if graph.children(v) == set():
                    return False
                if descendants_at_rank.has_key(r):
                    descendants_at_rank[r].update(graph.children(v))
                else:
                    descendants_at_rank[r] = graph.children(v)
        return True

    if (rank < 0):
        rank = -rank
        descendants_at_rank = {}
        descendants_at_rank[1] = graph.parent(vid)
        for r in xrange(2,rank+1):
            for v in descendants_at_rank[r-1]:
                if graph.parent(v) == set():
                    return False
                if descendants_at_rank.has_key(r):
                    descendants_at_rank[r].update(graph.parent(v))
                else:
                    descendants_at_rank[r] = graph.parent(v)
        return True


def time_point_property(graph, time_point, vertex_property, only_lineaged = False, as_mother = False, as_daughter = False):
    """
    Allow to extract a property 'vertex_property' from the temporal graph for one time-point.
    
    :Parameters:
    - `graph` (TemporalPropertyGraph) - Spatio-temporal graph to browse;
    - `time_point` (int) - define the time-point to consider;
    - `vertex_property` (str) - name of the vertex property to extract;
    :Return:
    - dictionnary of vertex property extracted from the time-point 'time_point';
    """
    # if a name is given, we use vertex_property stored in the graph with this name.
    if isinstance(vertex_property,str):
        vertex_property = graph.vertex_property(vertex_property)
        
    if time_point not in graph.vertex_property('index').values():
        raise ValueError(str(time_point)+"not in"+str(graph))

    vids_at_time = graph.vertex_ids_at_time(time_point, only_lineaged, as_mother, as_daughter)
    
    return dict([(i,vertex_property[i]) for i in vids_at_time if vertex_property.has_key(i)])
    

def time_point_property_by_regions(graph, time_point, vertex_property, only_lineaged = False, as_mother = False, as_daughter = False):
    """
    Allow to extract a property 'vertex_property' from the temporal graph for one time-point, sorted by regions.
    Return a dict of dict, first level of keys are region(s) name(s) and second layer are vertex ids and the values of their associated property.
    
    :Parameters:
    - `graph` (TemporalPropertyGraph) - Spatio-temporal graph to browse;
    - `time_point` (int) - define the time-point to consider;
    - `vertex_property` (str) - name of the vertex property to extract;
    :Return:
    - dictionary of regions which values are a dictionnary of vertex property extracted from the time-point;
    """
    extracted_property = time_point_property(graph, time_point, vertex_property, only_lineaged, as_mother, as_daughter)
    
    regions_names = list(np.unique([v[0] for k,v in graph.vertex_property('regions').iteritems() if graph.vertex_property('index')[k]==time_point]))
    
    property_by_regions = {}
    for region_name in regions_names:
        property_by_regions[region_name] = dict( (k,v) for k,v in extracted_property.iteritems() if graph.vertex_property('regions').has_key(k) and (graph.vertex_property('regions')[k][0]==region_name) )
    
    return property_by_regions


def histogram_property_by_time_points(graph, vertex_property, time_points=None, vids=None, **kwargs):
    """
    Display an histogram or barplot of the provided `vertex_property` by `time_points`.
    """
    property_name = None
    if isinstance(vertex_property,str):
        assert vertex_property in list(graph.vertex_properties())
        property_name = vertex_property
        vertex_property = graph.vertex_property(vertex_property)
    
    if time_points is None:
        time_points = xrange(graph.nb_time_points)
    if vids is None:
        vids = [vid for vid in graph.vertices() if vid in vertex_property]

    ppt_kwargs = {}
    if 'only_lineaged' in kwargs: ppt_kwargs.update({'only_lineaged':kwargs['only_lineaged']})
    if 'as_mother' in kwargs: ppt_kwargs.update({'as_mother':kwargs['as_mother']})
    if 'as_daughter' in kwargs: ppt_kwargs.update({'as_daughter':kwargs['as_daughter']})
    data = []
    for tp in time_points:
        data.append(time_point_property(graph, tp, vertex_property,**ppt_kwargs).values())

    h_kwargs= {}
    if 'bins' in kwargs: h_kwargs.update({'bins':kwargs['bins']})
    if 'normed' in kwargs: h_kwargs.update({'normed':kwargs['normed']})
    if 'histtype' in kwargs: h_kwargs.update({'histtype':kwargs['histtype']})
    
    fig = plt.figure()
    n, bins, patches = plt.hist(data, label = ["time point #{}".format(tp) for tp in time_points], **h_kwargs)
    if kwargs.has_key('title'):
        plt.title(kwargs['title'])
    elif property_name is not None:
        plt.title("Histogram of {0} property".format(property_name))
    if kwargs.has_key('xlabel'):
        plt.xlabel(kwargs['xlabel'])
    elif property_name is not None:
        plt.xlabel(property_name)
    if h_kwargs.has_key('normed') and h_kwargs['normed']:
        plt.ylabel("Relative Frequency")
    elif h_kwargs.has_key('normed') and not h_kwargs['normed']:
        plt.ylabel("Frequency")
    plt.legend()

    return n, bins, patches


def translate_keys2daughters_ids(graph, dictionary):
    """
    Translate keys of a dictionary to daughter ids according to the graph (Temporal Property Graph).
    """
    dictionary_daughters={}
    no_descendants=[]
    for vid in dictionary:
        vid_descendants = graph.descendants(vid ,1)-graph.descendants(vid,0)
        if vid_descendants != set():
            for id_descendant in vid_descendants:
                dictionary_daughters[id_descendant]=dictionary[vid]
        elif graph.vertex_property('index')[vid] < graph.nb_time_points-1: #if `vid``belong to the last time point, it's perfectly normal that there is no descendants
            no_descendants.append(vid)

    if no_descendants!=[]:
        warnings.warn("No daughter found for those vertex:"+str(no_descendants))

    return dictionary_daughters


def translate_list2daughters_ids(graph, ids_list):
    """
    Translate keys of a dictionary to daughter ids according to the graph (Temporal Property Graph).
    """
    list_daughters=[]
    no_descendants=[]
    for vid in ids_list:
        vid_descendants = graph.descendants(vid ,1)-graph.descendants(vid,0)
        if vid_descendants != set():
            for id_descendant in vid_descendants:
                list_daughters.append(id_descendant)
        elif graph.vertex_property('index')[vid] < graph.nb_time_points-1: #if `vid``belong to the last time point, it's perfectly normal that there is no descendants
            no_descendants.append(vid)

    if no_descendants!=[]:
        warnings.warn("No daughter found for those vertex:"+str(no_descendants))

    return list_daughters


def weighted_mean( values, weights ):
    """
    Function computing a weighted mean of `values` according to `weights`.
         - `values` (list)
         - `weights` (list)
    Return:
         - wm = sum_i( value_i * weight_i/sum(weights) )
    """
    assert len(values)==len(weights)
    
    if isinstance(values[0],int) or isinstance(values[0],np.ndarray):
        return sum( [v * w / float(sum(weights)) for v,w in zip(values, weights)] )
    if isinstance(values[0],list) or isinstance(values[0],tuple):
        return sum( [np.array(v) * w / float(sum(weights)) for v,w in zip(values, weights)] )


def __strain_parameters(func):
    def wrapped_function(graph, vids = None, labels_at_t_n = True, use_projected_anticlinal_wall = False, verbose = False):
        """
        :Parameters:
         - `graph` (TPG)
         - `vids` (int|list) - list of (graph) vertex ids @ t_n. If :None: it will be computed for all possible vertex
         - `use_projected_anticlinal_wall` (bool) - if True, use the medians of projected anticlinal wall ('projected_anticlinal_wall_median') to compute a strain in 2D.
        """
        # Check if cells landmarks have been recovered ans stored in the graph structure:
        if use_projected_anticlinal_wall:
            assert 'projected_anticlinal_wall_median' in graph.edge_property_names()
            assert 'epidermis_wall_median' in graph.vertex_property_names()
            assert 'epidermis_surface' in graph.vertex_property_names()
        else:
            assert 'wall_median' in graph.edge_property_names()
            assert 'unlabelled_wall_median' in graph.vertex_property_names()
            assert 'epidermis_wall_median' in graph.vertex_property_names()

        # -- If the vid is not associated through time it's not possible to compute the strain.
        if vids is None:
            vids = list(graph.vertices())
        if isinstance(vids,int):
            vids=[vids]

        # -- If the vid is not associated through time it's not possible to compute the strain.
        tmp = copy.copy(vids)
        for vid in vids:
            if graph.descendants(vid, 1) == set([vid]):
                tmp.remove(vid)

        vids = tmp
        if use_projected_anticlinal_wall:
            spatial_vertices_edge = dict( [(tuple(sorted(v)),k) for k,v in graph._edges.iteritems() if k in graph.edges(edge_type='s')] )
            # Next line could be changed: we could create a smaller dict by looking in something smaller than all graphs edges!!!
            wall_median_2 = dict( ( tuple(sorted(graph.edge_vertices(eid))), graph.edge_property('projected_anticlinal_wall_median')[eid]) for eid in graph.edges(edge_type='s') if graph.edge_property('projected_anticlinal_wall_median').has_key(eid) )
            stretch_mat = {}

            for n,vid in enumerate(vids):
                if verbose and n%10==0: print n, " / ", len(vids)
                missing_data = False
                spatial_edges = list(graph.edges( vid, 's' ))
                # We create the dictionary of medians associate over time: {(label_1,label_2):[x,y,z]} with label_1<label_2 and label_1&label_2 in the first layer !
                wall_median = dict( ( tuple(sorted(graph.edge_vertices(eid))), graph.edge_property('projected_anticlinal_wall_median')[eid] ) for eid in spatial_edges if graph.edge_property('projected_anticlinal_wall_median').has_key(eid) )

                # -- Now we want to associate landmarks over time:
                xyz_t1, xyz_t2 = [], []
                descendants_vid = list(graph.descendants(vid,1)-set([vid]))
                neighbors_t1 = [nei for nei in list(graph.neighbors(vid,'s')) if wall_median.has_key(tuple(sorted([nei,vid])))]
                # - Using barycenter of the epidermis wall :
                xyz_t1.append(np.array(graph.vertex_property('epidermis_wall_median')[vid]))
                if len(descendants_vid)>1:
                    xyz_t2.append(weighted_mean( [graph.vertex_property('epidermis_wall_median')[desc_id_cp] for desc_id_cp in descendants_vid], [graph.vertex_property('epidermis_surface')[desc_id_cp] for desc_id_cp in descendants_vid if graph.vertex_property('epidermis_surface').has_key(desc_id_cp)] ))
                else:
                    xyz_t2.append(np.array(graph.vertex_property('epidermis_wall_median')[descendants_vid[0]]))

                # - Now we need to find the time correspondance between each median:
                for neighbor in neighbors_t1:
                    descendants_neighbor = [desc_nei for desc_nei in graph.descendants(neighbor,1)-set([neighbor])]
                    nei = list(set(descendants_vid) | set(descendants_neighbor))
                    # - In order to find the decendants that share the 'same' wall we have to find those from each (two) groups that have a topological distance of 1:
                    topological_distance = dict( ((vtx_id, graph.topological_distance(vtx_id, 's', full_dict=False))) for vtx_id in nei )
                    neighbors_descendants = []
                    for nei_1 in descendants_vid:
                        for nei_2 in descendants_neighbor:
                            if wall_median_2.has_key(tuple(sorted((nei_1,nei_2)))) and topological_distance[nei_1][nei_2] == 1:
                                neighbors_descendants.append(tuple(sorted((nei_1,nei_2))))
                    # - If correspondance is found we retreive landmarks coordiantes
                    if neighbors_descendants != [] and len([wall_median_2[desc_id_cp] for desc_id_cp in neighbors_descendants])==len(neighbors_descendants):
                        id_couple = (min(vid,neighbor),max(vid,neighbor))
                        xyz_t1.append(np.array(wall_median[id_couple]))
                        # - We compute a weighted average for the t_n+1 landmark if the cell has divided: x,y,z = sum_i{ wall_surface_i * [x_i,y_i,z_i] }
                        xyz_t2.append(weighted_mean( [wall_median_2[desc_id_cp] for desc_id_cp in neighbors_descendants], [graph.edge_property('wall_surface')[spatial_vertices_edge[desc_id_cp]] for desc_id_cp in neighbors_descendants if graph.edge_property('wall_surface').has_key(spatial_vertices_edge[desc_id_cp])] ))

                if not missing_data:
                    assert len(xyz_t1) == len(xyz_t2)
                    N = len(xyz_t1)
                    stretch_mat[vid] = func(graph, xyz_t1, xyz_t2)
        else:
            ############################################################
            # If graph.vertex_property('unlabelled_wall_median')[vid] is None, it means we should not compute a 3D strain for this cell !!!
            # It's beacause unlabelled walls were not contiguous, so it could not be used to compute a median !!
            ############################################################
            spatial_vertices_edge = dict( ((min(v[0],v[1]),max(v[0],v[1])),k) for k,v in graph._edges.iteritems() if k in graph.edges(edge_type='s'))
            # Next line need to be changed: we should create a smaller dict by looking in something smaller than all graphs edges!!!
            wall_median_2 = dict( ( (min(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1]),max(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1])) ,graph.edge_property('wall_median')[eid]) for eid in graph.edges(edge_type='s') if graph.edge_property('wall_median').has_key(eid) )
            stretch_mat = {}
            for n,vid in enumerate(vids):
                if verbose and n%10==0: print n, " / ", len(vids)
                missing_data=False
                spatial_out_edges = list(graph.edges( vid, 's' ))
                wall_median = dict( ((min(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1]),max(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1])),graph.edge_property('wall_median')[eid]) for eid in spatial_out_edges if graph.edge_property('wall_median').has_key(eid) )

                # - If not every 's'type edges from a `vid` have a median and there is no 'unlabelled_wall_median' associated, it means we don't have all the info for strain computation:
                if (len(wall_median) == len(spatial_out_edges)) or (graph.vertex_property('unlabelled_wall_median').has_key(vid)):
                    xyz_t1, xyz_t2 = [], []
                    descendants_vid = graph.descendants(vid,1)-set([vid])
                    neighbors_t1 = list(graph.neighbors(vid,'s'))
                    # -- Now we need to find the time correspondance between each median:
                    for neighbor in neighbors_t1:
                        descendants_neighbor = graph.descendants(neighbor,1)-set([neighbor])
                        nei = list(descendants_vid | descendants_neighbor)
                        # -- In order to find the decendants that share the 'same' wall we have to find those from each (two) groups that have a topological distance of 1:
                        topological_distance = dict( ((vtx_id, graph.topological_distance(vtx_id, 's', full_dict=False))) for vtx_id in nei )
                        neighbors_descendants = []
                        for nei_1 in descendants_vid:
                            for nei_2 in descendants_neighbor:
                                if topological_distance[nei_1][nei_2] == 1:
                                    if nei_1 < nei_2: neighbors_descendants.append((nei_1,nei_2))
                                    if nei_1 > nei_2: neighbors_descendants.append((nei_2,nei_1))

                        if neighbors_descendants != [] and len([wall_median_2[desc_id_cp] for desc_id_cp in neighbors_descendants])==len(neighbors_descendants):
                            id_couple = (min(vid,neighbor),max(vid,neighbor))
                            xyz_t1.append(np.array(wall_median[id_couple]))
                            xyz_t2.append(weighted_mean( [wall_median_2[desc_id_cp] for desc_id_cp in neighbors_descendants], [graph.edge_property('wall_surface')[spatial_vertices_edge[desc_id_cp]] for desc_id_cp in neighbors_descendants] ))
                        else:
                            missing_data=True

                    # -- We need to make sure `unlabelled_wall_median` is both @ t_n and at least for one daughter cell @ t_n+1
                    if not missing_data and graph.vertex_property('unlabelled_wall_median').has_key(vid) and (sum([graph.vertex_property('unlabelled_wall_median').has_key(id2) for id2 in descendants_vid])>=1):
                        xyz_t1.append(graph.vertex_property('unlabelled_wall_median')[vid])
                        xyz_t2.append( weighted_mean( [graph.vertex_property('unlabelled_wall_median')[desc_vid] for desc_vid in descendants_vid], [graph.vertex_property('unlabelled_wall_surface')[desc_id] for desc_id in descendants_vid] ))

                    # -- We need to make sure `epidermis_wall_median` is both @ t_n and at least for one daughter cell @ t_n+1
                    if not missing_data and graph.vertex_property('epidermis_wall_median').has_key(vid) and (sum([graph.vertex_property('epidermis_wall_median').has_key(id2) for id2 in descendants_vid])>=1):
                        xyz_t1.append(graph.vertex_property('epidermis_wall_median')[vid])
                        xyz_t2.append( weighted_mean( [graph.vertex_property('epidermis_wall_median')[desc_vid] for desc_vid in descendants_vid], [graph.vertex_property('epidermis_surface')[desc_id] for desc_id in descendants_vid] ))

                if not missing_data:
                    assert len(xyz_t1) == len(xyz_t2)
                    N = len(xyz_t1)
                    stretch_mat[vid] = func(graph, xyz_t1, xyz_t2)

        # -- Now we return the results of temporal differentiation function:
        if labels_at_t_n: 
            return stretch_mat
        else:
            stretch_mat_daughters={}
            print "You have asked for labels @ t_n+1"
            for vid in stretch_mat:
                vid_descendants = graph.descendants(vid ,1)-graph.descendants(vid,0)
                for id_descendant in vid_descendants:
                    stretch_mat_daughters[id_descendant]=stretch_mat[vid]
            return stretch_mat_daughters

    return  wrapped_function

@__strain_parameters
def stretch_matrix(graph, xyz_t1, xyz_t2):
    """
    Compute the stretch / deformation matrix.
    """
    ## Compute the centroids:
    c_t1 = np.mean(xyz_t1,0)
    c_t2 = np.mean(xyz_t2,0)
    ## Compute the centered matrix:
    centered_coord_t1=np.array(xyz_t1-c_t1)
    centered_coord_t2=np.array(xyz_t2-c_t2)
    ## Least-square estimation of A.
    #A is the transformation matrix in the regression equation between the centered vertices position of two time points:
    lsq=lstsq(centered_coord_t1,centered_coord_t2)
    A=lsq[0]

    return A

def strain_orientations(stretch_mat, nb_directions=None, after_deformation=True):
    """
    Return the strain main directions after deformation (default) or before.
    """
    if nb_directions is None:
        nb_directions = 3

    directions = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(stretch_mat[vid])
        # Compute Strain Rates :
        if after_deformation:
            directions[vid] = Q[:nb_directions,:]
        else:
            directions[vid] = R[:,:nb_directions]

    return directions

def strain_rates(graph, stretch_mat):
    """
    Return the strain rate: sr[c][i] = np.log(D_A[i])/deltaT, for i = [0,1] if 2D, i = [0,1,2] if 3D.
    Dimensionnality is imposed by the one of the strain matrix.
    """
    sr = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(stretch_mat[vid])
        # Compute Strain Rates :
        sr[vid] = np.log(D_A)/float(time_interval(graph, vid, rank =1))

    return sr

def areal_strain_rates(graph, stretch_mat):
    """
    Compute the areal strain rate: asr[c] = sum_i(np.log(D_A[i])/deltaT), for i = [0,1].
    """
    asr = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(stretch_mat[vid])
        # Compute Strain Rates and Areal Strain Rate:
        asr[vid] = sum(np.log(D_A[0:2])/float(time_interval(graph, vid, rank =1)))

    return asr

def volumetric_strain_rates(graph, stretch_mat):
    """
    Compute the volumetric strain rate: asr[c] = sum_i(np.log(D_A[i])/deltaT), for i = [0,1,2].
    """
    vsr = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(stretch_mat[vid])
        # Compute Strain Rates and Areal Strain Rate:
        vsr[vid] = sum(np.log(D_A)/float(time_interval(graph, vid, rank =1)))

    return vsr

def strain_anisotropy(graph, stretch_mat):
    """
    Compute the "Growth" Anisotropy = (sr1-sr2)/(sr1+sr2)
    Dimensionnality is imposed by the one of the strain matrix.
    """
    anisotropy = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q = svd(stretch_mat[vid])
        # Compute Strain Rates :
        strain_rate = D_A/float(time_interval(graph, vid, rank =1))
        anisotropy[vid] = (strain_rate[0]-strain_rate[1])/(strain_rate[0]+strain_rate[1])

    return anisotropy

def anisotropy_ratios(stretch_mat):
    """
    Anisotropy ratio :
     R, strain_values, Q = svd( stretch_mat ), then
    -if 2D:
        return strain_values[0]/strain_values[1]
    - if 3D:
        return [ sv[0]/sv[1], sv[1]/sv[2], sv[0]/sv[2] ]

    Dimensionnality is imposed by the one of the strain matrix `stretch_mat`.
    """
    anisotropy_ratio = {}
    for vid in stretch_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q = svd(stretch_mat[vid])
        if len(D_A) == 3:
            anisotropy_ratio[vid] = [ D_A[0]/D_A[1], D_A[1]/D_A[2], D_A[0]/D_A[2] ]
        else:
            anisotropy_ratio[vid] = D_A[0]/D_A[1]

    return anisotropy_ratio


def time_interval(graph,vid,rank=1):
    """
    Compute the time interval for the vexterx id `vid` thanks to data saved in graph.graph_property('time_steps').
    """
    index_1 = graph.vertex_property('index')[vid]
    return (graph.graph_property('time_steps')[index_1+rank]-graph.graph_property('time_steps')[index_1])


def sibling_volume_ratio(graph):
    """
    """
    svr={}
    used_vtx = []
    for vtx in graph.vertices():
        sibling = graph.sibling(vtx)
        if sibling is not None and len(sibling)==1 and list(graph.sibling(vtx))[0] not in used_vtx:
            used_vtx.append(vtx)
            sibling = list(graph.sibling(vtx))[0]
            ratio = graph.vertex_property('volume')[vtx]/graph.vertex_property('volume')[sibling]
            if ratio >=1:
                svr[sibling,vtx]=1./ratio
            else:
                svr[vtx,sibling]=ratio
    return svr

def triplot(graphs_list, values2plot, labels_list=None, values_name="",normed=False):
    """
    TO DO
    """
    import numpy as np
    if labels_list==None:
        labels_list=[]
        for g in graphs_list:
            labels_list.append(g.vertex_property('label'))
    
    values=[]
    abs_dev_values=[]
    laplacian_values=[]
    #-- if 'values2plot' is a string, it must be a property found in all graphs in the 'graph_list'.
    if type(values2plot)==type(str('str')):
        for g in graphs_list:
            if values2plot not in g.vertex_property_names():
                import sys
                sys.exit(1)
            else:
                if (values_name==""):
                    values_name=values2plot
                values.append(g.vertex_property(values2plot).values())
                abs_dev_values.append(dev_abs(g,values2plot,True))
                laplacian_values.append(laplacian(g,values2plot,True))

    import matplotlib.pyplot as plt
    fig = plt.figure()
    fig.subplots_adjust( wspace=0.13, left=0.05, right=0.95, top=0.95)
    main=fig.add_subplot(1,2,1)
    main.hist(values, bins=20,normed=normed,
        label=( ('t1, n='+str(len(values[0]))+', mean='+str(np.round(np.mean(values[0]), 2))) ,
        ('t2, n='+str(len(values[1]))+', mean='+str(np.round(np.mean(values[1]), 2))) ,
        ('t3, n='+str(len(values[2]))+', mean='+str(np.round(np.mean(values[2]), 2))) ), histtype='bar' )
    plt.title("L1 cells' "+values_name)
    if values_name=='volume':
        plt.xlabel('Volumes'+ r' ($\mu m^3$)')
    else:
        plt.xlabel(values_name)
    if normed:
            plt.ylabel('Frequency')
    else:
        plt.ylabel('Number of observations')
    plt.legend()
    
    dev=fig.add_subplot(2,2,2)
    dev.hist(abs_dev_values, bins=20,normed=normed,
        label=( ('t1, n='+str(len(abs_dev_values[0]))+', mean='+str(np.round(np.mean(abs_dev_values[0]), 2))) ,
        ('t2, n='+str(len(abs_dev_values[1]))+', mean='+str(np.round(np.mean(abs_dev_values[1]), 2))) ,
        ('t3, n='+str(len(abs_dev_values[2]))+', mean='+str(np.round(np.mean(abs_dev_values[2]), 2))) ), histtype='bar' )
    plt.title("L1 cells' absolute deviance from neighbors in "+values_name)
    plt.xlabel('Deviance from neighbors in volumes'+ r' ($\mu m^3$)')
    if normed:
            plt.ylabel('Frequency')
    else:
        plt.ylabel('Number of observations')
    plt.legend()
    
    lap=fig.add_subplot(2,2,4)
    lap.hist(laplacian_values, bins=20,normed=normed,
        label=( ('t1, n='+str(len(laplacian_values[0]))+', mean='+str(np.round(np.mean(laplacian_values[0]), 2))) ,
        ('t2, n='+str(len(laplacian_values[1]))+', mean='+str(np.round(np.mean(laplacian_values[1]), 2))) ,
        ('t3, n='+str(len(laplacian_values[2]))+', mean='+str(np.round(np.mean(laplacian_values[2]), 2))) ), histtype='bar' )
    plt.title("L1 cells' laplacian from neighbors in "+values_name)
    plt.xlabel('Laplacian from neighbors in volumes'+ r' ($\mu m^3$)')
    if normed:
            plt.ylabel('Frequency')
    else:
        plt.ylabel('Number of observations')
    plt.legend()
    plt.show()


#~ def shape_anisotropy_2D(graph, vids=None, add2vertex_property = True):
    #~ """
    #~ Compute shape anisotropy in 2D based on the two largest inertia axis length.
    #~ !!!!! SHOULD BE COMPARED WITH NORMAL VECTOR FROM CURVATURE COMPUTATION !!!!!
    #~ """
    #~ if vids == None:
        #~ vids = graph.vertex_property('inertia_axis').keys()
    #~ else:
        #~ for vid in vids:
            #~ if not graph.vertex_property('inertia_axis').has_key(vid):
                #~ warnings.warn("Inertia axis hasn't been computed for vid #"+str(vid))
                #~ vids.remove(vid)
    #~ 
    #~ shape_anisotropy_2D = {}
    #~ for vid in vids:
        #~ axis_len = graph.vertex_property('inertia_axis')[vid][1]
        #~ shape_anisotropy_2D[vid] = float(axis_len[0]-axis_len[1])/(axis_len[0]+axis_len[1])
    #~ 
    #~ if add2vertex_property:
        #~ graph.add_vertex_property("2D shape anisotropy",shape_anisotropy_2D)
    #~ 
    #~ return shape_anisotropy_2D
#~ 
#~ 
