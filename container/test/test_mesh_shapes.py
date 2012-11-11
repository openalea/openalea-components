from numpy import array
from openalea.container import line, polygon, regular_grid

def tovec (tup) :
	return array(tup, 'f')

############################################################
#
print "line"
#
############################################################
m = line(3)

for did in m :
	print did, m.degree(did), tuple(m.borders(did) ), m.position(did)


############################################################
#
print "polygon"
#
############################################################
m = polygon(4)
m.apply_geom_transfo(tovec)

for did in m :
	print did, m.degree(did), tuple(m.borders(did) ), m.position(did)


############################################################
#
print "grid 2d"
#
############################################################
m = regular_grid( (2,3) )
m.apply_geom_transfo(tovec)

for did in m :
	print did, m.degree(did), tuple(m.borders(did) ), m.position(did)


############################################################
#
print "grid 3d"
#
############################################################
m = regular_grid( (1,2,3) )
m.apply_geom_transfo(tovec)

for did in m :
	print did, m.degree(did), tuple(m.borders(did) ), m.position(did)

















