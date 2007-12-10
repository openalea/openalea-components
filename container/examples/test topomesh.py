from openalea.container import Topomesh

t=Topomesh()

def c () :
	t.clear()
	cells=[t.add_cell() for i in xrange(2)]
	pts=[t.add_point() for i in xrange(7)]
	for i in xrange(4) :
		t.add_link(cells[0],pts[i])
	for i in (1,2,4,5) :
		t.add_link(cells[1],pts[i])
	return cells,pts

cells,pts=c()
cid=cells[0]
print "has_cell",t.has_cell(cid),t.has_cell(1000)
print "has_point",t.has_point(pts[0]),t.has_point(1000)

print "cell_links",t.nb_cell_links(cid),list(t.cell_links(cid))
print "point_links",t.nb_point_links(pts[0]),list(t.point_links(pts[0]))

lid=t.cell_links(cid).next()
print "cell",t.cell(lid)
print "point",t.point(lid)

print "cells",t.nb_cells(),list(t.cells())
print "cells(pid)",t.nb_cells(pts[0]),list(t.cells(pts[0]))
print "points",t.nb_points(),list(t.points())
print "points(cid)",t.nb_points(cid),list(t.points(cid))

print "add cell",t.add_cell()
print "add cell",t.add_cell(100)
print "add cell",t.add_cell(None)
print "remove cell",t.remove_cell(cid)
print "remove cell",list(t.cells()),list(t.cells(pts[0]))

cells,pts=c()
print "add point",t.add_point()
print "add point",t.add_point(10000)
print "add point",t.add_point(None)
print "remove point",t.remove_point(pts[1])
print "remove point",list(t.points()),list(t.points(cid))

cells,pts=c()
print "add link",t.add_link(cells[0],pts[4])
print "add link",t.add_link(cells[0],pts[5],1000)
print "add link",t.add_link(cells[0],pts[6],None)
print "add link",list(t.cell_links(cells[0]))
print "remove link",t.remove_link(0)
print "remove_link",list(t.cell_links(cells[0]))

print "clear links",t.clear_links()
print "clear_links",list(t.cell_links(cells[0])),list(t.cells())
