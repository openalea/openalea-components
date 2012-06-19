########################################################################
###   TESTS :
########################################################################
import numpy as np
from scipy import ndimage

from openalea.image.spatial_image import SpatialImage
from openalea.image.serial.basics import imread
from openalea.container import PropertyGraph, TemporalPropertyGraph

import openalea.container.temporal_graph_creation
reload( openalea.container.temporal_graph_creation )
from openalea.container.temporal_graph_creation import *

from vplants.tissue_analysis.growth_analysis import L1_cells_list,border_cells

t1=imread('p114-t1_imgSeg.inr.gz')
t2=imread('p114-t2_imgSeg.inr.gz')
t3=imread('p114-t3_imgSeg.inr.gz')
L1_1=list(set(L1_cells_list(t1))-set(border_cells(t1)))
L1_2=list(set(L1_cells_list(t2))-set(border_cells(t2)))
L1_3=list(set(L1_cells_list(t3))-set(border_cells(t3)))


from openalea.image.algo.graph_from_image import graph_from_image
graph_1=graph_from_image(t1,labels=L1_1)
graph_2=graph_from_image(t2,labels=L1_2)
graph_3=graph_from_image(t3,labels=L1_3)


import LienTissuTXT
l12=LienTissuTXT.LienTissuTXT("suiviExpert_01.txt")
mapping=l12.cellT1_cellT2

g = TemporalPropertyGraph()
g.extend([graph_1,graph_2],[mapping])


# Ajout de propriétés:
from vplants.tissue_analysis.growth_analysis import cell_volume,dict_cells_slices,dict_cells_coordinates, geometric_median, centroid
dic1_L1=dict_cells_slices(t1,L1_1)
dic2_L1=dict_cells_slices(t2,L1_2)

#~ pos1=geometric_median(dict_cells_coordinates(t1,dic1_L1))
pos1=centroid(dict_cells_coordinates(t1,dic1_L1))
pos2=centroid(dict_cells_coordinates(t2,dic2_L1))
g=add_prop2vrtx(g,pos1,'centroid')
g=add_prop2vrtx(g,pos2,'centroid')

v1_L1=cell_volume(dict_cells_coordinates(t1,dic1_L1,L1_1),L1_1)
v2_L1=cell_volume(dict_cells_coordinates(t2,dic2_L1,L1_2),L1_2)
g=add_prop2vrtx(g,v1_L1,'volume')
#~ g=add_prop2vrtx(g,v2_L1,'volume')

import openalea.container.temporal_graph_analysis
reload( openalea.container.temporal_graph_analysis )
from openalea.container.temporal_graph_analysis import dev_abs
from openalea.container.temporal_graph_creation import add_prop2vrtx

g=add_prop2vrtx(g,dev_abs(g,'volume'),'abs_dev_vol')

l=[]
cmap=[]
pos=[]
G=g.to_networkx()
for i in G.nodes():
	if G.node[i]['index']==0:
		l.append(i)
		cmap.append(G.node[i]['volume'])
		pos.append(G.node[i]['centroid'])

import matplotlib.pyplot as plt
plt.figure(figsize=(8,8))
nx.draw_networkx( G,pos=pos, node_size=80, nodelist=l ,node_color= cmap)
plt.axis('off')
plt.show()


import networkx as nx
import numpy as np
from enthought.mayavi import mlab

xyz=[]
scalars=[]
n=0
renum={}
for k,v in g.vertex_property('abs_dev_vol').iteritems():
	if k in g.vertex_property('centroid'):
		# node position
		xyz.append(g.vertex_property('centroid')[k])
		# scalar colors
		scalars.append(g.vertex_property('abs_dev_vol')[k])
		renum[k]=n
		n+=1
#~ 
#~ lines=[]
#~ for k,v in g.edge_property('source-target').iteritems():
	#~ if ((v[0] in renum.keys()) and (v[1] in renum.keys())):
		#~ lines.append( g.edge_property('source-target')[k] )

xyz=np.array(xyz)

mlab.figure(bgcolor=(0, 0, 0))
mlab.clf()

pts = mlab.points3d(xyz[:,0], xyz[:,1], xyz[:,2], scalars, scale_factor=10, scale_mode='none', colormap='hot')
mlab.scalarbar(pts,'Mean absolute deviation',orientation='horizontal',nb_colors=256)
for index, label in enumerate(renum.keys()):
	tmplabel = mlab.text3d( xyz[index,0], xyz[index,1], xyz[index,2], str(label), scale=0.50, color = (1,1,1) )

