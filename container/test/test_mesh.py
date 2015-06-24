from numpy import array
from openalea.container.mesh import Mesh

m = Mesh()

pids = []
for x, y in [(-1, -1), (1, -1), (1, 1), (-1, 1)] :
    did = m.add_dart(0)
    m.set_position(did, array([x, y]) )
    pids.append(did)

eids = []
nb = len(pids)
for i in range(nb) :
    eid = m.add_dart(1)
    m.link(eid, pids[i])
    m.link(eid, pids[(i + 1) % nb])
    eids.append(eid)

fid = m.add_dart(2)
for eid in eids :
    m.link(fid,eid)

for did in m.darts() :
    print did, m.degree(did), m.position(did)


print "local view"
mv = m.local_view(eids[0])
for did in mv.darts() :
    print did, mv.degree(did), mv.position(did)


