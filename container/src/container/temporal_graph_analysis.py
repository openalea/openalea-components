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
import sys

def differential(graph, vertex_property_name, func, vids=None, n=1):
    """
       
    :Parameters:
    - 'graph' : a TPG.
    - 'vertex_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vids' : by default a vertex id or a list of vertex ids. If 'vids=None' the mean absolute deviation will be computed for all ids present in the graph provided.
    - 'n' : neighborhood at distance 'n' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.

    :Return:
    - a single value if vids is an interger, or a dictionnary of *keys=vids and *values= Mean absolute deviation
    """

    # -- If no vids provided we compute the mean absolute deviation for all keys present in the graph_property_name:
    try :
        if vids==None:
            vids=graph.vertex_property(vertex_property_name).keys()
    except PropertyError as e:
        print "Error", vertex_property_name, "is not a vertex_property of", graph
        print e
        sys.exit(0)
    
    
    if type(vids)==int:
        return func(graph, vertex_property_name, vids, n)
    else:
        l={}
        for k in vids:
            if k%10==0:
                print k,'/',len(vids)
            l[k]=func(graph, vertex_property_name, k, n)
        return l


def mean_abs_dev(graph, vertex_property_name, vid, n=1):
    """
    Sub-function computing the mean sum of absolute difference between ONE vertex ('vid') and its neighbors at rank 'n'.

    :Parameters:
    - 'graph' : a TPG.
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vid' : a vertex id.
    - 'n' : neighborhood at distance 'n' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.
    
    :Return:
    - a single value = the mean absolute deviation between vertex 'vid' and its neighbors at rank 'n'.
    """
    tmp=0
    nei=graph.neighborhood(vid,n,edge_type='s')
    nei.remove(vid)
    p=graph.vertex_property(vertex_property_name)
    if len(nei)!=0: # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in nei:
            tmp=tmp+abs(p[vid]-p[i])
    else:
        print "No neighbors found for 'vid' =", vid, "..."
    
    return tmp/float(len(nei)-1)


def laplacian(graph, vertex_property_name, vid, n=1):
    """
    Sub-function computing the laplacian between ONE vertex ('vid') and its neighbors at rank 'n'.

    :Parameters:
    - 'graph' : a TPG.
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vid' : a vertex id.
    - 'n' : neighborhood at distance 'n' will be used.
    - 'edge_type' : type of edges to browse; 's' = structural, 't' = temporal.
    
    :Return:
    - a single value = laplacian between vertex 'vid' and its neighbors at rank 'n'.
    """
    tmp=0
    nei=graph.neighborhood(vid,n,edge_type='s')
    nei.remove(vid)
    p=graph.vertex_property(vertex_property_name)
    if len(nei)!=0: # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in nei:
            tmp=tmp+p[i]
    else:
        print "No neighbors found for 'vid' =", vid, "..."
    
    return p[vid]-tmp/float(len(nei)-1)


def temporal_change(graph, vertex_property_name, vid, n=1):
    """
    Sub-function computing the temporal change between ONE vertex ('vid') and its descendants at rank 'n'.

    :Parameters:
    - 'graph' : a TPG.
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vid' : a vertex id.
    - 'n' : neighborhood at distance 'n' will be used.
    
    :Return:
    - a single value = temporal change between vertex 'vid' and its neighbors at rank 'n'.
    """
    tmp=0
    nei=graph.neighborhood(vid,n,edge_type='t')
    nei.remove(vid)
    p=graph.vertex_property(vertex_property_name)
    if len(nei)!=0: # if ==0 it's mean that there is no neighbors for the vertex vid.
        for i in nei:
            tmp=tmp+p[i]
    else:
        print "No neighbors found for 'vid' =", vid, "..."
    
    return tmp-p[vid]


def relative_temporal_change(graph, vertex_property_name, vid, n=1):
    """
    Sub-function computing the relative temporal change between ONE vertex ('vid') and its descendants at rank 'n'.

    :Parameters:
    - 'graph' : a TPG.
    - 'graph_property_name' : the dictionnary TPG.vertex_property('property-of-interest').
    - 'vid' : a vertex id.
    - 'n' : neighborhood at distance 'n' will be used.
    
    :Return:
    - a single value = relative temporal change between vertex 'vid' and its neighbors at rank 'n'.
    """
    p=graph.vertex_property(vertex_property_name)
    return temporal_change(graph, vertex_property_name, vid, n)/p[vid]

#~ def dev_abs(graph,graph_property,return_list=False):
	#~ """
	#~ Mean absolute deviation : sum of absolute difference between one cell and its neighbors.
	#~ 
	#~ :INPUTS:
		#~ - dic: dictionnary of any values by cells (*keys= cell ids; *values= any float)
		#~ - graph: temporal_property_graph related to the dic.
	#~ """
	#~ # -- If 'graph_property' is a string, we start by making sure that the graph property already exist!
	#~ from vplants.tissue_analysis.mesh_computation import is_instance_method
	#~ if is_instance_method(graph_property):
		#~ tmp={}
		#~ print 'creating dictionnary from instance method:'
		#~ for i in graph.vertex_property('label'):
			#~ if isinstance(graph_property(i),int):
				#~ tmp[i]=graph_property(i)
			#~ else:
				#~ import sys
				#~ print "Your instance method return ",str(type(graph_property(i)))," and I don't know what to do with that!! Interger needed :)..."
				#~ sys.exit(1)
		#~ graph_property=tmp
#~ 
	#~ if type(graph_property)==type(str('str')):
		#~ if graph_property not in graph.vertex_property_name():
			#~ import sys
			#~ sys.exit(1)
		#~ else:
			#~ p=graph.vertex_property(str(graph_property))
	#~ else:
		#~ p=graph_property
	#~ 
	#~ # -- We compute the sum of absolute deviation:
	#~ l={}
	#~ for k in p:
		#~ tmp=0
		#~ if graph.nb_neighbors(k)!=0:
			#~ n=0
			#~ for i in graph.neighbors(k):
				#~ if i in p.keys():
					#~ n+=1 # We want to be sure that we normalise by the number of neighbors we used to compute the deviance.
					#~ tmp=tmp+abs(p[k]-p[i])
				#~ else:
					#~ print 'The neighbours', str(i),'of the vertex',str(k),'is ignored while computing the sum of absolute deviation.'
			#~ l[k]=tmp/float(n)
	#~ 
	#~ if return_list:
		#~ return l.values()
	#~ else:
		#~ return l
	
#~ def laplacian(graph,graph_property,return_list=False,labels=None):
	#~ """
	#~ Calcul la somme des ecarts absolu a ses voisines pour chaque cellule.
	#~ 
	#~ :INPUTS:
		#~ - dic: dictionnary of any values by cells (*keys= cell ids; *values= any float)
		#~ - graph: temporal_property_graph related to the dic.
	#~ """
	#~ from vplants.tissue_analysis.mesh_computation import is_instance_method
	#~ if labels==None:
		#~ labels=graph.vertex_property('label').values()
	#~ 
	#~ if is_instance_method(graph_property):
		#~ tmp={}
		#~ print 'creating dictionnary from instance method:'
		#~ for i in labels:
			#~ if isinstance(graph_property(i),int):
				#~ tmp[i]=graph_property(i)
			#~ else:
				#~ import sys
				#~ print "Your instance method return ",str(type(graph_property(i)))," and I don't know what to do with that!! Interger needed :)..."
				#~ sys.exit(1)
		#~ graph_property=tmp
#~ 
	#~ import numpy as np
	#~ # -- If 'graph_property' is a string, we start by making sure that the graph property already exist!
	#~ p={}
	#~ if type(graph_property)==type(str('str')):
		#~ if graph_property not in graph.vertex_property_name():
			#~ import sys
			#~ sys.exit(1)
		#~ else:
			#~ for i in labels:
				#~ p[i]=graph.vertex_property(str(graph_property))[i]
	#~ elif type(graph_property)==type({}):
		#~ p=graph_property
	#~ 
	#~ # -- We compute the sum of absolute deviation:
	#~ l={}
	#~ for k in p:
		#~ tmp=[]
		#~ if graph.nb_neighbors(k)!=0:
			#~ for i in graph.neighbors(k):
				#~ if i in p.keys():
					#~ tmp.append(p[i])
				#~ else:
					#~ print 'The neighbours', str(i),'of the node',str(k),'is ignored while computing the sum of absolute deviation.'
			#~ l[k]=p[k]-float(np.mean(tmp))
			#~ 
	#~ if return_list:
		#~ return l.values()
	#~ else:
		#~ return l



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
