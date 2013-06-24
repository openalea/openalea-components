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
__revision__ = " $Id: $ "

import warnings
import numpy as np
from numpy import ndarray
import copy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.axes3d import Axes3D

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

def renorm(line, column, mat_topo, var_mat, temp_mat, w_topo, w_var, w_temp):
    w_renorm_topo = 0.
    if w_topo != 0.:
        if np.isnan(mat_topo[line,column]):
            w_renorm_topo = w_topo
            w_topo = 0.

    w_renorm_var = 0.
    for n in var_mat:
        if np.isnan(var_mat[n][line,column]):
            w_renorm_var += w_var[n]
            w_var[n] = 0.

    w_renorm_temp = 0.
    for n in temp_mat:
        if np.isnan(temp_mat[n][line,column]):
            w_renorm_temp += w_temp[n]
            w_temp[n] = 0.

    renorm = (1.-(w_renorm_topo+w_renorm_var+w_renorm_temp))
    if renorm != 0.:
        return w_topo/renorm, np.array(w_var)/renorm if w_var!=[] else [], np.array(w_temp)/renorm if w_temp!=[] else []
    else:
        return w_topo, w_var, w_temp


class Clusterer:
    """
    """
    def __init__(self, graph, standardisation_method, rank=1):
        # -- Initialisation:
        self.graph = graph
        self.labels = list(graph.vertices())
        self.rank = rank
        self.standardisation_method = standardisation_method

        # -- Variables saving informations:
        self.distance_matrix_dict = {}
        self.distance_matrix_info = {}

        # -- Variables for caching information:
        self._global_distance_matrix = None
        self._global_distance_ids = None
        self._global_distance_weigths = None
        self._global_distance_variables = None


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
            # - We make sure self.distance_matrix_dict can receive the distance mattrix with the name var_id[n]:
            if self.distance_matrix_dict.has_key(var_id[n]):
                raise KeyError("You already have a property named {}".format(var_id[n]))

        print("Computing the distance matrix related to vertex variables...")
        for n, var in enumerate(var_name):
            if isinstance(var,str):
                variable_vector = [self.graph.vertex_property(var)[vid] if self.graph.vertex_property(var).has_key(vid) else None for vid in self.labels]# we need to do that if we want to have all matrix ordered the same way
            if isinstance(var,dict):
                variable_vector = [var[vid] if var.has_key(vid) else None for vid in self.labels]# we need to do that if we want to have all matrix ordered the same way
            # - Adding it tho the list
            self.distance_matrix_dict[var_id[n]] = distance_matrix_from_vector(variable_vector, var_type[n])
            self.distance_matrix_info[var_id[n]] = ('s', var_type[n].lower())

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
            # - We make sure self.distance_matrix_dict can receive the distance mattrix with the name var_id[n]:
            if self.distance_matrix_dict.has_key(var_id[n]):
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
            self.distance_matrix_dict[var_id[n]] = distance_matrix_from_vector(temporal_distance_list, var_type[n])
            self.distance_matrix_info[var_id[n]] = ('t', var_type[n].lower())

        return var_id

    def add_topological_distance_matrix(self, force=False):
        """
        Create the topological distance matrix based on the graph provided and limited to vids if given.
        """
        if self.distance_matrix_dict.has_key("topology") and not force:
            raise KeyError("You already computed the distance matrix 'topology'. Use 'force=True' to do it again.")

        print("Computing the standardized topological distance matrix...")
        import time
        t = time.time()
        # - Extraction of the topological distance between all vertex of a time point:
        topo_dist = dict( [(vid, self.graph.topological_distance(vid, 's',return_inf=False)) for vid in self.labels] )
        # - Transformation into a distance matrix
        self.distance_matrix_dict["topological"] = np.array([[(topo_dist[i][j] if i!=j else 0) for i in self.labels] for j in self.labels])
        self.distance_matrix_info["topological"] = ('s', "rank")
        print "Distance matrix 'topological' created in {0}s".format(time.time() - t)


    def add_euclidean_distance_matrix(self, force=False):
        """
        Create the euclidean distance matrix based on the graph provided and limited to vids if given.
        """
        if self.distance_matrix_dict.has_key("euclidean") and not force:
            raise KeyError("You already computed the distance matrix 'euclidean'. Use 'force=True' to do it again.")

        print("Computing the standardized euclidean distance matrix...")
        import time
        t = time.time()
        # - Extraction of the topological distance between all vertex of a time point:
        bary = self.graph.vertex_property('barycenter')
        self.distance_matrix_dict["euclidean"] = np.array([[np.linalg.norm(bary[i]-bary[j]) for i in self.labels] for j in self.labels])
        self.distance_matrix_info["euclidean"] = ('s', "numeric")
        print "Distance matrix 'euclidean' created in {0}s".format(time.time() - t)


    def remove_distance_matrix(self, var_id):
        """
        remove a distance matrix form the dictionary `self.distance_matrix_dict` and it's attached information in `self.distance_matrix_info`
        """
        pass


    def assemble_matrix(self, variable_names, variable_weights, vids = None):
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
        assert sum(variable_weights)==1.

        # -- Checking all requested information (i.e. variables names) is present in the dictionary `self.distance_matrix_dict`:
        for k in variable_names:
            if not self.distance_matrix_dict.has_key(k):
                if k.lower() == 'topological':
                    self.add_topological_distance_matrix()
                elif k.lower() == 'euclidean':
                    self.add_euclidean_distance_matrix()
                else:
                    raise KeyError("'{}' is not in the dictionary `self.distance_matrix_dict`".format(k))

        # -- Detecting the kind of data we are facing !
        spatial_relation_data, temporal_data, spatial_data = False, False, False
        for k,v in self.distance_matrix_info.iteritems():
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
                mat_topo_dist_standard = standardisation(self.distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                topo_weight = variable_weights[n]
            elif self.distance_matrix_info[var_name][0] == 't':
                temporal_standard_distance_matrix[nb_temp_var] = standardisation(self.distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
                temporal_weights.append(variable_weights[n])
                nb_temp_var += 1
            else:
                spatial_standard_distance_matrix[nb_spa_var] = standardisation(self.distance_matrix_dict[var_name][ids_index,:][:,ids_index], self.standardisation_method)
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

        # - Replacing nan by zeros for computation.
        if spatial_relation_data:
            mat_topo = np.nan_to_num(mat_topo_dist_standard)
        else:
            mat_topo = []
        if spatial_data:
            var_mat = [np.nan_to_num(spatial_standard_distance_matrix[n]) for n in xrange(nb_spa_var)]
        else:
            var_mat, spatial_standard_distance_matrix = [], []
        if temporal_data:
            temp_mat = [np.nan_to_num(temporal_standard_distance_matrix[n]) for n in xrange(nb_temp_var)]
        else:
            temp_mat, temporal_standard_distance_matrix = [], []

        print("Creating the global pairwise weighted standard distance matrix...")
        # Finally making the global weighted pairwise standard distance matrix:
        N = len(vtx_list)
        global_matrix = np.zeros( shape = [N,N], dtype=float )
        w_mat = np.zeros( shape = [N,N], dtype=float )
        for i in xrange(global_matrix.shape[0]):
            for j in xrange(global_matrix.shape[1]):
                if i>j: #D[i,j]=D[j,i] and if i==j, D[i,j]=D[j,i]=0
                    # - Computing weights according to missing values.
                    w_topo, w_var, w_temp = renorm(i,j,mat_topo_dist_standard, spatial_standard_distance_matrix, temporal_standard_distance_matrix, copy.copy(topo_weight), copy.copy(spatial_weights), copy.copy(temporal_weights))
                    # - Pairwise weighted standard distance matrix
                    global_matrix[i,j] = global_matrix[j,i] = w_topo * mat_topo[i,j] + sum([w_var[n]*var_mat[n][i,j] for n in xrange(nb_spa_var)]) + sum([w_temp[n]*temp_mat[n][i,j] for n in xrange(nb_temp_var)])

        # -- We update caching variables only if there is more than ONE pairwise distance matrix :
        self._global_distance_matrix = global_matrix
        self._global_distance_ids = vtx_list
        self._global_distance_weigths = variable_weights
        self._global_distance_variables = variable_names

        return vtx_list, global_matrix


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
                raise ValueError("You have to provide the number of clusters you want for the Ward method.")

        self._clustering = clustering_labels
        if ids is not None:
            return dict([ (label,clustering_labels[n]) for n,label in enumerate(ids) ])
        else:
            return clustering_labels



class ClusteringChecker:
    """
    """
    def __init__(self, vtx_list, distance_matrix, clustering):
        self.vtx_list = vtx_list
        self.distance_matrix = distance_matrix
        self.clustering = clustering

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


    def within_cluster_distance(self):
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


    def between_cluster_distance(self):
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

        if 1 in nb_ids_by_clusters:
            raise ValueError("A cluster contain only one element!")

        D_between = {}
        for n,q in enumerate(clusters_ids):
            index_q = np.where(clustering == q)[0]
            index_not_q = list(set(xrange(len(clustering)))-set(index_q))
            D_between[q] = sum( [distance_matrix[i,j] for i in index_q for j in index_not_q] ) / ( (N-nb_ids_by_clusters[n]) * nb_ids_by_clusters[n])

        if nb_clusters == 1:
            return D_between.values()
        else:
            return D_between


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


    def clusters_separation(self):
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


    def global_cluster_distance(self):
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

            not_found = []
            labels_true, labels_pred = [], []
            max1 = max(dict_labels_expert.values())+1
            max2 = max(self.clustering.values())+1
            for k,v in dict_labels_expert.iteritems():
                if self.clustering.has_key(k):
                    v2 = self.clustering[k]
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

