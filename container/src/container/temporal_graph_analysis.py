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


def dev_abs(graph,graph_property):
	"""
	Calcul la somme des ecarts absolu a ses voisines pour chaque cellule.
	
	:INPUTS:
		- dic: dictionnary of any values by cells (*keys= cell ids; *values= any float)
		- graph: temporal_property_graph related to the dic.
	"""
	# -- If 'graph_property' is a string, we start by making sure that the graph property already exist!
	if type(graph_property)==type(str('str')):
		if graph_property not in graph.vertex_property_names():
			import sys
			sys.exit(1)
		else:
			p=graph.vertex_property(str(graph_property))
	else:
		p=graph_property
	
	# -- We compute the sum of absolute deviation:
	l={}
	for k in p.keys():
		tmp=0
		if graph.nb_neighbors(k)!=0:
			for i in graph.neighbors(k):
				if i in p.keys():
					tmp=tmp+abs(p[k]-p[i])
				else:
					print 'The neighbours', str(i),'of the vertex',str(k),'is ignored while computing the sum of absolute deviation.'
			l[k]=tmp/graph.nb_neighbors(k)
	
	return l
	
def laplacian(graph,graph_property):
	"""
	Calcul la somme des ecarts absolu a ses voisines pour chaque cellule.
	
	:INPUTS:
		- dic: dictionnary of any values by cells (*keys= cell ids; *values= any float)
		- graph: temporal_property_graph related to the dic.
	"""
	import numpy as np
	# -- If 'graph_property' is a string, we start by making sure that the graph property already exist!
	if type(graph_property)==type(str('str')):
		if graph_property not in graph.vertex_property_names():
			import sys
			sys.exit(1)
		else:
			p=graph.vertex_property(str(graph_property))
	else:
		p=graph_property
	
	# -- We compute the sum of absolute deviation:
	l={}
	for k in p.keys():
		tmp=[]
		if graph.nb_neighbors(k)!=0:
			for i in graph.neighbors(k):
				if i in p.keys():
					tmp.append(p[k])
				else:
					print 'The neighbours', str(i),'of the vertex',str(k),'is ignored while computing the sum of absolute deviation.'
			l[k]=p[i]-np.mean(tmp)
			
	return l
