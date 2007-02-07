from topomesh import TopoMesh

m=TopoMesh()
for i in xrange(9) : m.add_point()
for i in xrange(4) : m.add_cell()
for cid,l in enumerate([[0,1,3,4],[1,2,4,5],[3,4,6,7],[4,5,7,8]]) :
	for pid in l : m.add_link(cid,pid)
print "points",list(m.points())
print "cells",list(m.cells())
print "points around 0",list(m.points(0))
print "cells around 0",list(m.cells(0))
print "cells around 4",list(m.cells(4))
print "neighbors of cell 0",list(m.cell_neighbors(0))
print "neighbors of point 0",list(m.point_neighbors(0))
print "neighbors of point 4",list(m.point_neighbors(4))

