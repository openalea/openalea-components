from openalea.container import Topomesh


def test_topomesh():
    t = Topomesh(3)

    def dstr (did) :
    	return "%d (%d)" % (did, t.degree(did) )

    dids = [t.add_wisp(d) for d in range(4)]

    print [dstr(did) for did in t.wisps()]
    print [dstr(did) for did in t.wisps(1)]

    for i in range(3) :
    	t.link(dids[i], dids[i + 1])

    did = dids[1]
    print "regions", did, [dstr(rid) for rid in t.regions(did)]
    print "borders", did, [dstr(bid) for bid in t.borders(did)]


    did = dids[2]
    print "regions2", did, [dstr(rid) for rid in t.regions(did, 2)]
    print "borders2", did, [dstr(bid) for bid in t.borders(did, 2)]


    t.remove_wisp(did)
    print [dstr(did) for did in t.wisps()]

    did = dids[1]
    print "regions", did, [dstr(rid) for rid in t.regions(did)]
    print "borders", did, [dstr(bid) for bid in t.borders(did)]
















