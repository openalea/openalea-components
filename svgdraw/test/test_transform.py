from math import radians
from openalea.svgdraw import transform as tr

print "scaling"
t = tr.scaling(1., 2.)
ti = t.inverse()
print t
print ti
print t * ti

print "translation"
t = tr.translation(1., 2.)
ti = t.inverse()
print t
print ti
print t * ti

print "rotation"
t = tr.rotation(radians(45) )
ti = t.inverse()
print t
print ti
print t * ti

print "composite"
t = tr.translation(1., 2.) * tr.rotation(radians(45) ) * tr.scaling(1., 2.)
ti = t.inverse()
print t
print ti
print t * ti





