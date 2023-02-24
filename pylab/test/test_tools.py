from openalea.oapylab import tools

def test_metainfo():
    from openalea.oapylab import version, authors
    


def test_build_dict():
    d = tools.build_dict(['a'])
    assert d['a'] == 'a'
    assert 'None' not in list(d.keys())

    d = tools.build_dict(['a'], add_none=True)
    assert d['None'] == None
   

#def test_all():
#    from openalea.pylab.tools import * 
