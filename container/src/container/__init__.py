#from _container import *
#from id_dict import IdDict
from utils import IdDict
from data_prop import Quantity,DataProp
from graph import Graph
from property_graph import PropertyGraph
from tree import Tree, PropertyTree
from grid import Grid
from relation import Relation

################################
#
#       topomesh
#
################################
from topomesh import Topomesh
from topomesh_txt import write_topomesh,read_topomesh
from topomesh_algo import clean_geometry, clean_orphans,\
                          is_flip_topo_allowed, flip_edge,\
                          is_collapse_topo_allowed, collapse_edge,\
                          expand, border, shrink,\
                          expand_to_border, expand_to_region, external_border,\
                          clean_duplicated_borders, merge_wisps,\
                          find_cycles
