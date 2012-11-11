from openalea.container import regular_grid, mesh_to_txt, mesh_from_txt

############################################################
#
print "to_txt"
#
############################################################
m1 = regular_grid( (2,3) )

txt = mesh_to_txt(m1)
print txt

############################################################
#
print "from_txt"
#
############################################################
m2 = regular_grid( (1,3) )

mesh_from_txt(m2, txt)

for deg in range(3) :
	assert set(m1.darts(deg) ) == set(m2.darts(deg) )
	for did in m1.darts(deg) :
		assert set(m1.borders(did) ) == set(m2.borders(did) )

print mesh_to_txt(m2)

