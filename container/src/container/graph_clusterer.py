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

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import warnings
import numpy as np
from numpy import ndarray
import copy
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from openalea.container.temporal_graph_analysis import exist_relative_at_rank
from sklearn.cluster import SpectralClustering, Ward, DBSCAN
from sklearn import metrics
from openalea.container.temporal_graph_analysis import translate_keys_Image2Graph

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
                if data[i] is None or data[j] is None or i in no_dist_index or j in no_dist_index:
                    dist_mat[i,j] = dist_mat[j,i] = None
                else:
                    dist_mat[i,j] = dist_mat[j,i] = abs(data[i]-data[j])

    if variable_types == "Ordinal":
        rank = data.argsort() # In case of ordinal variables, observed values are replaced by ranked values.
        for i in xrange(N):
            for j in xrange(i+1,N): # we skip when i=j because in that case the distance is 0.
                if data[i] is None or data[j] is None or i in no_dist_index or j in no_dist_index:
                    dist_mat[i,j] = dist_mat[j,i] = None
                else:
                    dist_mat[i,j] = dist_mat[j,i] = abs(rank[i]-rank[j])

    return dist_mat


def standardisation(data, norm, variable_types = None, verbose = False):
    """
    :Parameters:
     - `mat` (np.array) - distance matrix
     - `norm` (str) - "L1" or "L2", select which standarisation metric to apply to the data;
     - `variable_types` (str) - "Numeric" or "Ordinal" or "Interval"

    :Returns:
     - `standard_mat` (np.array) - standardized distance matrix
    """

    if (norm.upper() != 'L1') and (norm.upper() != 'L2'):
        raise ValueError("Undefined standardisation metric")

    # -- Identifying case where numpy.array are vectors:
    if isinstance(data,ndarray) and (((data.shape[0] == 1) and (data.shape[1] > 1)) or ((data.shape[1] == 1) and (data.shape[0] > 1))):
        data.tolist()

    # -- Creating the distance matrix if not provided in `data`:
    if isinstance(data,list):
        if isinstance(data[0],list) and len(data)==len(data[0]):
            data = np.array(data)
        elif not isinstance(data[0],list):
            if verbose: print "You provided a vector of variable, we compute the distance matrix first !"
            distance_matrix = distance_matrix_from_vector(data, variable_types)
        else:
            raise ValueError("Can not convert the provided data.")

    if isinstance(data,ndarray) and (data.shape[0]==data.shape[1]) and ((data.shape[0]!=1)and(data.shape[1]!=1)):
        if verbose: print "You provided a distance matrix !"
        distance_matrix = data

    # -- Now we can start the standardisation:
    nan_index = np.isnan(distance_matrix)
    if True in nan_index:
        nb_missing_values = len(np.where(nan_index is True)[0])
        distance_matrix = np.nan_to_num(distance_matrix)
        #~ warnings.warn("It seems there are {0} missing values to take into account!".format(np.sqrt(nb_missing_values)))
    else:
        nb_missing_values = 0.

    N = distance_matrix.shape[0]
    if norm.upper() == "L1":
        absd = np.nansum(np.nansum(abs(distance_matrix))) / (N*(N-1)-nb_missing_values)
        return distance_matrix / absd

    if norm.upper() == "L2":
        sd = np.nansum(np.nansum(distance_matrix**2)) / (N*(N-1)-nb_missing_values)
        return distance_matrix / sd


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


def create_weight_matrix(N,weight,standard_distance_matrix):
    tmp_w_mat = np.zeros( shape = [N,N], dtype=float )
    tmp_w_mat.fill(weight)
    tmp_w_mat[np.where(np.isnan(standard_distance_matrix))]==np.nan
    return tmp_w_mat


def _within_cluster_distances(distance_matrix, clustering):
    """
    Function computing within cluster distance.
    $$ D(q) = \dfrac{ \sum_{i,j \in q; i \neq j} D(i,j) }{(N_{q}-1)N_{q}} ,$$
    where $D(i,j)$ is the distance matrix, $self._N$ is the total number of elements and $N_{q}$ is the number of elements found in clusters $q$.

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
        return D_within.values()[0]
    else:
        return D_within


def _between_cluster_distances(distance_matrix, clustering):
    """
    Function computing within cluster distance.
    $$ D(q) = \dfrac{ \sum_{i \in q} \sum_{j \not\in q} D(i,j) }{ (self._N - N_q) N_q }, $$
    where $D(i,j)$ is the distance matrix, $self._N$ is the total number of elements and $N_{q}$ is the number of elements found in clusters $q$.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    N = len(clustering)
    clusters_ids = list(set(clustering))
    nb_clusters = len(clusters_ids)
    nb_ids_by_clusters = [len(np.where(clustering == q)[0]) for q in clusters_ids]

    if 1 in nb_ids_by_clusters:
        raise ValueError("A cluster contain only one element!")

    D_between = {}
    for n,q in enumerate(clusters_ids):
        index_q = np.where(clustering == q)[0]
        index_not_q = list(set(xrange(len(clustering)))-set(index_q))
        D_between[q] = sum( [distance_matrix[i,j] for i in index_q for j in index_not_q] ) / ( (N-nb_ids_by_clusters[n]) * nb_ids_by_clusters[n])

    if nb_clusters == 1:
        return D_between.values()[0]
    else:
        return D_between


def _global_cluster_distances(distance_matrix, clustering):
    """
    Function computing global cluster distances, i.e. return the sum of within_cluster_distance and between_cluster_distance.

    :Parameters:
     - `distance_matrix` (np.array) - distance matrix used to create the clustering.
     - `clustering` (list) - list giving the resulting clutering.

    :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
    """
    w = _within_cluster_distances(distance_matrix, clustering)
    b = _between_cluster_distances(distance_matrix, clustering)
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



class Clusterer:
    """
    Class to cluster temporal_property_graph objects.
    """
    def __init__(self, graph, standardisation_method, rank=1):
        # -- Initialisation:
        self.graph = graph
        self.labels = list(graph.vertices())
        self.rank = rank
        self.standardisation_method = standardisation_method

        # -- Variables saving informations:
        self._distance_matrix_dict = {}
        self._distance_matrix_info = {}

        # -- Variables for caching information:
        self._global_distance_matrix = None
        self._global_distance_ids = None
        self._global_distance_weigths = None
        self._global_distance_variables = None
        self._method = None
        self._nb_clusters = None
        self._clustering = None

    def add_vertex_variable(self, var_name, var_type, var_id = None):
        """
        Add a distance matrix related to vertices properties form the graph.

        :Parameters:
         - `var_name` (str|dict|list) - string or list of strings related to one or several vertex_property name in the graph. If one is a dict type, we will construct the distance matrix based on ids matching with those from the graph
         - `var_type` (str|list) - string or list of strings declaring the type of properties used
         - `var_id` (str|list) - (Optional) name to give to the variable
        """
        if isinstance(var_name,str) or isinstance(var_name,dict):
            var_name = [var_name]
        if isinstance(var_type,str) or isinstance(var_type,dict):
            var_type = [var_type]
        if var_id is None or isinstance(var_id,str):
            var_id = [var_id]
        assert len(var_name)==len(var_type)
        assert len(var_name)==len(var_id)

        for n, var in enumerate(var_name):
            if (var_id[n] is None or var_id[n] == "") and isinstance(var_name[n],str):
                var_id[n] = var_name[n]
            elif not isinstance(var_id[n],str):
                raise ValueError("You have to give a name to your variable #{} if you want to use it!".format(n))
            # - We make sure self._distance_matrix_dict can receive the distance mattrix with the name var_id[n]:
            if self._distance_matrix_dict.has_key(var_id[n]):
                raise KeyError("You already have a property named {}".format(var_id[n]))

        print("Computing the distance matrix related to vertex variables...")
        for n, var in enumerate(var_name):
            if isinstance(var,str):
                variable_vector = [self.graph.vertex_property(var)[vid] if self.graph.vertex_property(var).has_key(vid) else None for vid in self.labels]# we need to do that if we want to have all matrix ordered the same way
            if isinstance(var,dict):
                variable_vector = [var[vid] if var.has_key(vid) else None for vid in self.labels]# we need to do that if we want to have all matrix ordered the same way
            # - Adding it tho the list
            self._distance_matrix_dict[var_id[n]] = distance_matrix_from_vector(variable_vector, var_type[n])
            self._distance_matrix_info[var_id[n]] = ('s', var_type[n].lower())

        return var_id

    def add_temporal_variable(self, var_name, var_type, var_id = None):
        """
        Add a distance matrix related to temporal differentiation of vertex properties form the graph.

        :Parameters:
         - `var_name` (str|dict|list) - string or list of strings related to one or several vertex_property name in the graph. If one is a dict type, we will construct the distance matrix based on ids matching with those from the graph
         - `var_type` (str|list) - string or list of strings declaring the type of properties used
         - `var_id` (str|list) - (Optional) name to give to the variable

        :WARNING:
        If a string is given as variable name, we will compute the `relative_temporal_change` of the given string, considered as a vertex_property from the graph.
        """
        if isinstance(var_name,str) or isinstance(var_name,dict):
            var_name = [var_name]
        if isinstance(var_type,str) or isinstance(var_type,dict):
            var_type = [var_type]
        if var_id is None or isinstance(var_id,str):
            var_id = [var_id]
        assert len(var_name)==len(var_type)
        assert len(var_name)==len(var_id)

        for n, var in enumerate(var_name):
            if (var_id[n] is None or var_id[n] == "") and isinstance(var_name[n],str):
                var_id[n] = var_name[n]
            elif not isinstance(var_id[n],str):
                raise ValueError("You have to give a name to your variable #{} if you want to use it!".format(n))
            # - We make sure self._distance_matrix_dict can receive the distance mattrix with the name var_id[n]:
            if self._distance_matrix_dict.has_key(var_id[n]):
                raise KeyError("You already have a property named '{}'".format(var_id[n]))

        print("Computing the distance matrix related to temporal variables...")
        # If we want to work with temporally differentiated variables, we will have to filter vertex without parent (since we assign spatio-temporal variable @ t_n+1):
        for n, temporal_name in enumerate(var_name):
            if isinstance(temporal_name,dict):
                dict_temporal = temporal_name
            elif isinstance(temporal_name,str):
                from openalea.container.temporal_graph_analysis import relative_temporal_change
                dict_temporal = relative_temporal_change(self.graph, temporal_name, self.labels, self.rank, labels_at_t_n = False)
            else:
                raise ValueError("Unrecognized type of data.")
            # - Now we create the 'vector' of data sorted by vertices to create the distance matrix:
            temporal_distance_list = [dict_temporal[vid] if dict_temporal.has_key(vid) else None for vid in self.labels]# we need to do that if we want to have all matrix ordered the same way
            self._distance_matrix_dict[var_id[n]] = distance_matrix_from_vector(temporal_distance_list, var_type[n])
            self._distance_matrix_info[var_id[n]] = ('t', var_type[n].lower())

        return var_id

    def add_topological_distance_matrix(self, force=False):
        """
        Create the topological distance matrix based on the graph provided and limited to vids if given.
        """
        if self._distance_matrix_dict.has_key("topology") and not force:
            raise KeyError("You already computed the distance matrix 'topology'. Use 'force=True' to do it again.")

        print("Computing the standardized topological distance matrix...")
        import time
        t = time.time()
        # - Extraction of the topological distance between all vertex of a time point:
        topo_dist = dict( [(vid, self.graph.topological_distance(vid, 's',return_inf=False)) for vid in self.labels] )
        # - Transformation into a distance matrix
        self._distance_matrix_dict["topological"] = np.array([[(topo_dist[i][j] if i!=j else 0) for i in self.labels] for j in self.labels])
        self._distance_matrix_info["topological"] = ('s', "rank")
        print "Distance matrix 'topological' created in {0}s".format(time.time() - t)


    def add_euclidean_distance_matrix(self, force=False):
        """
        Create the euclidean distance matrix based on the graph provided and limited to vids if given.
        """
        if self._distance_matrix_dict.has_key("euclidean") and not force:
            raise KeyError("You already computed the distance matrix 'euclidean'. Use 'force=True' to do it again.")

        print("Computing the standardized euclidean distance matrix...")
        import time
        t = time.time()
        # - Extraction of the topological distance between all vertex of a time point:
        bary = self.graph.vertex_property('barycenter')
        self._distance_matrix_dict["euclidean"] = np.array([[np.linalg.norm(bary[i]-bary[j]) for i in self.labels] for j in self.labels])
        self._distance_matrix_info["euclidean"] = ('s', "numeric")
        print "Distance matrix 'euclidean' created in {0}s".format(time.time() - t)


    def remove_distance_matrix(self, var_id):
        """
        :TODO:
        remove a distance matrix form the dictionary `self._distance_matrix_dict` and it's attached information in `self._distance_matrix_info`
        """
        pass


    #~ def assemble_matrix_OLD(self, variable_names, variable_weights, vids = None):
        #~ """
        #~ Funtion creating the global weighted distance matrix.
        #~ Provided `variable_names` should exist in `self.vertex_matrix_dict`
#~ 
        #~ :Parameters:
         #~ - `variable_names` (list) - list of variables names in `self.vertex_matrix_dict` to combine
         #~ - `variable_weights` (list) - list of variables used to create the global weighted distance matrix
         #~ - `vids` (list) - list of ids to have in the distance matrix
        #~ """
        #~ if isinstance(variable_names,str):
            #~ variable_names = [variable_names]
        #~ if isinstance(variable_weights,int) or isinstance(variable_weights,float):
            #~ variable_weights = [float(variable_weights)]
        #~ assert len(variable_names) == len(variable_weights)
        #~ assert math.fsum(variable_weights)==1.
        #~ #assert math.fsum(variable_weights)==1. or math.fsum(variable_weights)-1.<1e-5
#~ 
        #~ # -- Checking all requested information (i.e. variables names) is present in the dictionary `self._distance_matrix_dict`:
        #~ for k in variable_names:
            #~ if not self._distance_matrix_dict.has_key(k):
                #~ if k.lower() == 'topological':
                    #~ self.add_topological_distance_matrix()
                #~ elif k.lower() == 'euclidean':
                    #~ self.add_euclidean_distance_matrix()
                #~ else:
                    #~ raise KeyError("'{}' is not in the dictionary `self._distance_matrix_dict`".format(k))
#~ 
        #~ # -- Detecting the kind of data we are facing !
        #~ spatial_relation_data, temporal_data, spatial_data = False, False, False
        #~ for k,v in self._distance_matrix_info.iteritems():
            #~ if k == 'topological' or k == 'euclidean':
                #~ spatial_relation_data = True
            #~ if v[0] == 't':
                #~ temporal_data = True
            #~ if v[0] == 's' and k != 'topological' and k != 'euclidean':
                #~ spatial_data = True
#~ 
        #~ # -- Creating the list of vertices:
        #~ # - Checking for unwanted ids:
        #~ if vids is not None:
            #~ id_not_in_labels = list(set(vids)-set(self.labels))
            #~ if len(id_not_in_labels) != 0:
                #~ warnings.warn("Some of the ids you provided has not been found in the graph : {}".format(id_not_in_labels))
                #~ print ("Removing them...")
                #~ vids = list(set(vids)-set(id_not_in_labels))
        #~ # - Filtering ids according to necessity:
        #~ if temporal_data:
            #~ # - We keep vertex ids only if they are temporally linked in the graph at `rank` or -`rank`
            #~ if vids is None:
                #~ vtx_list = [vid for vid in self.labels if exist_relative_at_rank(self.graph, vid, self.rank) or exist_relative_at_rank(self.graph, vid, -self.rank)]
            #~ else:
                #~ vtx_list = [vid for vid in vids if exist_relative_at_rank(self.graph, vid, self.rank) or exist_relative_at_rank(self.graph, vid, -self.rank)]
        #~ else:
            #~ # - No need to check for temporal link !
            #~ if vids is None:
                #~ vtx_list = self.labels
            #~ else:
                #~ vtx_list = vids
#~ 
        #~ # -- Shortcut when asking for the same result:
        #~ if variable_weights == self._global_distance_weigths and variable_names == self._global_distance_variables and vtx_list == self._global_distance_ids:
            #~ return self._global_distance_ids, self._global_distance_matrix
#~ 
        #~ # -- Standardization step:
        #~ # - Need to check if there is any changes (length or order) in the ids list compared to the initial list used to create the pairwise distance matrix:
        #~ ids_index = [self.labels.index(v) for v in vtx_list]
#~ 
        #~ spatial_standard_distance_matrix, temporal_standard_distance_matrix = {}, {}
        #~ temporal_weights, spatial_weights = [], []
        #~ nb_temp_var, nb_spa_var = 0, 0
        #~ mat_topo_dist_standard = []
        #~ for n,var_name in enumerate(variable_names):
            #~ if var_name == 'topological' or var_name == 'euclidean':
                #~ mat_topo_dist_standard = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                #~ topo_weight = variable_weights[n]
            #~ elif self._distance_matrix_info[var_name][0] == 't':
                #~ temporal_standard_distance_matrix[nb_temp_var] = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                #~ temporal_weights.append(variable_weights[n])
                #~ nb_temp_var += 1
            #~ else:
                #~ spatial_standard_distance_matrix[nb_spa_var] = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                #~ spatial_weights.append(variable_weights[n])
                #~ nb_spa_var += 1
#~ 
        #~ # -- Checking for simple cases: no re-weighting to do !
        #~ # - Only 'topological' or 'euclidean' distance asked:
        #~ if spatial_relation_data and (nb_spa_var+nb_temp_var)==0:
            #~ print "No topological/euclidean distance between each time point !!"
            #~ return vtx_list, mat_topo_dist_standard
        #~ # - Only ONE spatial pairwise distance asked:
        #~ if not spatial_relation_data and nb_temp_var == 0 and nb_spa_var == 1:
            #~ return vtx_list, spatial_standard_distance_matrix[0]
        #~ # - Only ONE temporal pairwise distance asked:
        #~ if not spatial_relation_data and nb_spa_var == 0 and nb_temp_var == 1:
            #~ print "Paiwise distance matrix based on temporally differentiated variables affected @t_n+1."
            #~ print "There will be no distance for the ids of the first time-point!"
            #~ return vtx_list, temporal_standard_distance_matrix[0]
#~ 
        #~ # - Replacing nan by zeros for computation.
        #~ if spatial_relation_data:
            #~ mat_topo = np.nan_to_num(mat_topo_dist_standard)
        #~ else:
            #~ mat_topo = []
        #~ if spatial_data:
            #~ var_mat = [np.nan_to_num(spatial_standard_distance_matrix[n]) for n in xrange(nb_spa_var)]
        #~ else:
            #~ var_mat, spatial_standard_distance_matrix = [], []
        #~ if temporal_data:
            #~ temp_mat = [np.nan_to_num(temporal_standard_distance_matrix[n]) for n in xrange(nb_temp_var)]
        #~ else:
            #~ temp_mat, temporal_standard_distance_matrix = [], []
#~ 
        #~ print("Creating the global pairwise weighted standard distance matrix...")
        #~ # Finally making the global weighted pairwise standard distance matrix:
        #~ N = len(vtx_list)
        #~ global_matrix = np.zeros( shape = [N,N], dtype=float )
        #~ w_mat = np.zeros( shape = [N,N], dtype=float )
        #~ for i in xrange(global_matrix.shape[0]):
            #~ for j in xrange(global_matrix.shape[1]):
                #~ if i>j: #D[i,j]=D[j,i] and if i==j, D[i,j]=D[j,i]=0
                    #~ # - Computing weights according to missing values.
                    #~ w_topo, w_var, w_temp = renorm(i,j,mat_topo_dist_standard, spatial_standard_distance_matrix, temporal_standard_distance_matrix, copy.copy(topo_weight), copy.copy(spatial_weights), copy.copy(temporal_weights))
                    #~ # - Pairwise weighted standard distance matrix
                    #~ global_matrix[i,j] = global_matrix[j,i] = w_topo * mat_topo[i,j] + sum([w_var[n]*var_mat[n][i,j] for n in xrange(nb_spa_var)]) + sum([w_temp[n]*temp_mat[n][i,j] for n in xrange(nb_temp_var)])
#~ 
        #~ # -- We update caching variables only if there is more than ONE pairwise distance matrix :
        #~ self._global_distance_matrix = global_matrix
        #~ self._global_distance_ids = vtx_list
        #~ self._global_distance_weigths = variable_weights
        #~ self._global_distance_variables = variable_names
#~ 
        #~ return vtx_list, global_matrix


    def assemble_matrix(self, variable_names, variable_weights, vids = None, return_data = False):
        """
        Funtion creating the global weighted distance matrix.
        Provided `variable_names` should exist in `self.vertex_matrix_dict`

        :Parameters:
         - `variable_names` (list) - list of variables names in `self.vertex_matrix_dict` to combine
         - `variable_weights` (list) - list of variables used to create the global weighted distance matrix
         - `vids` (list) - list of ids to have in the distance matrix
        """
        if isinstance(variable_names,str):
            variable_names = [variable_names]
        if isinstance(variable_weights,int) or isinstance(variable_weights,float):
            variable_weights = [float(variable_weights)]
        assert len(variable_names) == len(variable_weights)
        assert math.fsum(variable_weights)==1.
        #assert math.fsum(variable_weights)==1. or math.fsum(variable_weights)-1.<1e-5

        # -- Checking all requested information (i.e. variables names) is present in the dictionary `self._distance_matrix_dict`:
        for k in variable_names:
            if not self._distance_matrix_dict.has_key(k):
                if k.lower() == 'topological':
                    self.add_topological_distance_matrix()
                elif k.lower() == 'euclidean':
                    self.add_euclidean_distance_matrix()
                else:
                    raise KeyError("'{}' is not in the dictionary `self._distance_matrix_dict`".format(k))

        # -- Detecting the kind of data we are facing !
        spatial_relation_data, temporal_data, spatial_data = False, False, False
        for k,v in self._distance_matrix_info.iteritems():
            if k == 'topological' or k == 'euclidean':
                spatial_relation_data = True
            if v[0] == 't':
                temporal_data = True
            if v[0] == 's' and k != 'topological' and k != 'euclidean':
                spatial_data = True

        # -- Creating the list of vertices:
        # - Checking for unwanted ids:
        if vids is not None:
            id_not_in_labels = list(set(vids)-set(self.labels))
            if len(id_not_in_labels) != 0:
                warnings.warn("Some of the ids you provided has not been found in the graph : {}".format(id_not_in_labels))
                print ("Removing them...")
                vids = list(set(vids)-set(id_not_in_labels))
        # - Filtering ids according to necessity:
        if temporal_data:
            # - We keep vertex ids only if they are temporally linked in the graph at `rank` or -`rank`
            if vids is None:
                vtx_list = [vid for vid in self.labels if exist_relative_at_rank(self.graph, vid, self.rank) or exist_relative_at_rank(self.graph, vid, -self.rank)]
            else:
                vtx_list = [vid for vid in vids if exist_relative_at_rank(self.graph, vid, self.rank) or exist_relative_at_rank(self.graph, vid, -self.rank)]
        else:
            # - No need to check for temporal link !
            if vids is None:
                vtx_list = self.labels
            else:
                vtx_list = vids

        # -- Shortcut when asking for the same result:
        if variable_weights == self._global_distance_weigths and variable_names == self._global_distance_variables and vtx_list == self._global_distance_ids:
            return self._global_distance_ids, self._global_distance_matrix

        # -- Standardization step:
        # - Need to check if there is any changes (length or order) in the ids list compared to the initial list used to create the pairwise distance matrix:
        ids_index = [self.labels.index(v) for v in vtx_list]

        spatial_standard_distance_matrix, temporal_standard_distance_matrix = {}, {}
        temporal_weights, spatial_weights = [], []
        nb_temp_var, nb_spa_var = 0, 0
        mat_topo_dist_standard = []
        for n,var_name in enumerate(variable_names):
            if var_name == 'topological' or var_name == 'euclidean':
                mat_topo_dist_standard = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                topo_weight = variable_weights[n]
            elif self._distance_matrix_info[var_name][0] == 't':
                temporal_standard_distance_matrix[nb_temp_var] = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                temporal_weights.append(variable_weights[n])
                nb_temp_var += 1
            else:
                spatial_standard_distance_matrix[nb_spa_var] = standardisation(self._distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                spatial_weights.append(variable_weights[n])
                nb_spa_var += 1

        # -- Checking for simple cases: no re-weighting to do !
        # - Only 'topological' or 'euclidean' distance asked:
        if spatial_relation_data and (nb_spa_var+nb_temp_var)==0:
            print "No topological/euclidean distance between each time point !!"
            return vtx_list, mat_topo_dist_standard
        # - Only ONE spatial pairwise distance asked:
        if not spatial_relation_data and nb_temp_var == 0 and nb_spa_var == 1:
            return vtx_list, spatial_standard_distance_matrix[0]
        # - Only ONE temporal pairwise distance asked:
        if not spatial_relation_data and nb_spa_var == 0 and nb_temp_var == 1:
            print "Paiwise distance matrix based on temporally differentiated variables affected @t_n+1."
            print "There will be no distance for the ids of the first time-point!"
            return vtx_list, temporal_standard_distance_matrix[0]

        # - Creating weight matrix and replacing nan by zeros for computation in standardized matrix.
        N = len(vtx_list)
        weights, weight_matrix, standardized_matrix = [], [], []
        if spatial_relation_data:
            standardized_matrix.append( np.nan_to_num(mat_topo_dist_standard) )
            weights.append(topo_weight)
            weight_matrix.append(create_weight_matrix(N,topo_weight,mat_topo_dist_standard))
        if spatial_data:
            standardized_matrix.extend( [np.nan_to_num(spatial_standard_distance_matrix[n]) for n in xrange(nb_spa_var)] )
            for n in xrange(nb_spa_var):
                weights.append(spatial_weights[n])
                weight_matrix.append(create_weight_matrix(N,spatial_weights[n],spatial_standard_distance_matrix[n]))
        if temporal_data:
            standardized_matrix.extend( [np.nan_to_num(temporal_standard_distance_matrix[n]) for n in xrange(nb_temp_var)] )
            for n in xrange(nb_temp_var):
                weights.append(temporal_weights[n])
                weight_matrix.append(create_weight_matrix(N,temporal_weights[n],temporal_standard_distance_matrix[n]))

        print("Creating the global pairwise weighted standard distance matrix...")
        # Finally making the global weighted pairwise standard distance matrix:
        for w, w_m in zip(weights,weight_matrix):
            binary = ~np.isnan(w_m)
            weight_matrix = [weight_matrix[r]*(binary+~binary*w) for r in xrange(len(weights))]

        global_matrix = np.zeros( shape = [N,N], dtype=float )
        for wei_mat, standard_mat in zip(weight_matrix,standardized_matrix):
            global_matrix += np.nan_to_num(wei_mat)*standard_mat

        # -- We update caching variables only if there is more than ONE pairwise distance matrix :
        self._global_distance_matrix = global_matrix
        self._global_distance_ids = vtx_list
        self._global_distance_weigths = variable_weights
        self._global_distance_variables = variable_names

        if return_data:
            return vtx_list, global_matrix
        else:
            print "Done."


    def cluster(self, n_clusters, method = "ward", ids = None, global_matrix = None):
        """
        Actually run the clustering method.
        :Parameters:
         - `n_clusters` (int) - number of cluster to create
         - `method` (str) - clustering method to use, "ward", "spectral" and "DBSCAN"
         - `ids` (list) - list of ids
         - `global_matrix` (np.array) - distance matrix to cluster (ordered the same way than `ids`)
        """
        if global_matrix is None:
            if self._global_distance_matrix is not None:
                global_matrix = self._global_distance_matrix
            else:
                raise ValueError("No distance matrix saved, please give one!")
        if ids is None:
            ids = self._global_distance_ids

        if method.lower() == "ward":
            if n_clusters is not None:
                clustering = Ward(n_clusters = n_clusters).fit(global_matrix)
                clustering_labels = clustering.labels_
            else:
                raise ValueError("You have to provide the number of clusters you want for the Ward method.")
        if method.lower() == "spectral":
            if n_clusters is not None:
                clustering = SpectralClustering(n_clusters = n_clusters, precomputed=True).fit(global_matrix)
                clustering_labels = clustering.labels_
            else:
                raise ValueError("You have to provide the number of clusters you want for the spectral method.")

        self._clustering = list(clustering_labels)
        self._method = method.lower()
        self._nb_clusters = n_clusters
        if ids is not None:
            return dict([ (label,clustering_labels[n]) for n,label in enumerate(ids) ])
        else:
            return clustering_labels


    def export_clustering2graph(self, graph, save_all = False, name=""):
        """
        Function saving the current clustering on the graph structure.
        """
        if self._global_distance_matrix is None:
            return warnings.warn('No clustering made yet !')

        if name == "":
            name=self._method+"_"+str(self._nb_clusters)+"_"+str([str(self._global_distance_weigths[n])+"*"+str(self._global_distance_variables[n]) for n in xrange(len(self._global_distance_weigths))])
            print "The clustering '{}' will be added to the `graph` ...".format(name)

        graph.add_vertex_property(name, dict([ (label,self._clustering[n]) for n,label in enumerate(self._global_distance_ids) ]))
        graph.add_graph_property("dist_weigths_"+name, self._global_distance_weigths)
        graph.add_graph_property("dist_variables_"+name, self._global_distance_variables)
        if save_all:
            print "Saving vertex id list and the global distance matrix too ..."
            graph.add_graph_property("ids_"+name, self._global_distance_ids)
            graph.add_graph_property("dist_matrix_"+name, self._global_distance_matrix)

        warnings.warn("This addded clustering informations to the provided `graph` but did not saved it on disk!")


    def silhouette_estimators(self, clustering_method, k_min=4, k_max=15, beta = 1, plot_estimator = True):
        """
        Compute various estimators based on clustering results.
        
        :Parameters:
         - distance_matrix (np.array): distance matrix to be used for clustering;
         - clustering_method (str): clustering methods to be applyed, must be "Ward" or "Spectral"
         - clustering_range (list): range of clusters to consider.
        """
        from sklearn import metrics
        from sklearn.cluster import spectral_clustering, Ward
        clustering_labels={}
        sil = {}
        assert k_min>1

        for k in xrange(k_min, k_max+1):
            if clustering_method.lower() == "ward":
                clustering = Ward(n_clusters=k).fit(self._global_distance_matrix)
                clustering_labels[k] = clustering.labels_
            if clustering_method.lower() == "spectral":
                similarity = np.exp(-beta * self._global_distance_matrix / self._global_distance_matrix.std())
                clustering = SpectralClustering(n_clusters = k, precomputed=True).fit(self._global_distance_matrix)
                clustering_labels[k] = clustering.labels_

            sil[k] = metrics.silhouette_score(self._global_distance_matrix, clustering_labels[k], metric='euclidean')

        if plot_estimator:
            fig = plt.figure(figsize=(4,4),dpi=100)
            plt.plot(xrange(k_min, k_max+1), sil.values(), color='red')
            plt.title("Silhouette estimator")

        return sil

    def clustering_estimators(self, clustering_method, k_min=4, k_max=15, beta = 1, plot_estimator = True):
        """
        Compute various estimators based on clustering results.

        :Parameters:
         - distance_matrix (np.array): distance matrix to be used for clustering;
         - clustering_method (str): clustering methods to be applyed, must be "Ward" or "Spectral"
         - clustering_range (list): range of clusters to consider.
        """
        from sklearn import metrics
        from sklearn.cluster import spectral_clustering, Ward
        clustering_labels, w, N = {}, {}, {}
        CH, sil = {}, {}
        assert k_min>=1

        for k in xrange(k_min, k_max+1):
            if clustering_method.lower() == "ward":
                clustering = Ward(n_clusters=k).fit(self._global_distance_matrix)
                clustering_labels[k] = clustering.labels_
            if clustering_method.lower() == "spectral":
                similarity = np.exp(-beta * self._global_distance_matrix / self._global_distance_matrix.std())
                clustering = SpectralClustering(n_clusters = k, precomputed=True).fit(self._global_distance_matrix)
                clustering_labels[k] = clustering.labels_

            N[k] = len(clustering_labels[k])
            if k!=1:
                w[k], b = _global_cluster_distances(self._global_distance_matrix, clustering_labels[k])
                CH[k] = CH_estimator(k,w[k],b,N[k])
                sil[k] = metrics.silhouette_score(self._global_distance_matrix, clustering_labels[k], metric='euclidean')
            else:
                w[k] = _within_cluster_distances(self._global_distance_matrix, clustering_labels[k])

        Hartigan = dict( [(k, Hartigan_estimator(k,w,N[k])) for k in xrange(k_min, k_max)] )

        if plot_estimator:
            fig = plt.figure(figsize=(12,4),dpi=100)
            fig.add_subplot(131)
            plt.plot(xrange(k_min if k_min>1 else 2, k_max+1),CH.values())
            plt.title("Calinski and Harabasz estimator")
            fig.add_subplot(132)
            plt.plot(xrange(k_min, k_max), Hartigan.values(), color='green')
            plt.title("Hartigan estimator")
            fig.add_subplot(133)
            plt.plot(xrange(k_min if k_min>1 else 2, k_max+1), sil.values(), color='red')
            plt.title("Silhouette estimator")

        return CH, Hartigan, sil


class ClustererChecker:
    """
    Class allowing to analyse a `Clusterer` object.
    """
    def __init__(self, clusterer, construct_clustered_graph = True):
        # - Paranoia :
        assert clusterer.__class__.__name__ == 'Clusterer'
        # - Initialisation
        self.clusterer = clusterer
        self._vtx_list = clusterer._global_distance_ids
        self._distance_matrix = clusterer._global_distance_matrix
        self._clustering = clusterer._clustering
        # - Precompute usefull values :
        self._N = len(self._clustering)
        self._clusters_ids = list(set(self._clustering))
        self._nb_clusters = len(self._clusters_ids)
        self._nb_ids_by_clusters = dict( [ (q,len(np.where(self._clustering == q)[0])) for q in self._clusters_ids] )
        self._ids_by_clusters = dict( (q, [self._vtx_list[k] for k in np.where(self._clustering == q)[0]]) for q in self._clusters_ids )
        # - Reformat inherited (usefull) info :
        self.info_clustering = {'method': clusterer._method,
                                'variables': clusterer._global_distance_variables,
                                'weigths': clusterer._global_distance_weigths}
        self.clustering_name = self.info_clustering['method']+"_"+str(self._nb_clusters)+"_"+str([str(self.info_clustering['weigths'][n])+"*"+str(self.info_clustering['variables'][n]) for n in xrange(len(self.info_clustering['weigths']))])
        # - Construct the clustered graph :
        if construct_clustered_graph:
            print 'Creating the clustered version of the inherited graph...'
            self.clustered_graph = self.clustered_temporal_property_graph()
        else:
            self.clustered_graph = None

    def cluster_distance_matrix(self):
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

        :WARNING: `distance_matrix` and `clustering` should obviously be ordered the same way!
        """
        D = np.zeros( shape = [self._nb_clusters,self._nb_clusters], dtype = float )
        for n,q in enumerate(self._clusters_ids):
            for m,l in enumerate(self._clusters_ids):
                if n==m:
                    index_q = np.where(self._clustering == q)[0]
                    D[n,m] = sum( [self._distance_matrix[i,j] for i in index_q for j in index_q if i!=j] ) / ( (self._nb_ids_by_clusters[n]-1) * self._nb_ids_by_clusters[n])
                if n>m:
                    index_q = np.where(self._clustering == q)[0]
                    index_l = np.where(self._clustering == l)[0]
                    D[n,m] = D[m,n]= sum( [self._distance_matrix[i,j] for i in index_q for j in index_l] ) / (self._nb_ids_by_clusters[n] * self._nb_ids_by_clusters[m])

        return D


    def plot_cluster_distances(self):
        """
        Display a heat-map of cluster distances with matplotlib.
        """
        cluster_distances = self.cluster_distance_matrix()
        fig = plt.figure()
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


    def cluster_diameters(self):
        """
        Function computing within cluster diameter, i.e. the max distance between two vertex from the same cluster.
        $$ \max_{i,j \in q} D(j,i) ,$$
        where $D(i,j)$ is the distance matrix and $q$ a cluster, .

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        diameters = {}
        for q in self._clusters_ids:
            index_q = np.where(self._clustering == q)[0]
            diameters[q] = max([self._distance_matrix[i,j] for i in index_q for j in index_q])

        if self._nb_clusters == 1:
            return diameters.values()
        else:
            return diameters


    def cluster_separation(self):
        """
        Function computing within cluster diameter, i.e. the min distance between two vertex from two diferent clusters.
        $$ \min_{i \in q, j \not\in q} D(j,i) ,$$
        where $D(i,j)$ is the distance matrix and $q$ a cluster.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        separation = {}
        for q in self._clusters_ids:
            index_q = np.where(self._clustering == q)[0]
            index_not_q = np.where(self._clustering != q)[0]
            separation[q] = min([self._distance_matrix[i,j] for i in index_q for j in index_not_q ])

        if self._nb_clusters == 1:
            return separation.values()
        else:
            return separation

    def within_cluster_distances(self):
        """
        Function computing within cluster distance.
        """
        return _within_cluster_distances(self._distance_matrix, self._clustering)


    def between_cluster_distances(self):
        """
        Function computing within cluster distance.
        """
        return _between_cluster_distances(self._distance_matrix, self._clustering)


    def global_cluster_distance(self):
        """
        Function computing global cluster distances, i.e. return the sum of within_cluster_distance and between_cluster_distance.
        """
        return _global_cluster_distance(self._distance_matrix, self._clustering)


    def __score_param(func):
        def wrapped_function(self, dict_labels_expert, groups2compare = []):
            """
            Wrapped function for clustering score computation according to the knowledge of the ground truth class assignments.

            :Parameters:
             - dict_labels_expert (dict) - expert defined regions / clusters in wich keys are labels
             - groups2compare (list) - pair(s) of groups id to compare, with first the expert id then the predicted id ex. [0,6] or [[0,6],[4,3]]
            """
            if groups2compare != []:
                compare_groups = True
                groups2compare = np.array(groups2compare, ndmin=2)
            else:
                compare_groups = False

            clustering_dict = dict(zip(self._vtx_list, self._clustering))
            not_found = []
            labels_true, labels_pred = [], []
            max1 = max(dict_labels_expert.values())+1
            max2 = max(clustering_dict.values())+1
            for k,v in dict_labels_expert.iteritems():
                if clustering_dict.has_key(k):
                    v2 = clustering_dict[k]
                    if compare_groups:
                        labels_true.append(v if (v in groups2compare[:,0]) else max1)
                        labels_pred.append(v2 if (v2 in groups2compare[:,1]) else max2)
                        #~ labels_pred.append(v2)
                    else:
                        labels_true.append(v)
                        labels_pred.append(v2)
                else:
                    not_found.append(k)

            if not_found != []:
                warnings.warn("These labels were not found in the clustering result: {}".format(not_found))

            return func(labels_true, labels_pred)
        return wrapped_function


    @__score_param
    def adjusted_rand_score(labels_true, labels_pred):
        """
        The Adjusted Rand Index (ARI) is a function that measures the similarity of the two assignments, ignoring permutations and with chance normalization.

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples

        :Notes:
         - Random (uniform) label assignments have a ARI score close to 0.0.
         - Bounded range [-1, 1]. Negative values are bad (independent labelings), similar clusterings have a positive ARI, 1.0 is the perfect match score.
         - No assumption is made on the cluster structure: can be used to compare clustering algorithms such as k-means which assumes isotropic blob shapes with results of spectral clustering algorithms which can find cluster with "folded" shapes.
        """
        return metrics.adjusted_rand_score(labels_true, labels_pred)

    @__score_param
    def adjusted_mutual_info_score(labels_true, labels_pred):
        """
        The Mutual Information (NMI and AMI) is a function that measures the agreement of the two assignments, ignoring permutations.
        Adjusted Mutual Information (AMI) was proposed more recently than NMI and is normalized against chance.

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples

        :Note:
         - Random (uniform) label assignments have a AMI score close to 0.0.
        """
        return metrics.adjusted_mutual_info_score(labels_true, labels_pred)

    @__score_param
    def normalized_mutual_info_score(labels_true, labels_pred):
        """
        The Mutual Information (NMI and AMI) is a function that measures the agreement of the two assignments, ignoring permutations.
        Normalized Mutual Information (NMI) is often used in the literature, but it is NOT normalized against chance.
        """
        return metrics.normalized_mutual_info_score(labels_true, labels_pred)

    @__score_param
    def homogeneity_score(labels_true, labels_pred):
        """
        Homogeneity: each cluster contains only members of a single class.
        Bounded below by 0.0 and above by 1.0 (higher is better).

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples

        :Note:
         - homogeneity_score(a, b) == completeness_score(b, a)
        """
        return metrics.homogeneity_score(labels_true, labels_pred)

    @__score_param
    def completeness_score(labels_true, labels_pred):
        """
        Completeness: all members of a given class are assigned to the same cluster.
        Bounded below by 0.0 and above by 1.0 (higher is better).

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples

        :Note:
         - homogeneity_score(a, b) == completeness_score(b, a)
        """
        return metrics.completeness_score(labels_true, labels_pred)

    @__score_param
    def v_measure_score(labels_true, labels_pred):
        """
        Harmonic mean of homogeneity and completeness_score is called V-measure.

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples

        :Note:
         - `v_measure_score` is symmetric, it can be used to evaluate the agreement of two independent assignments on the same dataset.
        """
        return metrics.v_measure_score(labels_true, labels_pred)

    @__score_param
    def homogeneity_completeness_v_measure(labels_true, labels_pred):
        """
        Homogeneity, completensess and V-measure can be computed at once using homogeneity_completeness_v_measure

        :Parameters:
         - `labels_true` (list) - knowledge of the ground truth class assignments
         - `labels_pred` (list) - clustering algorithm assignments of the same samples
        """
        return metrics.homogeneity_completeness_v_measure(labels_true, labels_pred)


    def cluster_by_time_points(self, graph):
        """
        Return the representativity of each time points (index+1) by clusters.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        index_time_points = list(set(graph.vertex_property('index').values()))

        percent = {}
        for q in self._clusters_ids:
            for t in index_time_points:
                nb = len([k for k in self._ids_by_clusters[q] if k in graph.vertex_at_time(t)])
                percent[(q,t)] = [nb/float(self._nb_ids_by_clusters[q]), nb]

        return dict( ((q,t), percent[(q,t)]) for q in self._clusters_ids for t in index_time_points if percent[(q,t)][0] != 0)


    def time_point_by_clusters(self, graph):
        """
        Return the representativity of each time points (index+1) by clusters.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        index_time_points = list(set(graph.vertex_property('index').values()))

        percent = {}
        for t in index_time_points:
            for q in self._clusters_ids:
                nb = len([k for k in self._ids_by_clusters[q] if k in graph.vertex_at_time(t)])
                percent[(t,q)] = [nb/float(self._nb_ids_by_clusters[q]), nb]

        return dict( ((t,q), percent[(t,q)]) for q in self._clusters_ids for t in index_time_points if percent[(t,q)][0] != 0)


    def forward_projection_match(self, graph):
        """
        Compute the temporal evolution of ids of each clusters.
        """
        index_time_points = list(set(graph.vertex_property('index').values()))

        forward_projection_cluster = {}
        for t in index_time_points[:-1]:
            for vid in graph.vertex_at_time(t):
                if graph.has_children(vid):
                    children = graph.children(vid)
                    for vid_children in children:
                        forward_projection_cluster[(t,self._clustering[vid])] = 1

        return None


    def vertex2clusters_distance(self):
        """
        Compute the mean distance between a vertex and those from each group.
        $$ D(i,q) = \dfrac{ \sum_{i \neq j} D(i,j) }{ N_q } \: , \quad \forall i \in [1,self._N] \:, \: q \in [1,Q],$$
        where $D(i,j)$ is the distance matrix and $q$ a cluster.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        index_q = {}
        for n,q in enumerate(self._clusters_ids):
            index_q[q] = np.where(self._clustering == q)[0]

        vertex_cluster_distance = {}
        for i in xrange(self._N):
            tmp = np.zeros( shape=[self._nb_clusters], dtype=float )
            for n,q in enumerate(self._clusters_ids):
                tmp[n] = sum([self._distance_matrix[i,j] for j in index_q[q] if i!=j])/(self._nb_ids_by_clusters[n]-1)

            vertex_cluster_distance[i] = tmp

        return vertex_cluster_distance


    def vertex_distance2cluster_center(self):
        """
        Compute the distance between a vertex and the center of its group.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        D_iq = self.vertex2clusters_distance()
        vertex_distance2center = {}
        for i in xrange(self._N):
            vertex_distance2center[i] = D_iq[i][self._clustering[i]]

        return vertex_distance2center


    def plot_vertex_distance2cluster_center(self):
        """
        Plot the distance between a vertex and the center of its group.

        :Parameters:
         - `distance_matrix` (np.array) - distance matrix used to create the clustering.
         - `clustering` (list) - list giving the resulting clutering.

        :WARNING: `distance_matrix` and `clustering` should obviously ordered the same way!
        """
        vtx2center = self.vertex_distance2cluster_center()
        index_q = {}
        fig = plt.figure()
        for n,q in enumerate(self._clusters_ids):
            index_q[q] = np.where(self._clustering == q)[0]
            vector = [vtx2center[i] for i in index_q[q]]
            vector.sort()
            plt.plot( vector, label = "Cluster "+str(self._clusters_ids[n]) )
            plt.axis([0,max(self._nb_ids_by_clusters), min(vtx2center.values()), max(vtx2center.values())])

        plt.legend(ncol=3)


    def clustered_temporal_property_graph(self):
        """
        Create a clustered version of the temporal_property_graph `graph`, representing the spatio-temporal relations between clusters.

        :Returns:
         - `tpg` (temporal_property_graph) - represent the spatio-temporal relations between clusters.
        """
        # - Start by retreiving the representativity of each time points (index) and clusters
        graph = self.clusterer.graph
        tp_c = self.time_point_by_clusters(graph)

        # -- Create a list of spatial `graphs` at each time point (no spatial relation taken into account!)
        from openalea.container.property_graph import PropertyGraph
        graphs = []
        for t in xrange(graph.nb_time_points+1):
            pg = PropertyGraph()
            vertex2label = {}
            # - Add a vertex for each cluster `q` at time `t`:
            for q in self._clusters_ids:
                if tp_c.has_key((t,q)):
                    vertex2label[pg.add_vertex(q)]=(t,q)
            # - Save the couples (time,cluster) as 'label':
            pg.add_vertex_property('label')
            pg.vertex_property('label').update(vertex2label)
            graphs.append(pg)

        # -- Recover the lineage and the number of children between (temporally) successive clusters :
        lineage = [{},{},{},{}]
        quantif = [{},{},{},{}]
        for t, q in tp_c.keys():
            if t < graph.nb_time_points: # there will be no children from the last time point
                vids_in_q_at_t = [k for k in self._ids_by_clusters[q] if k in graph.vertex_at_time(t)]
                lineage[t][q]=[]
                quantif[t][q]={}
                for vid in vids_in_q_at_t:
                    children = list(graph.children(vid))
                    if children!=[]:
                        for child in children:
                            child_cluster = self._clustering[self._vtx_list.index(child)]
                            if child_cluster not in lineage[t][q]:
                                lineage[t][q].append(child_cluster)
                            if not quantif[t][q].has_key(child_cluster):
                                quantif[t][q][child_cluster]=1
                            else:
                                quantif[t][q][child_cluster]+=1

        # -- Create the `TemporalPropertyGraph`
        from openalea.container.temporal_property_graph import TemporalPropertyGraph
        tpg = TemporalPropertyGraph()
        tpg.extend(graphs, lineage, graph.graph_property('time_steps'))

        # -- Add 'cluster_size' and 'nb_children' properties:
        from openalea.image.algo.graph_from_image import label2vertex_map
        label2vertex = label2vertex_map(tpg)
        # - Add 'cluster_size' property, i.e. the number of cell in each cluster at a give time:
        tpg.add_vertex_property('cluster_size', dict( [(label2vertex[k],v[1]) for k,v in tp_c.iteritems()] ))
        # - Add 'nb_children' property, i.e. the number of child ren between (temporally) successive clusters:
        from openalea.image.algo.graph_from_image import vertexpair2edge_map, add_edge_property_from_dictionary
        add_edge_property_from_dictionary(tpg, 'nb_children', dict( [((label2vertex[(t,q)],label2vertex[(t+1,child)]),value) for t in xrange(len(quantif)) for q in quantif[t] for child,value in quantif[t][q].iteritems()]), vertexpair2edge_map(tpg))

        self.clustered_graph = tpg

        return tpg


    def plot_clustered_temporal_property_graph(self, no_spatiotemp_data_cluster = 'auto'):
        """
        Graphical representations of the clustered spatio-temporal graph.
        
        :Parameters:
         - `clustered_graph` (temporal_property_graph) - a clustered spatio-temporal graph
         - `no_spatiotemp_data_cluster` (str|int|list) - filter for displaying the cluster made of cells without spatio-temporal properties. If 'auto' the cluster is obtained automatically by using the cluster defined at the first time point. A integer or a list of cluster can be provided too.
        """
        # -- Use or create the clustered version of the `TemporalPropertyGraph`:
        if self.clustered_graph is None:
            clustered_graph = self.clustered_temporal_property_graph()
        else:
            clustered_graph = self.clustered_graph

        # -- Translate the temporal_property_graph into a NetworkX graph:
        G = clustered_graph.to_networkx()

        # -- Define possition of each node:
        pos={}
        for node in G.node.keys():
            x = G.node[node]['index']
            y = G.node[node]['old_label']
            pos[node] = (x,y)

        # -- Retreive node informations:
        node_cluster = np.array([G.node[k]['old_label'] for k in G.node.keys()])
        node_size = np.array([G.node[k]['cluster_size'] for k in G.node.keys()])

        # -- Filter for displaying the cluster made of cells without spatio-temporal properties:
        if no_spatiotemp_data_cluster == None:
            no_spatiotemp_data_cluster = []
        if no_spatiotemp_data_cluster == 'auto':
            xy = np.array(pos.values())
            no_spatiotemp_data_cluster = list(xy[np.where(xy[:,0]==0),1])
        if isinstance(no_spatiotemp_data_cluster,int):
            no_spatiotemp_data_cluster = [no_spatiotemp_data_cluster]

        import networkx as nx
        # -- Draw the graphs:
        fig = plt.figure(figsize=(15,6),dpi=100)
        fig.subplots_adjust( wspace=0.1, left=0.04, right=0.96, top=0.9)
        plt.suptitle('Clustered SpatioTemporal Graph of {}'.format(self.clustering_name))
        fig.add_subplot(121)
        # -- Nodes plotting:
        nx.draw_networkx_nodes(G, pos, node_size=node_size*5, node_color=node_cluster, vmin=min(node_cluster), vmax=max(node_cluster),cmap='jet')
        # -- Edges plotting:
        # - Edge sizes depend on the number of children going to a cluster divided by the number of children from that cluster:
        edge_size = np.array([G.edge[id1][id2]['nb_children']/float(sum([G.edge[id_1][id_2]['nb_children'] for id_1,id_2 in G.edges() if id1==id_1])) for id1,id2 in G.edges()])
        edge_style = np.array(['solid' if G.node[id1]['old_label'] not in no_spatiotemp_data_cluster else 'dotted' for id1,id2 in G.edges()])
        # - Draw edges:
        nx.draw_networkx_edges(G, pos, width=5*edge_size, style=edge_style)
        # - Axes labels and plot title:
        plt.xlabel('Successive time points')
        plt.ylabel('Cluster id')
        plt.title('Edge sizes are related to were children go to.')

        fig.add_subplot(122)
        # -- Nodes plotting:
        nx.draw_networkx_nodes(G, pos, node_size=node_size*5, node_color=node_cluster, vmin=min(node_cluster), vmax=max(node_cluster),cmap='jet')
        # -- Edges plotting:
        # - Edge sizes depend on the number of children going to a cluster divided by the number of children in that cluster:
        edge_size = np.array([G.edge[id1][id2]['nb_children']/float(G.node[id2]['cluster_size']) for id1,id2 in G.edges()])
        edge_style = np.array(['solid' if G.node[id1]['old_label'] not in no_spatiotemp_data_cluster else 'dotted' for id1,id2 in G.edges()])
        # - Draw edges:
        nx.draw_networkx_edges(G, pos, width=5*edge_size, style=edge_style)
        # - Axes labels and plot title:
        plt.xlabel('Successive time points')
        plt.ylabel('Cluster id')
        plt.title('Edge sizes are related to were children come from.')


    def nonHomogen_Markov_Chain(self):
        """ Function doc """
        # -- Use or create the clustered version of the `TemporalPropertyGraph`:
        if self.clustered_graph is None:
            clustered_graph = self.clustered_temporal_property_graph()
        else:
            clustered_graph = self.clustered_graph

        # -- We create usefull variables and dictionary:
        nb_clusters = self._nb_clusters
        from openalea.image.algo.graph_from_image import label2vertex_map
        index_cluster_id2vtx = label2vertex_map(clustered_graph)
        vtx2index_cluster_id = dict( (v,k) for k,v in index_cluster_id2vtx.iteritems())

        # -- Initialisation of transition and initial probability matrix:
        p_init = []
        for t in xrange(clustered_graph.nb_time_points+1):
            # - For each time point we have an initial proba matrix
            p_init.append(np.zeros((nb_clusters,)))

        p_trans = []
        for t in xrange(clustered_graph.nb_time_points):
            # - For each time interval we have an homogen transition proba matrix
            p_trans.append(np.zeros((nb_clusters, nb_clusters)))

        # -- Filling up initial probability matrix:
        for vid in clustered_graph.vertices():
            # - For each state without parent we save its size (number of individual)
            if clustered_graph.parent(vid) == set([]):
                index, label = vtx2index_cluster_id[vid]
                p_init[index][label] = clustered_graph.vertex_property('cluster_size')[vid]

        # - We now normalise by the number of new individual at each time point:
        for t in xrange(clustered_graph.nb_time_points+1):
            if float(sum(p_init[t])) != 0.:
                p_init[t] = p_init[t]/float(sum(p_init[t]))

        # -- Filling up transition probability matrix:
        for eid in clustered_graph.edges():
            # - For each edges between two states we save the number of children going from one to another
            vid1, vid2 = clustered_graph.edge_vertices(eid)
            index1, label1 = vtx2index_cluster_id[vid1]
            index2, label2 = vtx2index_cluster_id[vid2]
            p_trans[index2-1][label1,label2] = clustered_graph.edge_property('nb_children')[eid]

        # - We now normalise by the total number of children from each state (per lines in the matrix)
        for t in xrange(clustered_graph.nb_time_points):
            for i in xrange(nb_clusters):
                if float(sum(p_trans[t][i,])) != 0.:
                    p_trans[t][i,] = p_trans[t][i,]/float(sum(p_trans[t][i,]))

        return p_init, p_trans


    def update_cluster_labels(self, old2new_labels, contruct_clustered_graph = True):
        """
        Change the cluster labels according to given info in `old2new_labels`.

        :Parameter:
         - `old2new_labels` (dict) - translation dictionary
        """
        assert isinstance(old2new_labels, dict)
        self.clusterer._clustering = [old2new_labels[k] for k in self._clustering]

        self.__init__( self.clusterer, contruct_clustered_graph )
        print "Clustering labels have been udpated !"



def cluster2labels(clusters_dict):
    """
    Create a dict *key=clusters; *labels=ids from a dict *key=ids; *labels=clusters.
    """
    cluster2labels = {}
    for k,v in clusters_dict.iteritems():
        try:
            cluster2labels[v].append(k)
        except:
            cluster2labels[v] = []

    return cluster2labels


def cost_function(ids_1, ids_2, similarity = False):
    """
    The matching elements cost function (dissimilarity):
    $$ D(a,b) = 1 - (2* intersect(a,b)) / (N_a + N_b), $$
     where N_a and N_b are the number of elements in ensemble a and b.

    :Parameters:
     - `ids_1` (list|set) - list or set of id-like elements belonging to a cluster
     - `ids_2` (list|set) - list or set of id-like elements belonging to another cluster (from another clustering!)
     - `similarity` (bool) - if True, return similarity function instead of dissimilarity
    """
    if isinstance(ids_1, list):
        ids_1 = set(ids_1)
    if isinstance(ids_2, list):
        ids_2 = set(ids_2)
    if similarity:
        return float(2*len(ids_1 & ids_2))/(len(ids_1)+len(ids_2))
    else:
        return 1-float(2*len(ids_1 & ids_2))/(len(ids_1)+len(ids_2))


def ensemble_cost_function( cluster2labels_1, cluster2labels_2, similarity = False ):
    """
    Cost function between two clusters relating to the number of common ids in them.

    :Parameters:
     - `cluster2labels_1` (dict) - 
     - `cluster2labels_2` (dict) - 
     - `similarity` (bool) - if True, return similarity function instead of dissimilarity
    """
    cost_triplets = []
    for clusters_1, ids_1 in cluster2labels_1.iteritems():
        for clusters_2, ids_2 in cluster2labels_2.iteritems():
            if set(ids_1) & set(ids_2) != set([]):
                cost_triplets.append([clusters_1, clusters_2, cost_function(ids_1, ids_2)])

    return cost_triplets


def cluster_matching(clusters_dict_1, clusters_dict_2, return_all = False):
    """
    Function calling the BipartiteMatching C++ code to match clusters based on a Minimum cost flow algorithm over their ids composition.
    :Parameters:
    
    """
    from openalea.tree_matching.bipartitematching import BipartiteMatching
    c2l1 = cluster2labels(clusters_dict_1)
    c2l2 = cluster2labels(clusters_dict_2)
    res = BipartiteMatching(c2l1.keys(), c2l2.keys(), ensemble_cost_function(c2l1,c2l2), [1.0 for i in xrange(len(c2l1))], [1.0 for i in xrange(len(c2l2))])
    match = res.match()

    if return_all:
        return match
    else:
        return match[1]


class ClustererComparison:
    """
    """
    def __init__(self, clustering_1, clustering_2):
        # -- Initialisation:
        if clustering_1.__class__.__name__ == 'ClustererChecker':
            self.clustering_1 = dict(zip(clustering_1._vtx_list, clustering_1._clustering))
        else:
            assert isinstance(clustering_1, dict)
            self.clustering_1 = clustering_1
        if clustering_2.__class__.__name__ == 'ClustererChecker':
            self.clustering_2 = dict(zip(clustering_2._vtx_list, clustering_2._clustering))
        else:
            assert isinstance(clustering_2, dict)
            self.clustering_2 = clustering_2

        # -- Matching clusters:
        print "Matching clusters by a Minimum cost flow algorithm base on their ids composition."
        matching = cluster_matching(self.clustering_1, self.clustering_2, True)
        self.matching_score = matching[0]
        print "Total cost of the flow: {}".format(self.matching_score)
        self.matched_clusters = matching[1]
        print "Matched clusters : {}".format(self.matched_clusters)
        self.unmatched_clusters_1 = matching[2]
        self.unmatched_clusters_2 = matching[3]
        if self.unmatched_clusters_1 != []:
            self.all_matched_1=False
            print "Unmatched clusters from `clustering_1`: {}".format(self.unmatched_clusters_1)
        else:
            self.all_matched_1=True
            print "All clusters from `clustering_1` have been matched !"
        if self.unmatched_clusters_2 != []:
            self.all_matched_2=False
            print "Unmatched clusters from `clustering_2`: {}".format(self.unmatched_clusters_2)
        else:
            self.all_matched_2=True
            print "All clusters from `clustering_2` have been matched !"


    def relabelling_dictionary_1(self):
        """
        """
        relabelling_dict = dict( (id1,id2) for id1,id2 in self.matched_clusters )
        if not self.all_matched_1:
            max_1 = max(self.clustering_1.values())
            for n,k in enumerate(self.unmatched_clusters_1):
                relabelling_dict.update({k:max_1+n+1})

        return relabelling_dict

    def relabelling_dictionary_2(self):
        """
        """
        relabelling_dict = dict( (id2,id1) for id1,id2 in self.matched_clusters )
        if not self.all_matched_2:
            max_1 = max(self.clustering_2.values())
            for n,k in enumerate(self.unmatched_clusters_2):
                relabelling_dict.update({k:max_1+n+1})

        return relabelling_dict




#~ def renorm(line, column, mat_topo, var_mat, temp_mat, w_topo, w_var, w_temp):
    """
    !!! WORKS WITH assemble_matrix_OLD !!!
    """
    #~ w_renorm_topo = 0.
    #~ if w_topo != 0.:
        #~ if np.isnan(mat_topo[line,column]):
            #~ w_renorm_topo = w_topo
            #~ w_topo = 0.
#~ 
    #~ w_renorm_var = 0.
    #~ for n in var_mat:
        #~ if np.isnan(var_mat[n][line,column]):
            #~ w_renorm_var += w_var[n]
            #~ w_var[n] = 0.
#~ 
    #~ w_renorm_temp = 0.
    #~ for n in temp_mat:
        #~ if np.isnan(temp_mat[n][line,column]):
            #~ w_renorm_temp += w_temp[n]
            #~ w_temp[n] = 0.
#~ 
    #~ renorm = (1.-(w_renorm_topo+w_renorm_var+w_renorm_temp))
    #~ if renorm != 0.:
        #~ return w_topo/renorm, np.array(w_var)/renorm if w_var!=[] else [], np.array(w_temp)/renorm if w_temp!=[] else []
    #~ else:
        #~ return w_topo, w_var, w_temp
