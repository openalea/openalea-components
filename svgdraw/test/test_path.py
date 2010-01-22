from openalea.svgdraw import open_svg

f = open_svg("test_path.svg",'r')
sc = f.read()
f.close()

pth = sc.get_by_id("path0000")

print pth
pts = tuple(pth.polyline_ctrl_points() )

for pt in pts :
	print pt,pth.scene_pos(pt)
