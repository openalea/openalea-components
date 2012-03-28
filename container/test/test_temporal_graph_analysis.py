from openalea.container.temporal_graph_analysis import *
from temporal_property_graph_input import create_TemporalGraph


def create_temporal_property_graph():
    """ Test of laplacian function with TemporalPropertyGraph """
    g = create_TemporalGraph()
    prop = dict([(i,float(i)) for i in g.vertices()])
    g.add_vertex_property('property',prop)
    return g
    
def test_laplacian():
    g = create_temporal_property_graph()
    assert laplacian(g,'property', range(7)) == { 0 : -1.,  1 : 1., 2 : -1., 3 : (3-11/3.), 4 : 0., 5 : (5-13/3.), 6 : 1. }
    
def test_mean_abs_dev():
    g = create_temporal_property_graph()
    assert mean_abs_dev(g,'property', range(7)) == { 0 : 1,  1 : 1, 2 : 1., 3 : 4/3., 4 : 1, 5 : 4/3., 6 : 1 }
    
def test_temporal_change():
    g = create_temporal_property_graph()
    res = { 0 : 9,  1 : 10, 2 : 13, 3 : 6, 4 : 42, 5 : 24, 6 : 64, 7 : 0 }
    assert temporal_change(g,'property', range(8)) == res

def test_relative_temporal_change():
    g = create_temporal_property_graph()
    res = { 1 : 10, 2 : 13/2., 3 : 2, 4 : 10.5, 5 : 4.8, 6 : 64/6., 7 : 0 }
    assert relative_temporal_change(g,'property', range(1,8)) == res