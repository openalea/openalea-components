from openalea.svgdraw import *

f = open_svg("testref.svg", 'r')
sc = f.read()
f.close()

save_png("test.png", sc, (255, 255, 255, 0) )

