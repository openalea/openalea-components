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

def distance_matrix_from_vector(data, variable_types, no_dist_index = []):
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
                if i in no_dist_index or j in no_dist_index:
                    dist_mat[i,j] = dist_mat[j,i] = 0
                else:
                    dist_mat[i,j] = i-j
                    dist_mat[j,i] = j-i

    if variable_types == "Ordinal":
        rank = data.argsort() # In case of ordinal variables, observed values are replaced by ranked values.
        for i in xrange(N):
            for j in xrange(i+1,N): # we skip when i=j because in that case the distance is 0.
                if i in no_dist_index or j in no_dist_index:
                    dist_mat[i,j] = dist_mat[j,i] = 0
                else:
                    dist_mat[i,j] = rank[i]-rank[j]
                    dist_mat[j,i] = rank[j]-rank[i]

    return dist_mat


def standardisation(data, norm, variable_types=None):
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
    Defines for each vertex the neighbouring vertex following a given structure of the data.

    :Parameters:
     - `graph` (Graph | PropertyGraph | TemporalPropertyGraph) - graph from which to extract connectivity.
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
     - `graph` (Graph | PropertyGraph | TemporalPropertyGraph) - graph from wich to extract spatial, spatio-temporal and topological/euclidean distance variables.
     - `variable_list` (list) - list of `vertex_property_names` related to spatial information (ex. volume).
     - `variable_weights` (list) - list of weights related to spatial information (ex. volume). If only an integer is given for several variables (in `variable_list`), we divide it by the number of variables in `variable_list`.
     - `variable_types` (list) - list of variable types. Can be "Ordinal" or "Numeric".
     - `spatial_weight` (int) - weight related to topological/euclidian distance.
     - `temporal_list` (list) - list of `vertex_property_names` related to spatio-temporal information (ex. volumetric growth).
     - `temporal_weights` (list) - list of weights related to spatio-temporal information (ex. volumetric growth). If only an integer is given for several variables (in `temporal_list`), we divide it by the number of variables in `temporal_list`.

    :NOTE:
     - We use :ABSOLUTE: temporal change (from openalea.container.temporal_graph_analysis import temporal_change)!
     - We assign temporal change to t_n+1.
     - One can privide a vector (type list) of spatial or/and spatio-temporal data => NEED to be detected before creating the `vtx_list` and would force to provide this list of vertices!!! (or we could use a dictionary)  NOT DONE YET !!!
    """
    # -- Taking care of stupid cases:
    if spatial_weight == 1:
        print("No need to do that: no topological/euclidian distance between each time point!!")
        return None

    # -- Making sure all spatial variable asked for in `variable_list` are present in the `graph`:
    for variable_name in variable_list:
        if isinstance(variable_name,str):
            assert variable_name in graph.vertex_property_names()

    # -- Handling multiple types of inputs:
    if isinstance(variable_weights,int) or isinstance(variable_weights,float): 
        variable_weights = [variable_weights]
    if isinstance(variable_list,str): variable_list = [variable_list]
    nb_variables = len(variable_list)
    if isinstance(variable_types,str): variable_types = [variable_types]
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
    min_index = min(graph.vertex_property('index').values())
    max_index = max(graph.vertex_property('index').values())
    if nb_temporal_variables != 0:
        print "Make sure the rank you provided is equal (or superior) to the one you used to compute spatio-temporal properties !!"
    vtx_list = [vid for vid in graph.vertices() if exist_relative_at_rank(graph, vid, rank) or exist_relative_at_rank(graph, vid, -rank)] #we keep vertex ids only if they are temporally linked in the graph at `rank`
    N = len(vtx_list)

    index = dict( (vid,graph.vertex_property('index')[vid]) for vid in vtx_list )
    #~ nb_individuals_index = [sum(np.array(index.values())==t) for t in xrange(max_index)]

    # -- We compute the standardized distance matrix related to spatial variables:
    if nb_variables != 0:
        variable_standard_distance_matrix = {}
        for n, variable_name in enumerate(variable_list):
            if isinstance(variable_name,str):
                variable_vector = [graph.vertex_property(variable_name)[vid] for vid in vtx_list]
            if isinstance(variable_name,dict):
                variable_vector = [variable_name[vid] for vid in vtx_list]
            variable_standard_distance_matrix[temporal_name] = standardisation(variable_vector, standardisation_method, variable_types[n])

    # -- We compute the standardized distance matrix related to temporal variables:
    vtx_with_no_temporal_data = []
    if nb_temporal_variables != 0:
        # If we want to work with temporally differentiated variables, we need to find vertex without a mother (since we assign spatio-temporal variable @ t_n+1):
        #    - those from the first time step
        #    - those from other time steps which doesnt have a mother
        vtx_with_no_temporal_data = [vid for vid in vtx_list if graph.vertex_property('index')[vid]==0 or (graph.vertex_property('index')[vid]>0 and not exist_relative_at_rank(graph, vid, -rank))]
        index_vtx_with_no_temporal_data = [vtx_list.index(k) for k in vtx_with_no_temporal_data]
        from openalea.container.temporal_graph_analysis import temporal_change
        temporal_standard_distance_matrix = {}
        for n, temporal_name in enumerate(temporal_list):
            if isinstance(temporal_name,dict):
                if sum([True if temporal_name.has_key(vid) or vid in vtx_with_no_temporal_data else False for vid in vtx_list])!=N:
                    warnings.warn("Some temporally linked vertex ids are missing in your temporal dictionary #%d !!" %n)
                    return None
                dict_temporal = temporal_name
            if isinstance(temporal_name,str):
                dict_temporal = temporal_change(graph, temporal_name, [vid for vid in vtx_list if index[vid]<max_index], rank, labels_at_t_n = False)
            temporal_distance_list = []
            for vid in vtx_list:# we need to do that if we want: len(temporal_distance_list) == N
                if dict_temporal.has_key(vid):
                    temporal_distance_list.append(dict_temporal[vid])
                if vid in vtx_with_no_temporal_data:
                    temporal_distance_list.append(0)
            temporal_standard_distance_matrix[temporal_name] = standardisation(distance_matrix_from_vector(temporal_distance_list, temporal_types[n], index_vtx_with_no_temporal_data), standardisation_method)

    # -- We compute the standardized topological distance matrix:
    if spatial_weight != 0:
        import time
        t = time.time()
        topological_distance = dict( ((vid, graph.topological_distance(vid, 's', full_dict=False))) for vid in vtx_list )
        print "Time to compute the topological distances : %f s" % (time.time() - t)
        topo_dist_rank = np.zeros( [N,N], dtype=float )
        # we suppose here that we have the topological distance of a vertex from itself (i.e. 0)
        for i,vid in enumerate(vtx_list):
            for j,vid2 in enumerate(vtx_list):
                if i != j and topological_distance[vid].has_key(vid2):
                    topo_dist_rank [i,j] = topological_distance[vid][vid2]

        topo_dist_rank_standard = standardisation(topo_dist_rank ,standardisation_method ,"Ordinal")
    else:
        topo_dist_rank_standard = np.zeros( [N,N], dtype=int )
  
    # -- If sum(temporal_weights)==1 : there is no spatial nor topological data to 're-norm'...
    if sum(temporal_weights) == 1:
        warnings.warn("You have asked only for a distance matrix based on temporally differentiated variables. There will be no distance for the first time-point!")
        D = sum([temporal_weights[n]*temporal_standard_distance_matrix[e] for n,e in enumerate(temporal_list)])
        return vtx_list, D

    D = np.zeros( shape = [N,N], dtype=float )
    for i,vid1 in enumerate(vtx_list):
        for j,vid2 in enumerate(vtx_list):
            if i>j: #D[i,j]=D[j,i] and if i==j, D[i,j]=D[j,i]=0
                # -- Case where one of the vertex doesn't have a spatio-temporal data assigned :
                if (vid1 in vtx_with_no_temporal_data or vid2 in vtx_with_no_temporal_data):
                    D[i,j] = D[j,i] = (spatial_weight/(1-sum(temporal_weights))) * topo_dist_rank_standard[i,j] + sum([(variable_weights[n]/(1-sum(temporal_weights)))*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)])
                # -- Case where both vertices belong to the same time_step ('index'): we use all information available.
                elif index[vid1] == index[vid2]:
                    D[i,j] = D[j,i] = spatial_weight * topo_dist_rank_standard[i,j] + sum([variable_weights[n]*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)]) + sum([temporal_weights[n]*temporal_standard_distance_matrix[e][i,j] for n,e in enumerate(temporal_list)])
                # -- Case where vertices doesn't belong to the same time_step ('index'): we need to 're-norm' because there is no topological/euclidean distance
                elif index[vid1] != index[vid2]:
                    D[i,j] = D[j,i] = sum([(variable_weights[n]/(1-spatial_weight))*variable_standard_distance_matrix[e][i,j] for n,e in enumerate(variable_list)]) + sum([(temporal_weights[n]/(1-spatial_weight))*temporal_standard_distance_matrix[e][i,j] for n,e in enumerate(temporal_list)])
                else:
                    print "UH-OH!!!, vids: ", [vid1, vid2]

    return vtx_list, D

