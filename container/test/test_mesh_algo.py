from numpy import array
from openalea.container import (polygon, regular_grid
                              , center_mesh, triangulate)

############################################################
#
print "center_mesh"
#
############################################################
def tovec (tup) :
	return array(tup, 'f')

m = regular_grid( (3,3) )
m.apply_geom_transfo(tovec)

for did in m.darts(2) :
	print did, m.position(did)

print "center"

center_mesh(m)

for did in m.darts(2) :
	print did, m.position(did)

############################################################
#
print "triangulate"
#
############################################################
from pylab import *

colors = ["#ff0000", "#00ff00", "#0000ff"
        , "#ffff00", "#00ffff", "#ff00ff", "#aaaaaa"]

m = polygon(6)
m.apply_geom_transfo(tovec)

fid, = m.darts(2)

for eid in m.borders(fid) :
	pt1, pt2 = (m.position(pid) for pid in m.borders(eid) )
	plot([pt1[0],pt2[0] ], [pt1[1], pt2[1] ]
		, color = "#000000"
		, linewidth = 2)

triangulate(m, fid)

for i,fid in enumerate(m.darts(2) ) :
	col = colors[i]
	for eid in m.borders(fid) :
		pt1, pt2 = (m.position(pid) for pid in m.borders(eid) )
		plot([pt1[0],pt2[0] ], [pt1[1], pt2[1] ]
			, color = col
			, linewidth = 1)

show()

















