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
from interface.property_graph import IPropertyGraph, PropertyError

from scipy.sparse import csr_matrix
from numpy.linalg import svd, lstsq

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
        return graph.descendants(vid,rank)-graph.descendants(vid,rank-1) != set()
    if (rank < 0) :
        return graph.ancestors(vid,abs(rank))-graph.ancestors(vid,abs(rank)-1) != set()


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
        warnings.warn('This is not a "list" type variable.')
        return None

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
        warnings.warn('This is not a "list" type variable.')
        return None

    graph_labels_at_time_point = graph.vertex_ids_at_time(time_point)
    Image2Graph_labels_at_time_point = dict( (v,k) for k,v in graph.vertex_property('old_label').iteritems() if k in graph_labels_at_time_point )

    Image2Graph_labels, Image_labels_not_found = [], []
    for k in id_list:
        if k in Image2Graph_labels_at_time_point.keys():
            Image2Graph_labels.append(Image2Graph_labels_at_time_point[k])
        else:
            Image_labels_not_found.append(k)

    if Image_labels_not_found != []:
        warnings.warn("The cell ids"+str(Image_labels_not_found)+"were not in the graph!")

    if isinstance(id_list,int) and (Image_labels_not_found == []):
        return Image2Graph_labels[0]

    return Image2Graph_labels

def translate_keys_Graph2Image(graph, dictionary):
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
        warnings.warn('This is not a "dict" type variable.')
        return None
    
    return dict( (graph.vertex_property('old_label')[k], dictionary[k]) for k in dictionary )

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
        warnings.warn('This is not a "dict" type variable.')
        return None
    
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
        return result - ivalue


def __normalized_temporal_parameters(func):
    def wrapped_function(graph, vertex_property, vids = None, rank = 1, labels_at_t_n = True, check_full_lineage = True, rank_lineage_check = None, verbose = False):
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
        if vids==None:
            vids = vertex_property.keys()
        
        if isinstance(vids,int):
            vids=[vids] # for single id, compute single result
        
        if rank_lineage_check == None:
            rank_lineage_check = rank

        try:
            graph.graph_property('time_steps')
        except:
            warnings.warn("You did not defined the `time_steps` when creating the TemporalPropertyGraph.")
            print("Use graph.add_graph_property('time_steps',time_steps) to add it.")
            return None

        # -- We compute the `time_interval` once and for all:
        index_1 = graph.vertex_property('index')[vids[0]]
        time_interval = (graph.graph_property('time_steps')[index_1+rank]-graph.graph_property('time_steps')[index_1])

        # -- For a list of ids, we create a dictionary of resulting values from function `func`.
        l={}
        for k,vid in enumerate(vids):
            if verbose and k%10==0: print k,'/',len(vids)
            if check_full_lineage:
                if full_lineage(graph, vid, rank_lineage_check): # Check if ALL descendants up to `rank_lineage_check` exists !
                    l[vid] = func(graph, vertex_property, vid, rank, time_interval)
            else:
                if full_lineage(graph, vid, 1): # Check if there is at least one descendants for `vid`!
                    l[vid] = func(graph, vertex_property, vid, rank, time_interval)

        if labels_at_t_n:
            return l
        else:
            m={}
            print "You have asked for labels @ t_n+"+str(rank)
            for vid in l:
                if rank > 1:
                    vid_descendants = graph.descendants(vid ,rank)-graph.descendants(vid,rank-1)
                else:
                    vid_descendants = graph.children(vid)

                for id_descendant in vid_descendants:
                    m[id_descendant]=l[vid]
            return m
    
    return  wrapped_function

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
    else: # if rank > 1, we want to compute the change only over the cell at `rank` and not for all cells between rank 1 and `rank`.
        vid_descendants = graph.descendants(vid,rank)-graph.descendants(vid,rank-1)
    
    nb_descendants = len(vid_descendants)
    descendants_value = 0
    vid_value = vertex_property[vid]
    for id_descendant in vid_descendants:
        descendants_value = descendants_value + vertex_property[id_descendant]
    
    return (descendants_value - vid_value) / float(time_interval)


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
    return temporal_change(graph, vertex_property, vid, rank).values()[0] / float(vertex_property[vid]) / float(time_interval)


def full_lineage(graph, vid, rank):
    """
    Check if lineage is complete over several ranks. 
    i.e. every decendants cells from `vid` have a lineage up to rank `rank`.
    Suppose that the lineage has been correctly done: a lineage is given to the graph only if we are sure to have all the daugthers from a mother.
    
    :Parameters:
    - `graph` TPG to browse;
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    """
    # -- We create a first list of descendants at rank 1.
    vids_descendants={}
    vids_descendants[1] = graph.descendants(vid,1)
    vids_descendants[1].remove(vid)
    
    # -- First thing you want to know is if there is a lineage at least at the first order !
    if len(vids_descendants[1]) < 1:
        return False
    
    # -- If rank == 1 (and there is a lineage but we already did the test!) we suppose that it has been correctly done !
    if rank == 1:
        return True
    
    # -- To check a full lineage @rank_n :
    for r in xrange(2,rank+1):
        len_lineage_at_r = 0
        for v in vids_descendants[r-1]: # for every mother cell @ rank_n-1 (n>2),
            if len(graph.descendants(v,1)) > 1: # we verify she has a daughter @ rank_n
                len_lineage_at_r += 1
        if len_lineage_at_r != len(vids_descendants[r-1]):
            #~ print len_lineage_at_r,'/', len(vids_descendants[r-1])
            return False
        else:
            # Retreive cells only at rank_n-1: (not all cells between rank 1 and `rank`)
            vids_descendants[r] = graph.descendants(vid,r)-graph.descendants(vid,r-1)
    
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
        import warnings
        warnings.warn(str(time_point)+"not in"+str(graph))

    vids_at_time = graph.vertex_ids_at_time(time_point, only_lineaged, as_mother, as_daughter)
    
    return dict([(i,vertex_property[i]) for i in vertex_property if i in vids_at_time])
    

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


def csr_matrix_from_graph(graph, vids2keep):
    """
    Create a sparse matrix representing a connectivity matrix recording the topological information of the graph.
    Defines for each vertex the neigbhoring vertex following a given structure of the data.
    
    :Parameters:
     - graph (Graph | PropertyGraph | TemporalPropertyGraph): graph to extract connectivity.
     - vids2keep (list): lis of vertex ids to build the sparse matrix from.
     (columns and rows will be ordered like in this list)
    """    
    N = len(vids2keep)
    data,row,col = [],[],[]
    
    for edge in graph.edges(edge_type='s'):
        s,t = graph.edge_vertices(edge)
        if (s in vids2keep) and (t in vids2keep):
            row.extend([vids2keep.index(s),vids2keep.index(t)])
            col.extend([vids2keep.index(t),vids2keep.index(s)])
            data.extend([1,1])
    
    return csr_matrix((data,(row,col)), shape=(N,N))


def shape_anisotropy_2D(graph, vids=None, add2vertex_property = True):
    """
    Compute shape anisotropy in 2D based on the two largest inertia axis length.
    !!!!! SHOULD BE COMPARED WITH NORMAL VECTOR FROM CURVATURE COMPUTATION !!!!!
    """
    if vids == None:
        vids = graph.vertex_property('inertia_axis').keys()
    else:
        for vid in vids:
            if not graph.vertex_property('inertia_axis').has_key(vid):
                warnings.warn("Inertia axis hasn't been computed for vid #"+str(vid))
                vids.remove(vid)
    
    shape_anisotropy_2D = {}
    for vid in vids:
        axis_len = graph.vertex_property('inertia_axis')[vid][1]
        shape_anisotropy_2D[vid] = float(axis_len[0]-axis_len[1])/(axis_len[0]+axis_len[1])
    
    if add2vertex_property:
        graph.add_vertex_property("2D shape anisotropy",shape_anisotropy_2D)
    
    return shape_anisotropy_2D


def cells_landmarks_relations(cells2landmark_coord):
    """
    Creates landmark_id2cells_id, landmark_id2coord & cell_id2landmarks_id dictionaries.
    
    :INPUT:
    - `cells2landmark_coord` (dict) *keys=the cells ids bound to a landmark coordinates ; *values=3D coordinates of a landmark in the SpatialImage.
    
    :OUPTUTS:
    - `landmark_id2cells_id` (dict) - *keys= landmark NEW id ; *values= ids of the associated cells.
    - `landmark_id2coord` (dict) - *keys= landmark NEW id ; *values= 3D coordinates of the landmark in the SpatialImage.
    - `cell_id2landmarks_id` (dict) - *keys= cell id ; *values= ids of the landmarks defining the cell.
    """
    landmark_id2cells_id = {} #associated cells to each vertex;
    cell_id2landmarks_id = {} #associated landmark to each cells;
    landmark_id2coord = {}
    for n, i in enumerate(cells2landmark_coord.keys()):
        landmark_id2cells_id[n] = list(i)
        landmark_id2coord[n] = list(cells2landmark_coord[i])
        for j in list(i):
            #check if cell j is already in the dict
            if cell_id2landmarks_id.has_key(j): 
                cell_id2landmarks_id[j] = cell_id2landmarks_id[j]+[n] #if true, keep the previous entry (landmark)and give the value of the associated landmark
            else:
                cell_id2landmarks_id[j] = [n] #if false, create a new one and give the value of the associated landmark
    #~ del(cell_id2landmarks_id[1]) #cell #1 doesn't really exist...
    return landmark_id2cells_id, landmark_id2coord, cell_id2landmarks_id


def landmark_temporal_association(graph, use_projected_anticlinal_wall = False):
    """
    Creates landmark2landmark dictionnary (v2v): associate the landmarks over time.

    :INPUTS:
     - `graph` (TPG) 
     - `use_projected_anticlinal_wall` (bool) - if True, use the medians of projected anticlinal wall ('projected_anticlinal_wall_median') to compute a strain in 2D.

    :OUPTUT:
        .v2v: dict *keys=t_n+1 vertex number; *values=associated t_n vertex.
    """
    # -- We create new dictionaries to be used further:
    landmark_id2cells_id, landmark_id2coord, cell_id2landmarks_id = cells_landmarks_relations( cells2landmark_coord )

    vtx_time_association = []
    
    for t in xrange( len(graph.graph_property('cell_vertices_coord'))-1 ):
        v2v = {} ##vertex t_n vers t_n+1
        ## Loop on the vertices label of t_n+1:
        for vtx in vtx2cells[t+1].keys():
            associated_cells = list( vtx2cells[t+1][vtx] )
            ## For the 4 (daugthers) cells associated to this vertex, we temporary replace it by it's mother label:
            for n,cell in enumerate(associated_cells):
                if cell == None: # Mean background...
                    associated_cells.remove(None)
                else:
                    ancestors = graph.ancestors(cell,1)
                    if len(ancestors) != 1: ## if the cell has ancestors (ancestor return a set containing the vertex you ask for)...
                        associated_cells[n] = list(ancestors-set([cell]))[0] ## ...we replace the daughters' label by the one from its mother.
                    else:
                        associated_cells[n] = 0 ## ...else we code by a 0 the absence of a mother in the lineage file (for one -or more- of the 4 daugthers)
            if 0 not in associated_cells: ## If the full topology around the vertex is known:
                associated_cells.sort()
                for k in vtx2cells[t].keys(): 
                    if len(set(vtx2cells[t][k])&set(associated_cells)) == len(associated_cells):
                        v2v[k] = vtx
        vtx_time_association.append(v2v)
    
    if return_cells_vertices_relations:
        return vtx_time_association, cell2vertices, vtx2coords, vtx2cells
    else:
        return vtx_time_association


def __strain_parameters(func):
    def wrapped_function(graph, vids = None, use_projected_anticlinal_wall = False, verbose = False):
        """
        :Parameters:
         - `graph` (TPG)
         - `vids` (int|list) - list of (graph) vertex ids @ t_n. If :None: it will be computed for all possible vertex
         - `use_projected_anticlinal_wall` (bool) - if True, use the medians of projected anticlinal wall ('projected_anticlinal_wall_median') to compute a strain in 2D.
        """
        # Check if cells landmarks have been recovered ans stored in the graph structure:
        if use_projected_anticlinal_wall:
            assert 'projected_anticlinal_wall_median' in graph.edge_property_names()
        else:
            assert 'wall_median' in graph.edge_property_names()
            assert 'unlabelled_wall_median' in graph.vertex_property_names()
            assert 'epidermis_wall_median' in graph.vertex_property_names()

        # -- If the vid is not associated through time it's not possible to compute the strain.
        if vids is None:
            vids = graph.vertices()
        if isinstance(vids,int):
            vids=[vids]

        # -- If the vid is not associated through time it's not possible to compute the strain.
        for vid in vids:
            if graph.descendants(vid, 1) == set([vid]):
                vids.remove(vid)

        spatial_vertices_edge = dict( ((min(v[0],v[1]),max(v[0],v[1])),k) for k,v in graph._edges.iteritems() if k in graph.edges(edge_type='s'))
        # Next line need to be changed: we should create a smaller dict by looking in something smaller than all graphs edges!!!
        wall_median_2 = dict( ( (min(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1]),max(graph.edge_vertices(eid)[0],graph.edge_vertices(eid)[1])) ,graph.edge_property('wall_median')[eid]) for eid in graph.edges(edge_type='s') if graph.edge_property('wall_median').has_key(eid) )
        strain_mat = {}
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
                if use_projected_anticlinal_wall:
                    strain_mat[vid] = func(graph, xyz_t1, xyz_t2, N, dimension = 2, deltaT = time_interval )
                else:
                    strain_mat[vid] = func(graph, xyz_t1, xyz_t2, N, dimension = 3, deltaT = time_interval )

        return strain_mat

    return  wrapped_function

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

@__strain_parameters
def strain_matrix(graph, xyz_t1, xyz_t2, N, dimension, deltaT):
    """
    Compute the strain matrix.
    """
    # -- We start by making sure we can compute the strain matrix in the dimensionnality provided.
    if (dimension > 3) or (dimension < 1) :
        import warnings
        warnings.warn("You can only compute the strain in 1D, 2D or 3D!")
        return None

    ## Compute the centroids:
    c_t1 = np.mean(xyz_t1,0)
    c_t2 = np.mean(xyz_t2,0)
    ## Compute the centered matrix:
    c_xyz_t1=np.array(xyz_t1-c_t1)
    c_xyz_t2=np.array(xyz_t2-c_t2)
    ## Compute the Singular Value Decomposition (SVD) of centered coordinates:
    U_t1,D_t1,V_t1=svd(c_xyz_t1, full_matrices=False)
    U_t2,D_t2,V_t2=svd(c_xyz_t2, full_matrices=False)
    V_t1=V_t1.T ; V_t2=V_t2.T
    ## Projection of the vertices' xyz 3D co-ordinate into the 2D subspace defined by the 2 first eigenvector
    #(the third eigenvalue is really close from zero confirming the fact that all the vertices are close from the plane -true for external part of L1, not for inner parts of the tissue).
    c_xy_t1=np.array([np.dot(U_t1[k,0:dimension],np.diag(D_t1)[0:dimension,0:dimension]) for k in range(N)])
    c_xy_t2=np.array([np.dot(U_t2[k,0:dimension],np.diag(D_t2)[0:dimension,0:dimension]) for k in range(N)])
    ## Least-square estimation of A.
    #A is the transformation matrix in the regression equation between the centered vertices position of two time points:
    lsq=lstsq(c_xy_t1,c_xy_t2)
    A=lsq[0]

    return A

def strain_rate(graph, strain_mat):
    """
    Compute the strain rate: sr[c] = np.log(D_A[0])/deltaT , np.log(D_A[1])/deltaT
    Dimensionnality is imposed by the one of the strain matrix.
    """
    sr = {}
    for vid in strain_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(strain_mat[vid])
        # Compute Strain Rates :
        sr[vid] = np.log(D_A)/float(time_interval(graph, vid, rank =1))

    return sr

def areal_strain_rate(graph, strain_mat):
    """
    Compute the areal strain rate: asr[c] = sum(np.log(D_A[0])/deltaT, np.log(D_A[1])/deltaT)
    Dimensionnality is imposed by the one of the strain matrix.
    """
    asr = {}
    for vid in strain_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q=svd(strain_mat[vid])
        # Compute Strain Rates and Areal Strain Rate:
        asr[vid] = sum(np.log(D_A)/float(time_interval(graph, vid, rank =1)))

    return asr

def strain_anisotropy(graph, strain_mat):
    """
    Compute the "Growth" Anisotropy = (sr1-sr2)/(sr1+sr2)
    Dimensionnality is imposed by the one of the strain matrix.
    """
    anisotropy = {}
    for vid in strain_mat:
        ##  Singular Value Decomposition (SVD) of A.
        R,D_A,Q = svd(strain_mat[vid])
        # Compute Strain Rates :
        strain_rate = np.log(D_A)/float(time_interval(graph, vid, rank =1))
        anisotropy[vid] = (strain_rate[0]-strain_rate[1])/(strain_rate[0]+strain_rate[1])

    return anisotropy

@__strain_parameters
def strain_cross(graph, xyz_t1, xyz_t2, dimension, N):
    """

    """
    # -- We start by making sure we can compute the strain matrix in the dimensionnality provided.
    if (dimension > 3) or (dimension < 1) :
        import warnings
        warnings.warn("You can only compute the strain in 1D, 2D or 3D!")
        return None

    ## Compute the centroids:
    c_t1 = np.mean(xyz_t1,0)
    c_t2 = np.mean(xyz_t2,0)
    ## Compute the centered matrix:
    c_xyz_t1=np.array(xyz_t1-c_t1)
    c_xyz_t2=np.array(xyz_t2-c_t2)
    ## Compute the Singular Value Decomposition (SVD) of centered coordinates:
    U_t1,D_t1,V_t1=svd(c_xyz_t1, full_matrices=False)
    U_t2,D_t2,V_t2=svd(c_xyz_t2, full_matrices=False)
    V_t1=V_t1.T ; V_t2=V_t2.T
    ## Projection of the vertices' xyz 3D co-ordinate into the 2D subspace defined by the 2 first eigenvector
    #(the third eigenvalue is really close from zero confirming the fact that all the vertices are close from the plane -true for external part of L1, not for inner parts of the tissue).
    c_xy_t1=np.array([np.dot(U_t1[k,0:dimension],np.diag(D_t1)[0:dimension,0:dimension]) for k in range(N)])
    c_xy_t2=np.array([np.dot(U_t2[k,0:dimension],np.diag(D_t2)[0:dimension,0:dimension]) for k in range(N)])
    ## Compute the Singular Value Decomposition (SVD) of the least-square estimation of A.
    #A is the (linear) transformation matrix in the regression equation between the centered vertices position of two time points:
    lsq=lstsq(c_xy_t1,c_xy_t2)
    ##  Singular Value Decomposition (SVD) of A.
    R,D_A,Q=svd(lsq[0])
    Q=Q.T
    ##  Getting back in 3D: manually adding an extra dimension.
    R=np.hstack([np.vstack([R,[0,0]]),[[0],[0],[1]]])
    D_A=np.hstack([np.vstack([np.diag(D_A),[0,0]]),[[0],[0],[0]]])
    Q=np.hstack([np.vstack([Q,[0,0]]),[[0],[0],[1]]])
    ##  Getting back in 3D: strain of cell c represented at each time point.
    s_t1 = np.dot(np.dot(np.dot(np.dot(V_t1, R), D_A), R.T), V_t1.T)
    s_t2 = np.dot(np.dot(np.dot(np.dot(V_t2, Q), D_A), Q.T), V_t2.T)

    return s_t1,s_t2

def time_interval(graph,vid,rank=1):
    """
    Compute the time interval for the vexterx id `vid` thanks to data saved in graph.graph_property('time_steps').
    """
    index_1 = graph.vertex_property('index')[vid]
    return (graph.graph_property('time_steps')[index_1+rank]-graph.graph_property('time_steps')[index_1])

#~ def display_lignage(graph, ini):
    
#~ def strain2D(graph, tp_1, tp_2):
    #~ """
    #~ Strain computation based on the 3D->2D->3D GOODALL method.
    #~ 
    #~ :INPUTS:
        #~ .t1: t_n Spatial Image containing cells (segmented image)
        #~ .t2: t_n+1 Spatial Image containing cells (segmented image)
        #~ .l12: lineage between t_n & t_n+1;
        #~ .l21: INVERTED lineage between t_n & t_n+1;
        #~ .deltaT: time interval between two time points;
        #~ 
    #~ :Variables:
        #~ .v2v_21: vertex (keys=t_n+1) to vertex (values=t_n) association.
        #~ .c2v_1: cells 2 vertex @ t_n
        #~ .v2b_1: vextex 2 barycenters @ t_n
        #~ .v2b_2: vextex 2 barycenters @ t_n+1
    #~ 
    #~ :OUTPUTS: (c= keys= mother cell number)
        #~ .sr[c]: Strain Rate = np.log(D_A[0])/deltaT , np.log(D_A[1])/deltaT
        #~ .asr[c]: Areal Strain Rate = (sr1+sr2)
        #~ .anisotropy[c]: Growth Anisotropy = (sr1-sr2)/(sr1+sr2)
        #~ .s_t1[c]: t_n strain cross in 3D (tensor)
        #~ .s_t2[c]: t_n+1 strain cross in 3D (tensor)
    #~ 
    #~ ########## Relationship between least-squares method and principal components: ##########
    #~ ## The first principal component about the mean of a set of points can be represented by that line which most closely approaches the data points 
    #~ #(as measured by squared distance of closest approach, i.e. perpendicular to the line).
    #~ ## In contrast, linear least squares tries to minimize the distance in the y direction only.
    #~ ## Thus, although the two use a similar error metric, linear least squares is a method that treats one dimension of the data preferentially, while PCA treats all dimensions equally.
    #~ #########################################################################################
    #~ """
    #~ from numpy.linalg import svd, lstsq
#~ 
    #~ ## Variable creation used to comput the strain.
    #~ v2v_12 = dict((v,k) for k, v in v2v_21.items())
    #~ lsq={}
    #~ s_t1,s_t2={},{}
    #~ sr={}
    #~ asr={}
    #~ anisotropy={}
#~ 
    #~ for c in l12.keys():
        #~ if c in c2v_1.keys():
            #~ if sum([(c2v_1[c][k] in v2v_12.keys()) for k in range(len(c2v_1[c]))])==len(c2v_1[c]):
                #~ N = len(c2v_1[c])
                #~ if N>2:
                    #~ ## Retreive positions of the vertices belonging to cell 'c':
                    #~ xyz_t1=np.array([v2b_1[c2v_1[c][k]] for k in range(N)])
                    #~ xyz_t2=np.array([v2b_2[v2v_12[c2v_1[c][k]]] for k in range(N)])
                    #~ ## Compute the centroids:
                    #~ c_t1=np.array((np.mean(xyz_t1[:,0]),np.mean(xyz_t1[:,1]),np.mean(xyz_t1[:,2])))
                    #~ c_t2=np.array((np.mean(xyz_t2[:,0]),np.mean(xyz_t2[:,1]),np.mean(xyz_t2[:,2])))
                    #~ ## Compute the centered matrix:
                    #~ c_xyz_t1=np.array(xyz_t1-c_t1)
                    #~ c_xyz_t2=np.array(xyz_t2-c_t2)
                    #~ ## Compute the Singular Value Decomposition (SVD) of centered coordinates:
                    #~ U_t1,D_t1,V_t1=svd(c_xyz_t1, full_matrices=False)
                    #~ U_t2,D_t2,V_t2=svd(c_xyz_t2, full_matrices=False)
                    #~ V_t1=V_t1.T ; V_t2=V_t2.T
                    #~ ## Projection of the vertices' xyz 3D co-ordinate into the 2D subspace defined by the 2 first eigenvector
                    #~ #(the third eigenvalue is really close from zero confirming the fact that all the vertices are close from the plane -true for external part of L1, not for inner parts of the tissue).
                    #~ c_xy_t1=np.array([np.dot(U_t1[k,0:2],np.diag(D_t1)[0:2,0:2]) for k in range(N)])
                    #~ c_xy_t2=np.array([np.dot(U_t2[k,0:2],np.diag(D_t2)[0:2,0:2]) for k in range(N)])
                    #~ ## Compute the Singular Value Decomposition (SVD) of the least-square estimation of A.
                    #~ #A is the (linear) transformation matrix in the regression equation between the centered vertices position of two time points:
                    #~ lsq[c]=lstsq(c_xy_t1,c_xy_t2)
                    #~ ##  Singular Value Decomposition (SVD) of A.
                    #~ R,D_A,Q=svd(lsq[c][0])
                    #~ Q=Q.T
                    #~ # Compute Strain Rates and Areal Strain Rate:
                    #~ sr[c] = np.log(D_A)/deltaT
                    #~ asr[c] = sum(sr[c])
                    #~ anisotropy[c]=((sr[c][0]-sr[c][1])/asr[c])
                    #~ ##  Getting back in 3D: manually adding an extra dimension.
                    #~ R=np.hstack([np.vstack([R,[0,0]]),[[0],[0],[1]]])
                    #~ D_A=np.hstack([np.vstack([np.diag(D_A),[0,0]]),[[0],[0],[0]]])
                    #~ Q=np.hstack([np.vstack([Q,[0,0]]),[[0],[0],[1]]])
                    #~ ##  Getting back in 3D: strain of cell c represented at each time point.
                    #~ s_t1[c] = np.dot(np.dot(np.dot(np.dot(V_t1, R), D_A), R.T), V_t1.T)
                    #~ s_t2[c] = np.dot(np.dot(np.dot(np.dot(V_t2, Q), D_A), Q.T), V_t2.T)
#~ 
    #~ return sr,asr,anisotropy,s_t1,s_t2



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


