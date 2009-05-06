from nose import with_setup
from openalea.container import Tree
from openalea.container.generator.tree import regular

g = None

def setup_func () :
    global g
    g = regular(Tree(), 0, nb_vertices=19)

def teardown_func () :
    g.clear()

# ##########################################################
#
# Vertex List Graph Concept
#
# ##########################################################
@with_setup(setup_func,teardown_func)
def test_vertices () :
    assert list(g.vertices())==range(20)
    assert list(g) == list(g.vertices())

@with_setup(setup_func,teardown_func)
def test_nb_vertices () :
    assert g.nb_vertices()==20
    assert len(g) == 20

@with_setup(setup_func,teardown_func)
def test_has_vertex () :
    for vid in range(0,20):
        assert g.has_vertex(vid)

@with_setup(setup_func,teardown_func)
def test_contain () :
    for vid in range(0,20):
        assert vid in g, vid

@with_setup(setup_func,teardown_func)
def test_iteredges () :
    assert len(list(g.iteredges())) == 20, 'edges = %s'%(' '.join(g.iteredges()))


# ##########################################################
#
# Mutable Vertex Graph concept
#
# ##########################################################

@with_setup(setup_func,teardown_func)
def test_clear () :
    g.clear()
    assert g.nb_vertices()==1

@with_setup(setup_func,teardown_func)
def test_remove_vertex () :
    leaves = [vid for vid in g if g.is_leaf(vid)]
    for leaf in leaves:
        g.remove_vertex(leaf)

    assert len(g) == 20 - len(leaves)
            

# ##########################################################
#
# Tree concept
#
# ##########################################################

@with_setup(setup_func,teardown_func)
def test_parent_et_al () :
    for vid in g:
        if vid == g.root:
            continue
        else:
            assert g.parent(vid) is not None, vid
            assert vid in list(g.children(g.parent(vid)))

            assert g.nb_children(vid) <= 3
            assert vid not in list(g.siblings(vid))
            assert g.nb_siblings(vid) <=2
            assert g.nb_siblings(vid) == g.nb_children(g.parent(vid))-1


# ##########################################################
#
# Extend Graph concept
#
# ##########################################################

