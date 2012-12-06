from openalea.svgdraw import *

f = open_svg("testref.svg", 'r')
sc = f.read()
f.close()

lay = sc.get_layer("background")
ref_elms = tuple(lay.elements() )

for elm in ref_elms :
	cent = elm.scene_pos(elm.center() )

	cx, cy = lay.local_pos(cent)
	sph = SVGSphere(cx, cy, 10, 10)
	sph.set_fill( (255, 0, 255) )
	lay.append(sph)

f = open_svg("result.svg", 'w')
f.write(sc)
f.close()

