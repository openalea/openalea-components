from openalea.container import Grid

g=Grid()
print "dim",g.dim()
print "shape",g.shape()
print "size",g.size(),len(g)
for i in g :
	print "iter",i,"coord",g.coordinates(i),"index",g.index(g.coordinates(i))
