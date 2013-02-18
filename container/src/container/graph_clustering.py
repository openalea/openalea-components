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
"""This module helps to use clustering and standardization methods on graphs."""

import warnings
import numpy as np
from numpy import ndarray

from openalea.container.temporal_graph_analysis import exist_relative_at_rank

def distance_matrix_from_vector(data, variable_types):
    """
    Function creating a distance matrix based on a vector (list) of values.
    Each values are attached to an individual.

    :Parameters:
     - `data` (list) - vector/list of value
     - `variable_types` (str) - type of variable

    :Returns:
     - `dist_mat` (np.array) - distance matrix
    """
    N = len(data)
    dist_mat = np.zeros( shape = [N,N], dtype=float )

    if variable_types == "Numeric":
        for i in xrange(N):
            for j in xrange(i+1,N):# we skip when i=j because in that case the distance is 0.
                dist_mat[i,j] = i-j
                dist_mat[j,i] = j-i

    if variable_types == "Ordinal":
        rank = data.argsort() # In case of ordinal variables, observed values are replaced by ranked values.
        for i in xrange(N):
            for j in xrange(i+1,N): # we skip when i=j because in that case the distance is 0.
                dist_mat[i,j] = rank[i]-rank[j]
                dist_mat[j,i] = rank[j]-rank[i]

    return dist_mat


def standardisation(data, norm, variable_types):
    """
    :Parameters:
     - `mat` (np.array) - distance matrix
     - `norm` (str) - "L1" or "L2", select which standarisation metric to apply to the data;
     - `variable_types` (str) - "Numeric" or "Ordinal" or "Interval"
    
    :Returns:
     - `standard_mat` (np.array) - standardized distance matrix
    """
    
    if (norm != 'L1') and (norm != 'L2'):
        warnings.warn("Undefined standardisation metric")

    if isinstance(data,ndarray) and (((data.shape[1] == 1) and (data.shape[0] > 1)) or ((data.shape[1] == 1) and (data.shape[0] > 1))):
        data.tolist()

    if isinstance(data,list):
        print "You provided a vector of variable, we compute the distance matrix first !"
        N = len(data)
        distance_matrix = distance_matrix_from_vector(data, variable_types)

    if isinstance(data,ndarray) and (data.shape[0]==data.shape[1]) and ((data.shape[0]!=1)and(data.shape[1]!=1)):
        print "You provided a distance matrix !"
        distance_matrix = data
        N = distance_matrix.shape[0]

    if norm == "L1":
        absd = sum(sum(abs(distance_matrix))) / (N*(N-1))
        return distance_matrix / absd

    if norm == "L2":
        sd = sum(sum(distance_matrix**2)) / (N*(N-1))
        return distance_matrix / sd


def standardisation_scikit(data, norm, variable_types):
    """
    :Parameters:
     - `mat` (np.array) - distance matrix
     - `norm` (str) - "L1" or "L2", select which standarisation metric to apply to the data;
     - `variable_types` (str) - "Numeric" or "Ordinal" or "Interval"
    
    :Returns:
     - `standard_mat` (np.array) - standardized distance matrix
    """
    if (norm != 'L1') and (norm != 'L2'):
        warnings.warn("Undefined standardisation metric")

    X = distance_matrix_from_vector(data, variable_types)

    from sklearn import preprocessing

    if norm == "L1":
        return preprocessing.normalize(X, norm='l1')

    if norm == "L2":
        return preprocessing.normalize(X, norm='l2')


def weighted_distance_matrix(distance_matrix_list, weights_list):
    """
    Compute a distance matrix from a list of distance matrix and a list of weight:
        D_w = sum_i(w_i * D_i); where sum_i(w_i) = 1.
    """
    if sum(weights_list) != 1:
        warnings.warn("The weights do not sum to 1 !")
        return None

    if len(distance_matrix_list) != len(weights_list):
        warnings.warn("You did not provided the same number of distance matrix and weigths !")
        return None

    # weighted_matrix initialisation:
    weighted_matrix = distance_matrix_list[0].copy()
    weighted_matrix.fill(0)
    for n, weigth in enumerate(weights_list):
        weighted_matrix += weigth * distance_matrix_list[n]

    return weighted_matrix


def csr_matrix_from_graph(graph, vids2keep):
    """
    Create a sparse matrix representing a connectivity matrix recording the topological information of the graph.
    Defines for each vertex the neigbhoring vertex following a given structure of the data.

    :Parameters:
     - `graph` (Graph | PropertyGraph | TemporalPropertyGraph) - graph from wich to extract connectivity.
     - `vids2keep` (list) - list of vertex ids to build the sparse matrix from (columns and rows will be ordered according to this list).
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


def weighted_global_distance_matrix(graph, variable_list=[], variable_weights=[], variable_types=[], spatial_weight=0, temporal_list=[], temporal_weights=[], temporal_types=[], standardisation_method = "L1", only_lineaged_vertices = True, rank = 1 ):
    """
    :Parameters:
     - `graph` (Graph | PropertyGraph | TemporalPropertyGraph) - graph from wich to extract spatial, spatio-temporal and topological/euclidian distance variables.
     - `variable_list` (list) - list of `vertex_property_names` related to spatial information (ex. volume).
     - `variable_weights` (list) - list of weights related to spatial information (ex. volume). If only an integer is given for several variables (in `variable_list`), we divide it by the number of variables in `variable_list`.
     - `variable_types` (list) - list of variable types. Can be "Ordinal" or "Numeric".
     - `spatial_weight` (int) - weight related to topological/euclidian distance.
     - `temporal_list` (list) - list of `vertex_property_names` related to spatio-temporal information (ex. volumetric growth).
     - `temporal_weights` (list) - list of weights related to spatio-temporal information (ex. volumetric growth). If only an integer is given for several variables (in `temporal_list`), we divide it by the number of variables in `temporal_list`.

    :NOTE: We use :ABSOLUTE: temporal change !
    """
    # -- Treating stupid cases:
    if spatial_weight == 1:
        print("No need to do that: no topological/euclidian distance between each time point!!")
        return None

    # -- Making sure all spatial variable asked for in `variable_list` are present in the `graph`:
    for variable_name in variable_list:
        assert variable_name in graph.vertex_property_names()

    # -- Handling multiple types of inputs:
    if isinstance(variable_list,str): variable_list = [variable_list]
    if isinstance(variable_types,str): variable_types = [variable_types]
    nb_variables = len(variable_list)
    if isinstance(variable_weights,int) or isinstance(variable_weights,float): 
        variable_weights = [variable_weights]
    # - If only an integer is given for several variables (in `variable_list`), we divide it by the number of variables in `variable_list`:
    if nb_variables != 0 and len(variable_weights)!=nb_variables:
        variable_weights = [variable_weights / float(nb_variables)]
        for i in xrange(nb_variables-1):
            variable_weights.append(variable_weights)

    # -- Handling multiple types of inputs:
    if isinstance(temporal_list,str): temporal_list = [temporal_list]
    if isinstance(temporal_types,str): temporal_types = [temporal_types]
    nb_temporal_variables = len(temporal_list)
    if isinstance(temporal_weights,int) or isinstance(temporal_weights,float):
        temporal_weights = [temporal_weights]
    # - If only an integer is given for several temporal variables (in `temporal_list`), we divide it by the number of temporal variable in `temporal_list`:
    if nb_temporal_variables != 0 and len(temporal_weights)!=nb_temporal_variables:
        temporal_weights = [temporal_weights / float(nb_temporal_variables)]
        for i in xrange(nb_temporal_variables-1):
            temporal_weights.append(temporal_weights)

    assert sum(variable_weights)+sum(temporal_weights)+spatial_weight==1

    # -- Creating the list of vertices:
    nb_time_points = max(graph.vertex_property('index').values())+1
    if temporal_weights == []:
        print "Make sure the rank you provided is equal (or superior) to the one you used to compute spatio-temporal properties !!"
    vtx_list = [vid for vid in graph.vertices() if (graph.vertex_property('index')[vid]<nb_time_points-1 and exist_relative_at_rank(graph, vid, rank)) or (graph.vertex_property('index')[vid]==nb_time_points-1 and exist_relative_at_rank(graph, vid, -rank))] #we keep vertex ids only if they are temporally linked in the graph at `rank`
    N = len(vtx_list)

    index = dict( (vid,graph.vertex_property('index')[vid]) for vid in vtx_list )
    #~ nb_individuals_index = [sum(np.array(index.values())==t) for t in xrange(nb_time_points)]

    # -- We compute the standardized distance matrix related to spatial variables:
    if nb_variables != 0:
        variable_standard_distance_matrix = {}
        for n, variable_name in enumerate(variable_list):
            variable_standard_distance_matrix[variable_name] = standardisation([graph.vertex_property(variable_name)[vid] for vid in vtx_list],standardisation_method, variable_types[n])

    # -- We compute the standardized distance matrix related to temporal variables:
    if nb_temporal_variables != 0:
        from openalea.container.temporal_graph_analysis import temporal_change
        temporal_standard_distance_matrix = {}
        for n, temporal_name in enumerate(temporal_list):
            temporal_standard_distance_matrix[temporal_name] = standardisation([temporal_change(graph, temporal_name, vids = vid, rank = rank, labels_at_t_n = False, check_full_lineage = True) for vid in vtx_list if exist_relative_at_rank(graph, vid, rank)], standardisation_method, temporal_types[n])

    # -- We compute the standardized topological distance matrix:
    if spatial_weight != 0:
        import time
        t = time.time()
        topological_distance = dict( ((vid, graph.topological_distance(vid, 's', full_dict=False))) for vid in vtx_list )
        print "Time to compute the topological distance matrix: %f s" % (time.time() - t)

        topo_dist_rank = np.zeros( [N,N], dtype=float )
        # we suppose here that we have the topological distance of a vertex from itself (i.e. 0)
        for i,vid in enumerate(vtx_list):
            for j,vid2 in enumerate(vtx_list):
                if i != j and topological_distance[vid].has_key(vid2):
                    topo_dist_rank [i,j] = topological_distance[vid][vid2]

        topo_dist_rank_standard = standardisation(topo_dist_rank ,standardisation_method ,"Ordinal")
    else:
        topo_dist_rank_standard = np.zeros( [N,N], dtype=int )

    D = np.zeros( shape = [N,N], dtype=float )
    if sum(temporal_weights)== 1:
        warnings.warn("You have asked only for temporally differenciated variables. There will be no distance for the first time-point!")
    for i,vid1 in enumerate(vtx_list):
        for j,vid2 in enumerate(vtx_list):
            if i>j:
                if sum(temporal_weights)!= 1 and (index[vid1] == rank or index[vid2]==rank):
                    D[i,j] = D[j,i] = (spatial_weight/(1-sum(temporal_weights))) * topo_dist_rank_standard[i,j] + sum([(variable_weights[n]/(1-sum(temporal_weights)))*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)])
                if index[vid1] != rank and index[vid1] == index[vid2]:
                    D[i,j] = D[j,i] = spatial_weight * topo_dist_rank_standard[i,j] + sum([variable_weights[n]*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)]) + sum([temporal_weights[n]*temporal_standard_distance_matrix[e][i,j] for n,e in enumerate(temporal_list)])
                if index[vid1]!=rank and index[vid2]!=rank and index[vid1] != index[vid2]:
                    D[i,j] = D[j,i] = sum([(variable_weights[n]/(1-spatial_weight))*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)]) + sum([(temporal_weights[n]/(1-spatial_weight))*temporal_standard_distance_matrix[e][i,j] for n,e in enumerate(temporal_list)])

    return vtx_list, D

