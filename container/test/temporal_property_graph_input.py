from openalea.container import PropertyGraph
from openalea.container import TemporalPropertyGraph

def create_TemporalGraph():
    """create a graph"""
    g = TemporalPropertyGraph()
    g1 = PropertyGraph()
    g2 = PropertyGraph()
    g3 = PropertyGraph()
    for i in range(2):
        g1.add_vertex()
    for i in range(5):
        g2.add_vertex()
    for i in range(13):
        g3.add_vertex()
    g1.add_edge(0,1)
    for i in range(4):
        g2.add_edge(i, i+1)
    g2.add_edge(1,3)
    for i in range(12):
        g3.add_edge(i, i+1)
    g3.add_edge(0,3)
    g3.add_edge(2,6)
    g3.add_edge(3,6)
    g3.add_edge(4,6)
    g3.add_edge(8,10)
    g3.add_edge(10,12)
    L12={
        0 : [0, 1, 2],
        1 : [3, 4]
        }
    L23={
        0 : [0, 1],
        1 : [2],
        2 : [3, 4, 5, 6],
        3 : [7, 8],
        4 : [9, 10, 11, 12]
        }
    
    g.extend([g1, g2, g3], [L12, L23])
    return g
    