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


def dev_abs_sum(dic,graph,order=1):
	"""
	Calcul la somme des écarts absolu à ses voisines pour chaque cellule.
	
	:INPUTS:
		- dic: dictionnary of any values by cells (*keys= cell ids; *values= any float)
		- graph: temporal_property_graph related to the dic.
		- order:
	"""
	l={}
	for k,v in graph.vertex_property('old_label').iteritems():
		if v in dic.keys():
			tmp=0
			for i in g.neighbors(k):
				tmp=tmp+abs(dic[k]-dic[i])
			l[k]=tmp
	
	return l
