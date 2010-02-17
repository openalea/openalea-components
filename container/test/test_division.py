from openalea.container import Topomesh,topo_divide_face

#############################################
#
#		divide face
#
#############################################

#	0----0----1----1----2
#	|                   |
#	5        fid        2
#	|                   |
#	5----4----4----3----3

m = Topomesh(2)

for i in xrange(6) :
	m.add_wisp(0,i)

for i in xrange(6) :
	m.add_wisp(1,i)
	m.link(1,i,i)
	m.link(1,i,(i + 1) % 6)

fid = m.add_wisp(2)
for i in xrange(6) :
	m.link(2,fid,i)

fid1,fid2,eid = topo_divide_face(m,fid,1,4)

#	0----0----1----1----2
#	|         |         |
#	5  fid1  eid  fid2  2
#	|         |         |
#	5----4----4----3----3

assert set(m.borders(1,eid) ) == set([1,4])
assert set(m.regions(1,eid) ) == set([fid1,fid2])
fid1, = m.regions(1,5)
fid2, = m.regions(1,2)
assert set(m.borders(2,fid1) ) == set([0,eid,4,5])
assert set(m.borders(2,fid2) ) == set([1,2,3,eid])

#############################################
#
#		divide cell
#
#############################################

#top
#	0----0----1----1----2
#	|                   |
#	5         0         2
#	|                   |
#	5----4----4----3----3

#bottom
#	6----6----7----7----8
#	|                   |
#	11        1         8
#	|                   |
#	11---10---10---9----9

#back
#	0----0----1----1----2
#	|                   |
#	13        2         12
#	|                   |
#	6----6----7----7----8

#front
#	5----4----4----3----3
#	|                   |
#	15        3         14
#	|                   |
#	11---10---10---9----9

#left
#	0----5----5
#	|         |
#	13   4    15
#	|         |
#	6----11---11

#right
#	2----2----3
#	|         |
#	12   5    14
#	|         |
#	8----8----9

m = Topomesh(3)

for i in xrange(12) :
	m.add_wisp(0,i)

for i in xrange(16) :
	m.add_wisp(1,i)

for i in xrange(6) :
	m.add_wisp(2,i)

cid = m.add_wisp(3)

for i in xrange(6) :
	m.link(1,i,i)
	m.link(1,i,(i + 1) % 6)

for i in xrange(6) :
	m.link(1,6 + i,6 + i)
	m.link(1,6 + i,6 + (i + 1) % 6)

for eid,pid1,pid2 in [(12,2,8),
                      (13,0,6),
                      (14,3,9),
                      (15,5,11)] :
	m.link(1,eid,pid1)
	m.link(1,eid,pid2)

for i in xrange(6) :
	m.link(2,0,i)
	m.link(2,1,6 + i)

for fid,eids in [(2,(0,1,12,7,6,13) ),
                 (3,(4,3,14,9,10,15) ),
                 (4,(5,15,11,13) ),
                 (5,(2,14,8,12) )] :
	for eid in eids :
		m.link(2,fid,eid)

for i in xrange(6) :
	m.link(3,cid,i)










