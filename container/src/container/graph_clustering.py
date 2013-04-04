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
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.axes3d import Axes3D

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
    if isinstance(variable_list,str):
        assert variable_list in graph.vertex_property_names()
    if isinstance(variable_list,list):
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
            variable_standard_distance_matrix[variable_name] = standardisation(variable_vector, standardisation_method, variable_types[n])

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


def cluster_distance_matrix( distance_matrix, clustering ):
    """
    Function computing distance between clusters.
    For $\ell \eq q$  :
    \[ D(q,\ell) = \dfrac{ \sum_{i,j \in q; i \neq j} D(i,j) }{(N_{q}-1)N_{q}} , \]
    For $\ell \neq q$  :
    \[ D(q,\ell) = \dfrac{ \sum_{i \in q} \sum_{j \in \ell} D(i,j) }{N_{q} N_{\ell} } , \]
    where $D(i,j)$ is the distance matrix, $N_{q}$ and $N_{\ell}$ are the number of elements found in clusters $q$ and $\ell$.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    D = np.zeros( shape = [nb_clusters,nb_clusters], dtype = float )
    for n,q in enumerate(clusters_ids):
        for m,l in enumerate(clusters_ids):
            if n==m:
                index_q = np.where(clustering == q)[0]
                D[n,m] = sum( [distance_matrix[i,j] for i in index_q for j in index_q if i!=j] ) / ( (nb_ids_by_clusters[n]-1) * nb_ids_by_clusters[n])
            if n>m:
                index_q = np.where(clustering == q)[0]
                index_l = np.where(clustering == l)[0]
                D[n,m] = D[m,n]= sum( [distance_matrix[i,j] for i in index_q for j in index_l] ) / (nb_ids_by_clusters[n] * nb_ids_by_clusters[m])

    return D


def within_cluster_distance(distance_matrix, clustering):
    """
    Function computing within cluster distance.
    $$ D(q) = \dfrac{ \sum_{i,j \in q; i \neq j} D(i,j) }{(N_{q}-1)N_{q}} ,$$
    where $D(i,j)$ is the distance matrix, $N$ is the total number of elements and $N_{q}$ is the number of elements found in clusters $q$.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    D_within = {}
    for n,q in enumerate(clusters_ids):
        index_q = np.where(clustering == q)[0]
        D_within[q] = 2. * sum( [distance_matrix[i,j] for i in index_q for j in index_q if j>i] ) / ( (nb_ids_by_clusters[n]-1) * nb_ids_by_clusters[n])

    if nb_clusters == 1:
        return D_within.values()
    else:
        return D_within


def between_cluster_distance(distance_matrix, clustering):
    """
    Function computing within cluster distance.
    $$ D(q) = \dfrac{ \sum_{i \in q} \sum_{j \not\in q} D(i,j) }{ (N - N_q) N_q }, $$
    where $D(i,j)$ is the distance matrix, $N$ is the total number of elements and $N_{q}$ is the number of elements found in clusters $q$.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    D_between = {}
    for n,q in enumerate(clusters_ids):
        index_q = np.where(clustering == q)[0]
        index_not_q = list(set(xrange(len(clustering)))-set(index_q))
        D_between[q] = sum( [distance_matrix[i,j] for i in index_q for j in index_not_q] ) / ( (N-nb_ids_by_clusters[n]) * nb_ids_by_clusters[n])

    if nb_clusters == 1:
        return D_between.values()
    else:
        return D_between


def cluster_diameters(distance_matrix, clustering):
    """
    Function computing within cluster diameter, i.e. the max distance between two vertex from the same cluster.
    $$ \max_{i,j \in q} D(j,i) ,$$
    where $D(i,j)$ is the distance matrix and $q$ a cluster, .
    
    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)

    diameters = {}
    for q in clusters_ids:
        index_q = np.where(clustering == q)[0]
        diameters[q] = max([distance_matrix[i,j] for i in index_q for j in index_q])

    if nb_clusters == 1:
        return diameters.values()
    else:
        return diameters


def clusters_separation(distance_matrix, clustering):
    """
    Function computing within cluster diameter, i.e. the min distance between two vertex from two diferent clusters.
    $$ \min_{i \in q, j \not\in q} D(j,i) ,$$
    where $D(i,j)$ is the distance matrix and $q$ a cluster.
    
    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)

    separation = {}
    for q in clusters_ids:
        index_q = np.where(clustering == q)[0]
        index_not_q = np.where(clustering != q)[0]
        separation[q] = min([distance_matrix[i,j] for i in index_q for j in index_not_q ])

    if nb_clusters == 1:
        return separation.values()
    else:
        return separation


def global_cluster_distance(distance_matrix, clustering):
    """
    Function computing global cluster distances, i.e. return the sum of within_cluster_distance and between_cluster_distance.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    w = within_cluster_distance(distance_matrix, clustering)
    b = between_cluster_distance(distance_matrix, clustering)

    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    gcd_w = sum( [ (nb_ids_by_clusters[q]*(nb_ids_by_clusters[q]-1))/float(sum([nb_ids_by_clusters[l]*(nb_ids_by_clusters[l]-1) for l in clusters_ids if l != q])) * w[q] for q in clusters_ids] )
    gcd_b = sum( [(N-nb_ids_by_clusters[q])*nb_ids_by_clusters[q]/float(sum([(N-nb_ids_by_clusters[l])*nb_ids_by_clusters[l] for l in clusters_ids if l != q])) * b[q] for q in clusters_ids] )
    return gcd_w, gcd_b


def CH_estimator(k,w,b,N):
    """
    Index of Calinski and Harabasz (1974).
    $$ \text{CH}(k) = \dfrac{B(k) / (k-1)}{W(k) / (n-k)} $$
    where $B(k)$ and $W(k)$ are the between- and within-cluster sums of squares, with $k$ clusters.
    The idea is to maximize $\text{CH}(k)$ over the number of clusters $k$. $\text{CH}(1)$ is not defined.

    :Parameters:
     - k: number of clusters;
     - w: global WITHIN cluster distances;
     - b: global BETWEEN cluster distances;
     - N: population size.
    """
    return (b/(k-1))/(w/(N-k))

def Hartigan_estimator(k,w_k,N):
    """
    Index of Hartigan (1975).
    Hartigan (1975) proposed the statistic:
    $$ \text{H}(k) = \left\{ \dfrac{W(k)}{W(k+1)} - 1 \right\} / (n-k-1)$$
    The idea is to start with $k=1$ and to add a cluster as long as $\text{H}(k)$ is sufficiently large.\\
    One can use an approximate $F$-distribution cut-off; instead Hartigan suggested that a cluster be added if $H(k) > 10$. Hence the estimated number of clusters is the smallest $k \geqslant 1$ such that $\text{H}(k) \leqslant 10$. This estimate is defined for $k=1$ and can potentially discriminate between one \textit{versus} more than one cluster.

    :Parameters:
     - k: number of clusters;
     - w_k: DICTIONARY of global WITHIN cluster distances (must contain k and k+1);
     - N: population size.
    """
    return (w_k[k]/w_k[k+1]-1)/(N-k-1)


def clustering_estimators(distance_matrix, clustering_method, clustering_range=[1,20]):
    """
    Compute various estimators based on clustering results.
    
    :Parameters:
     - distance_matrix (np.array): distance matrix to be used for clustering;
     - clustering_method (str): clustering methods to be applyed, must be "Ward" or "Spectral"
     - clustering_range (list): range of clusters to consider.
    """
    from sklearn import metrics
    from sklearn.cluster import spectral_clustering, Ward
    clustering, w, N = {}, {}, {}
    CH, sil = {}, {}

    for k in xrange(clustering_range[0], clustering_range[1]+1):
        if clustering_method == "Ward":
            ward = Ward(n_clusters=k).fit(distance_matrix)
            clustering[k] = ward.labels_
        if clustering_method == "Spectral":
            beta = 1
            similarity = np.exp(-beta * distance_matrix / distance_matrix.std())
            clustering[k] = spectral_clustering( similarity, n_clusters=k )

        N[k] = len(clustering[k])
        if k!=1:
            w[k], b = global_cluster_distance(distance_matrix, clustering[k])
            CH[k] = CH_estimator(k,w[k],b,N[k])
            sil[k] = metrics.silhouette_score(distance_matrix, clustering[k], metric='euclidean')
        else:
            w[k] = within_cluster_distance(distance_matrix, clustering[k])

    Hartigan = dict( [(k, Hartigan_estimator(k,w,N[k]) ) for k in xrange(clustering_range[0], clustering_range[1])] )

    return clustering, CH, Hartigan, sil


def vertex2clusters_distance(distance_matrix, clustering):
    """
    Compute the mean distance between a vertex and those from each group.
    $$ D(i,q) = \dfrac{ \sum_{i \neq j} D(i,j) }{ N_q } \: , \quad \forall i \in [1,N] \:, \: q \in [1,Q],$$
    where $D(i,j)$ is the distance matrix and $q$ a cluster.
    
    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    # -- Compute clusters index once and for all:
    index_q = {}
    for n,q in enumerate(clusters_ids):
        index_q[q] = np.where(clustering == q)[0]

    vertex_cluster_distance = {}
    for i in xrange(N):
        tmp = np.zeros( shape=[nb_clusters], dtype=float )
        for n,q in enumerate(clusters_ids):
            tmp[n] = sum([distance_matrix[i,j] for j in index_q[q] if i!=j])/(nb_ids_by_clusters[n]-1)

        vertex_cluster_distance[i] = tmp

    return vertex_cluster_distance


def vertex_distance2cluster_center(distance_matrix, clustering):
    """
    Compute the distance between a vertex and the center of its group.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)

    D_iq = vertex2clusters_distance(distance_matrix, clustering)
    vertex_distance2center = {}
    for i in xrange(N):
        vertex_distance2center[i] = D_iq[i][clustering[i]]

    return vertex_distance2center


def plot_vertex_distance2cluster_center(distance_matrix, clustering):
    """
    Plot the distance between a vertex and the center of its group.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    vtx2center = vertex_distance2cluster_center(distance_matrix, clustering)

    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    # -- Compute clusters index once and for all:
    index_q = {}
    for n,q in enumerate(clusters_ids):
        index_q[q] = np.where(clustering == q)[0]
        vector = [vtx2center[i] for i in index_q[q]]
        vector.sort()
        plt.plot( vector, label = "Cluster "+str(clusters_ids[n]) )
        plt.axis([0,max(nb_ids_by_clusters), min(vtx2center.values()), max(vtx2center.values())])

    plt.legend(ncol=3)


def time_point_by_clusters(graph, distance_matrix, clustering):
    """
    Return the representativity of each time points (index+1) by clusters.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    ids_by_clusters = dict( (q, np.where(clustering == q)[0]) for q in clusters_ids )
    nb_ids_by_clusters = dict( (q, len(np.where(clustering == q)[0])) for q in clusters_ids )
    index_time_points = list(set(graph.vertex_property('index').values()))

    percent = {}
    for q in clusters_ids:
        for t in index_time_points:
            nb = len([k for k in ids_by_clusters[q] if k in graph.vertex_ids_at_time(t)])
            percent[(q,t)] = [nb/float(nb_ids_by_clusters[q]), nb]

    return dict( ((q,t+1), percent[(q,t)]) for q in clusters_ids for t in index_time_points if percent[(q,t)][0] != 0)


def forward_projection_match(graph, distance_matrix, clustering):
    """
    Compute the temporal evolution of ids of each clusters.
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    ids_by_clusters = dict( (q, np.where(clustering == q)[0]) for q in clusters_ids )
    nb_ids_by_clusters = dict( (q, len(np.where(clustering == q)[0])) for q in clusters_ids )
    index_time_points = list(set(graph.vertex_property('index').values()))

    
    forward_projection_cluster = {}
    for t in index_time_points[:-1]:
        for vid in graph.vertex_ids_at_time(t):
            if graph.has_children(vid):
                children = graph.children(vid)
                for vid_children in children:
                    forward_projection_cluster[(t,clustering[vid])] = 1

    return None

def isolation(distance_matrix, clustering, index = None):
    """
    Isolation, a vertex is isolated if the max distance to a member of its group if superior to the min distance to a member of another group.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)

    if index is None:
        index = xrange(N)

    index_q = {}
    for q in clusters_ids:
        index_q[q] = np.where(clustering == q)[0]
        index_not_q = np.where(clustering != q)[0]

    isolated = {}
    for i in index:
        if max([distance_matrix[i,j] for j in index_q]) >  min([distance_matrix[i,j] for j in index_not_q if distance_matrix[i,j]!=0]):
            isolated[i] = True
        else:
            isolated[i] = False

    if len(index) == 1:
        return isolated.values()
    else:
        return isolated



# An implementation of the gap statistic algorithm from Tibshirani, Walther, and Hastie's "Estimating the number of clusters in a data set via the gap statistic".
#~ library(plyr)
#~ library(ggplot2)

#~ # Given a matrix `data`, where rows are observations and columns are individual dimensions, compute and plot the gap statistic (according to a uniform reference distribution).
#~ def gap_statistic(data, min_num_clusters = 1, max_num_clusters = 10, num_reference_bootstraps = 10):
    #~ num_clusters = xrange(min_num_clusters,max_num_clusters)
    #~ actual_dispersions = maply(num_clusters, function(n) dispersion(data, n))
    #~ ref_dispersions = maply(num_clusters, function(n) reference_dispersion(data, n, num_reference_bootstraps))
    #~ mean_ref_dispersions = ref_dispersions[ , 1]
    #~ stddev_ref_dispersions = ref_dispersions[ , 2]
    #~ gaps = mean_ref_dispersions - actual_dispersions
#~ 
    #~ print(plot_gap_statistic(gaps, stddev_ref_dispersions, num_clusters))
#~ 
    #~ print("The estimated number of clusters is ", num_clusters[which.max(gaps)], ".", sep = ""))
#~ 
    #~ list(gaps = gaps, gap_stddevs = stddev_ref_dispersions)
#~ 
#~ 
#~ # Plot the gaps along with error bars.
#~ def plot_gap_statistic(gaps, stddevs, num_clusters) {
    #~ plot(num_clusters, gaps, xlab = "# clusters", ylab = "gap", geom = "line", main = "Estimating the number of clusters via the gap statistic") + geom_errorbar(aes(num_clusters, ymin = gaps - stddevs, ymax = gaps + stddevs), size = 0.3, width = 0.2, colour = "darkblue")
    #~ plt.plot(num_clusters, gaps, xlab = "# clusters", ylab = "gap")
    #~ geom_errorbar(aes(num_clusters, ymin = gaps - stddevs, ymax = gaps + stddevs), size = 0.3, width = 0.2, colour = "darkblue")
    #~ plt.title("Estimating the number of clusters via the gap statistic")
#~ 
#~ # Calculate log(sum_i(within-cluster_i sum of squares around cluster_i mean)).
#~ def dispersion(data, num_clusters):
    #~ # R's k-means algorithm doesn't work when there is only one cluster.
    #~ if (num_clusters == 1):
        #~ cluster_mean = np.mean(data, 0) #column wise mean
        #~ distances_from_mean = aaply((data - cluster_mean)^2, 1, sum)
        #~ log(sum(distances_from_mean))
    #~ else:
        #~ # Run the k-means algorithm `nstart` times. Each run uses at most `iter.max` iterations.
        #~ k = kmeans(data, centers = num_clusters, nstart = 10, iter.max = 50)
        #~ # Take the sum, over each cluster, of the within-cluster sum of squares around the cluster mean. Then take the log. This is `W_k` in TWH's notation.
        #~ log(sum(k$withinss))
#~ 
#~ 
#~ 
#~ # For an appropriate reference distribution (in this case, uniform points in the same range as `data`), simulate the mean and standard deviation of the dispersion.
#~ def reference_dispersion(data, num_clusters, num_reference_bootstraps):
    #~ dispersions = maply(1:num_reference_bootstraps, function(i) dispersion(generate_uniform_points(data), num_clusters))
    #~ mean_dispersion = mean(dispersions)
    #~ stddev_dispersion = sd(dispersions) / sqrt(1 + 1 / num_reference_bootstraps) # the extra factor accounts for simulation error
    #~ c(mean_dispersion, stddev_dispersion)
#~ 
#~ 
#~ # Generate uniform points within the range of `data`.
#~ def generate_uniform_points(data):
    #~ # Find the min/max values in each dimension, so that we can generate uniform numbers in these ranges.
    #~ mins = aaply(data, 2, min)
    #~ maxs = apply(data, 2, max)
#~ 
    #~ num_datapoints = nrow(data)
    #~ # For each dimension, generate `num_datapoints` points uniformly in the min/max range.
    #~ uniform_pts = maply(1:length(mins), function(dim) runif(num_datapoints, min = mins[dim], max = maxs[dim]))
    #~ uniform_pts = t(uniform_pts)



def MDS(similarity, clustering, dimension=3):
    """
    Compute and display a Multi Dimensional Scaling of the dataset `similarity`.
    """
    if dimension!=2 and dimension!=3:
        warnings.warn("We can only represent in 2D or 3D!")
        return None
    from sklearn import manifold
    xy = manifold.MDS(n_components=dimension).fit_transform(similarity)
    fig = plt.figure()
    if dimension ==2:
        plt.scatter(xy[:,0],xy[:,1], c=clustering, cmap=cm.jet)
    else:
        ax = Axes3D(fig)
        ax.scatter(xy[:,0],xy[:,1],xy[:,2], c=clustering, marker='s', cmap=cm.jet)
        ax_min = np.min([xy[:,0],xy[:,1],xy[:,2]]); ax_max=np.max([xy[:,0],xy[:,1],xy[:,2]])
        ax.set_xlim3d(ax_min, ax_max)
        ax.set_ylim3d(ax_min, ax_max)
        ax.set_zlim3d(ax_min, ax_max)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

    plt.title("Multi Dimensional Scaling")
    plt.show()


def plot_cluster_distances(cluster_distances):
    """
    Display a heat-map of cluster distances with matplotlib.
    """
    plt.imshow(cluster_distances, cmap=cm.jet, interpolation='nearest')

    numrows, numcols = cluster_distances.shape
    def format_coord(x, y):
        col = int(x+0.5)
        row = int(y+0.5)
        if col>=0 and col<numcols and row>=0 and row<numrows:
            z = cd[row,col]
            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
        else:
            return 'x=%1.4f, y=%1.4f'%(x, y)

    plt.format_coord = format_coord
    plt.title("Cluster distances heat-map")
    plt.colorbar()
    plt.show()


