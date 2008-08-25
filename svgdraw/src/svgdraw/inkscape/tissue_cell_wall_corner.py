#!/usr/bin/env python

from math import atan2,pi
import inkex,simplestyle,simpleprimitive

def angle (vec1, vec2, cent) :
	x1,y1=vec1
	x2,y2=vec2
	cx,cy=cent
	x1-=cx
	y1-=cy
	x2-=cx
	y2-=cy
	a=atan2(x1*y2-y1*x2,x1*x2+y1*y2)
	if a<0 :
		a+=2*pi
	return a

def bary (pts) :
	cx=sum([pt[0] for pt in pts])/len(pts)
	cy=sum([pt[1] for pt in pts])/len(pts)
	return (cx,cy)

class CellWallCornerEffect(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
	
	def uniqueId(self, id_prefix, make_new_id = True):
		ind=0
		new_id = "%s%.4d" % (id_prefix,ind)
		if make_new_id:
			while new_id in self.doc_ids:
				ind+=1
				new_id = "%s%.4d" % (id_prefix,ind)
			self.doc_ids[new_id] = 1
		return new_id
	
	def test_connection (self, node1, node2) :
		parent=node1.getparent()
		nid=node1.get("id")
		walls=[]
		for node in simpleprimitive.connectors(parent) :
			sid=node.get(inkex.addNS('connection-start','inkscape'))[1:]
			eid=node.get(inkex.addNS('connection-end','inkscape'))[1:]
			if nid==eid :
				walls.append(sid)
		nid=node2.get("id")
		for wid in walls :
			for node in simpleprimitive.connectors(parent) :
				sid=node.get(inkex.addNS('connection-start','inkscape'))[1:]
				eid=node.get(inkex.addNS('connection-end','inkscape'))[1:]
				if sid==wid and eid==nid :
					for child in parent.getchildren() :
						if child.get("id")==wid :
							return child
	
	def effect(self):
		node_pos={}
		node_R=[]
		for node in self.selected.values() :
			if node.tag == inkex.addNS('path','svg') and node.get(inkex.addNS("cx","sodipodi")) is not None :#assume circle
				node_pos[node]=simpleprimitive.element_center(node)
				rx,ry=simpleprimitive.element_size(node)
				node_R.append((rx+ry)/2.)
		if len(node_pos)>2 :
			size=sum(node_R)/len(node_R)
			cx,cy=bary(node_pos.values())
			node_ref=iter(node_pos).next()
			parent=node_ref.getparent()
			box=simpleprimitive.box(parent,cx,cy,size,size,{"fill":simplestyle.svgcolors["blue"]})
			box.set("id",self.uniqueId("rect"))
			angles=[(angle(node_pos[node_ref],pt,(cx,cy)),node) for node,pt in node_pos.iteritems()]
			angles.sort()
			nb=len(angles)
			for i in xrange(nb) :
				n1=angles[i][1]
				n2=angles[(i+1)%nb][1]
				wall=self.test_connection(n1,n2)
				if wall is None :
					x,y=bary([node_pos[node] for node in (n1,n2)])
					wall=simpleprimitive.box(parent,x,y,size,size,{"fill":simplestyle.svgcolors["magenta"]})
					wall.set("id",self.uniqueId("rect"))
					for node in (n1,n2) :
						con=simpleprimitive.connect(parent,wall,node,{"stroke":simplestyle.svgcolors["blue"]})
						if con is not None :
							con.set("id",self.uniqueId("con"))
				con=simpleprimitive.connect(parent,box,wall,{"stroke":simplestyle.svgcolors["green"]})
				con.set("id",self.uniqueId("con"))
		else :
			raise UserWarning("must select at least 3 elements")

# Create effect instance and apply it.
if __name__=="__main__" :
	effect = CellWallCornerEffect()
	effect.affect()

