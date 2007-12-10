from openalea.container import Relation

r=Relation()
for i in xrange(3) :
	print "link",r.add_link(0,i,i)
for i in xrange(3) :
	print "link",r.add_link(0,i)

print "source",r.source(0)
print "target",r.target(0)
print "remove",r.remove_link(0)
print "state",r.state()
for i in xrange(3) :
	print "link",r.add_link(0,i)
print "clear",r.clear()
print "test",list(r.links())

