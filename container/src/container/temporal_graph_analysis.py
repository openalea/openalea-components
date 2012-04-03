# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2012 INRIA - CIRAD - INRA
#
#       File author(s):  Jonathan Legrand
#                        Frederic Boudon
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
################################################################################
"""This module helps to analyse TemporalPropertyGraph from Spatial Images."""
 
from interface.property_graph import IPropertyGraph, PropertyError


def __normalized_parameters(func):
    def wrapped_function(graph, vertex_property, vids = None, rank = 1, edge_type='s' , verbose = False):
        """
           
        :Parameters:
        - 'graph' : a TPG.
        - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
        - 'vids' : by default a vertex id or a list of vertex ids. If 'vids=None' the mean absolute deviation will be computed for all ids present in the graph provided.
        - 'rank' : neighborhood at distance 'rank' will be used.
        - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.

        :Return:
        - a single value if vids is an interger, or a dictionnary of *keys=vids and *values= Mean absolute deviation
        """
        # if a name is given, we use vertex_property stored in the graph with this name.
        if isinstance(vertex_property,str):
            vertex_property = graph.vertex_property(vertex_property)
        # -- If no vids provided we compute the function for all keys present in the vertex_property
        if vids==None:
            vids = vertex_property.keys()
                
        if type(vids)==int:
            # for single id, compute single result
            return func(graph, vertex_property, vids, rank, edge_type)
        else:
            # for set of ids, we compute a dictionary of resulting values.
            l={}
            for k in vids:
                if verbose and k%10==0: print k,'/',len(vids)
                l[k] = func(graph, vertex_property, k, rank, edge_type)
            return l        
    return  wrapped_function


@__normalized_parameters
def laplacian(graph, vertex_property, vid, rank=1, edge_type='s'):
    """
    Sub-function computing the laplacian between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.
    
    :Return:
    - a single value = laplacian between vertex 'vid' and its neighbors at rank 'rank'.
    """
    vid_neighborhood = graph.neighborhood(vid,rank,edge_type=edge_type)
    vid_neighborhood.remove(vid)
    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + vertex_property[i]
    
        return ivalue - (result / float(nb_neighborhood))
    else:
        return 0

@__normalized_parameters
def mean_abs_dev(graph, vertex_property, vid, rank=1, edge_type='s'):
    """
    Sub-function computing the mean sum of absolute difference between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.
    
    :Return:
    - a single value = the mean absolute deviation between vertex 'vid' and its neighbors at rank 'rank'.
    """
    vid_neighborhood = graph.neighborhood(vid,rank,edge_type=edge_type)
    vid_neighborhood.remove(vid)
    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + abs(ivalue - vertex_property[i])
    
        return result / float(nb_neighborhood)
    else:
        return 0

@__normalized_parameters
def change(graph, vertex_property, vid, rank=1, edge_type='t'):
    """
    Sub-function computing the laplacian between ONE vertex ('vid') and its neighbors at rank 'rank'.

    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.
    
    :Return:
    - a single value = laplacian between vertex 'vid' and its neighbors at rank 'rank'.
    """
    vid_neighborhood = graph.neighborhood(vid,rank,edge_type=edge_type)
    vid_neighborhood.remove(vid)
    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + vertex_property[i]
    
        return result - ivalue
    else:
        return 0

def __normalized_temporal_parameters(func):
    def wrapped_function(graph, vertex_property, vids = None, rank = 1, verbose = False):
        """
           
        :Parameters:
        - 'graph' : a TPG.
        - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest'), or the string 'property-of-interest'.
        - 'vids' : by default a vertex id or a list of vertex ids. If 'vids=None' the mean absolute deviation will be computed for all ids present in the graph provided.
        - 'rank' : neighborhood at distance 'rank' will be used.
        - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.

        :Return:
        - a single value if vids is an interger, or a dictionnary of *keys=vids and *values= Mean absolute deviation
        """
        # if a name is given, we use vertex_property stored in the graph with this name.
        if isinstance(vertex_property,str):
            vertex_property = graph.vertex_property(vertex_property)
        # -- If no vids provided we compute the function for all keys present in the vertex_property
        if vids==None:
            vids = vertex_property.keys()
                
        if type(vids)==int:
            # for single id, compute single result
            return func(graph, vertex_property, vids, rank)
        else:
            # for set of ids, we compute a dictionary of resulting values.
            l={}
            for k in vids:
                if verbose and k%10==0: print k,'/',len(vids)
                l[k] = func(graph, vertex_property, k, rank )
            return l        
    return  wrapped_function
    
@__normalized_temporal_parameters
def temporal_change(graph, vertex_property, vid, rank=1):
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
    vid_neighborhood = graph.descendants(vid,rank)
    vid_neighborhood.remove(vid)
    nb_neighborhood = len(vid_neighborhood)

    result = 0
    ivalue = vertex_property[vid]
    if nb_neighborhood != 0 : # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in vid_neighborhood:
            result = result + vertex_property[i]
    
        return result - ivalue
    else:
        return 0

@__normalized_temporal_parameters
def relative_temporal_change(graph, vertex_property, vid, rank=1):
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
    return temporal_change(graph, vertex_property, vid, rank) / vertex_property[vid]


def time_point_property(graph,time_point,vertex_property):
    """
    Allow to extract a property 'vertex_property' from the temporal graph for one time-point.
    
    :Parameters:
    - `graph` TPG to browse;
    - `time_point` integer defining the time-point to consider;
    - `vertex_property` vertex property to extract;
    :Return:
    - dictionnary of vertex property extracted from the time-point 'time_point';
    """
    # if a name is given, we use vertex_property stored in the graph with this name.
    if isinstance(vertex_property,str):
        vertex_property = graph.vertex_property(vertex_property)
        
    if time_point not in graph.vertex_property('index').values():
        print time_point,"not in ",graph

    k=[i for i in graph.vertex_property('index') if graph.vertex_property('index')[i]==time_point]
    tmp={}
    for i in k:
        tmp[i]=vertex_property[i]
    
    return tmp


def strain2D(graph, tp_1, tp_2):
    	"""
	Strain computation based on the 3D->2D->3D GOODALL method.
	
	:INPUTS:
		.t1: t_n Spatial Image containing cells (segmented image)
		.t2: t_n+1 Spatial Image containing cells (segmented image)
		.l12: lineage between t_n & t_n+1;
		.l21: INVERTED lineage between t_n & t_n+1;
		.deltaT: time interval between two time points;
		
	:Variables:
		.v2v_21: vertex (keys=t_n+1) to vertex (values=t_n) association.
		.c2v_1: cells 2 vertex @ t_n
		.v2b_1: vextex 2 barycenters @ t_n
		.v2b_2: vextex 2 barycenters @ t_n+1
	
	:OUTPUTS: (c= keys= mother cell number)
		.sr[c]: Strain Rate = np.log(D_A[0])/deltaT , np.log(D_A[1])/deltaT
		.asr[c]: Areal Strain Rate = (sr1+sr2)
		.anisotropy[c]: Growth Anisotropy = (sr1-sr2)/(sr1+sr2)
		.s_t1[c]: t_n strain cross in 3D (tensor)
		.s_t2[c]: t_n+1 strain cross in 3D (tensor)
	
	########## Relationship between least-squares method and principal components: ##########
	## The first principal component about the mean of a set of points can be represented by that line which most closely approaches the data points 
	#(as measured by squared distance of closest approach, i.e. perpendicular to the line).
	## In contrast, linear least squares tries to minimize the distance in the y direction only.
	## Thus, although the two use a similar error metric, linear least squares is a method that treats one dimension of the data preferentially, while PCA treats all dimensions equally.
	#########################################################################################
	"""
    ## Extract infos form t1:
	v2c_1, c2v_1, v2b_1 = dictionaries(time_point_property(graph,tp1,'cell_vertices'))
	## Extract infos form t2:
	v2c_2, c2v_2, v2b_2 = dictionaries(time_point_property(graph,tp2,'cell_vertices'))

	v2v_21=V2V(l21,v2c_1,v2c_2)
	v2map=V2MAP(l12,v2c_1)
	print 'Percentage of associated Vertex :',float(len(v2v_21))/len(v2map)*100.,'%'

	## Variable creation used to comput the strain.
	v2v_12 = dict((v,k) for k, v in v2v_21.items())
	lsq={}
	s_t1,s_t2={},{}
	sr={}
	asr={}
	anisotropy={}

	for c in l12.keys():
		if c in c2v_1.keys():
			if sum([(c2v_1[c][k] in v2v_12.keys()) for k in range(len(c2v_1[c]))])==len(c2v_1[c]):
				N = len(c2v_1[c])
				if N>2:
					## Retreive positions of the vertices belonging to cell 'c':
					xyz_t1=np.array([v2b_1[c2v_1[c][k]] for k in range(N)])
					xyz_t2=np.array([v2b_2[v2v_12[c2v_1[c][k]]] for k in range(N)])
					## Compute the centroids:
					c_t1=np.array((np.mean(xyz_t1[:,0]),np.mean(xyz_t1[:,1]),np.mean(xyz_t1[:,2])))
					c_t2=np.array((np.mean(xyz_t2[:,0]),np.mean(xyz_t2[:,1]),np.mean(xyz_t2[:,2])))
					## Compute the centered matrix:
					c_xyz_t1=np.array(xyz_t1-c_t1)
					c_xyz_t2=np.array(xyz_t2-c_t2)
					## Compute the Singular Value Decomposition (SVD) of centered coordinates:
					U_t1,D_t1,V_t1=svd(c_xyz_t1, full_matrices=False)
					U_t2,D_t2,V_t2=svd(c_xyz_t2, full_matrices=False)
					V_t1=V_t1.T ; V_t2=V_t2.T
					## Projection of the vertices' xyz 3D co-ordinate into the 2D subspace defined by the 2 first eigenvector
					#(the third eigenvalue is really close from zero confirming the fact that all the vertices are close from the plane -true for external part of L1, not for inner parts of the tissue).
					c_xy_t1=np.array([np.dot(U_t1[k,0:2],np.diag(D_t1)[0:2,0:2]) for k in range(N)])
					c_xy_t2=np.array([np.dot(U_t2[k,0:2],np.diag(D_t2)[0:2,0:2]) for k in range(N)])
					## Compute the Singular Value Decomposition (SVD) of the least-square estimation of A.
					#A is the (linear) transformation matrix in the regression equation between the centered vertices position of two time points:
					lsq[c]=lstsq(c_xy_t1,c_xy_t2)
					##  Singular Value Decomposition (SVD) of A.
					R,D_A,Q=svd(lsq[c][0])
					Q=Q.T
					# Compute Strain Rates and Areal Strain Rate:
					sr[c] = np.log(D_A)/deltaT
					asr[c] = sum(sr[c])
					anisotropy[c]=((sr[c][0]-sr[c][1])/asr[c])
					##  Getting back in 3D: manually adding an extra dimension.
					R=np.hstack([np.vstack([R,[0,0]]),[[0],[0],[1]]])
					D_A=np.hstack([np.vstack([np.diag(D_A),[0,0]]),[[0],[0],[0]]])
					Q=np.hstack([np.vstack([Q,[0,0]]),[[0],[0],[1]]])
					##  Getting back in 3D: strain of cell c represented at each time point.
					s_t1[c] = np.dot(np.dot(np.dot(np.dot(V_t1, R), D_A), R.T), V_t1.T)
					s_t2[c] = np.dot(np.dot(np.dot(np.dot(V_t2, Q), D_A), Q.T), V_t2.T)

	return sr,asr,anisotropy,s_t1,s_t2



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
