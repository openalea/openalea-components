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

from vplants.tissue_analysis.growth_analysis import L1_cells_list

t1=imread('p114-t1_imgSeg.inr.gz')
t2=imread('p114-t2_imgSeg.inr.gz')
L1_1=L1_cells_list(t1)
L1_2=L1_cells_list(t2)

pg1=toPropertyGraph(t1,labels=L1_1)
pg2=toPropertyGraph(t2,labels=L1_2)

pgs=[]
pgs.append(pg1)
pgs.append(pg2)

import LienTissuTXT
l12=LienTissuTXT.LienTissuTXT("suiviExpert_01.txt")
mapping=l12.cellT1_cellT2

g = TemporalPropertyGraph()
g.extend(pgs,[mapping])
display_NXgraph(g)

#~ cc,surface=cellNeighbours(t1)
#~ import matplotlib.pyplot as plt
#~ plt.hist(surface.values(),bins=100)
#~ plt.show()

