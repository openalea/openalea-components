#from _container import *
#from id_dict import IdDict
from utils import IdDict
from graph import Graph
from grid import Grid
from relation import Relation
from topomesh import Topomesh
from topomesh_algo import clean_geometry,clean_orphans,\
						expand,border,shrink,\
						expand_to_border,expand_to_region,external_border,\
						clean_duplicated_borders,merge_wisps
