# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2012 INRIA - CIRAD - INRA
#
#       File author(s): Jonathan Legrand
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
        - 'vertex_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
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
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
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
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
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
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
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
        - 'vertex_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
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
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest').
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
    - 'vertex_property' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vid' : a vertex id.
    - 'rank' : neighborhood at distance 'rank' will be used.
    
    :Return:
    - a single value = relative temporal change between vertex 'vid' and its neighbors at rank 'rank'.
    """
    return temporal_change(graph, vertex_property, vid, rank) / vertex_property[vid]




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
