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

class CellCornerEffect(inkex.Effect):
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
	
	def effect(self):
		node_pos={}
		for node in self.selected.values() :
			if node.tag == inkex.addNS('path','svg') and node.get(inkex.addNS("cx","sodipodi")) is not None :#assume circle
				node_pos[node]=simpleprimitive.element_center(node)
		if len(node_pos)>2 :
			cx=sum([pt[0] for pt in node_pos.itervalues()])/len(node_pos)
			cy=sum([pt[1] for pt in node_pos.itervalues()])/len(node_pos)
			node_ref=iter(node_pos).next()
			parent=node_ref.getparent()
			box=simpleprimitive.box(parent,cx,cy,10,10,{"fill":simplestyle.svgcolors["blue"]})
			box.set("id",self.uniqueId("rect"))
			angles=[(angle(node_pos[node_ref],pt,(cx,cy)),node) for node,pt in node_pos.iteritems()]
			angles.sort()
			nb=len(angles)
			for i in xrange(nb) :
				con=simpleprimitive.connect(parent,angles[i][1],angles[(i+1)%nb][1],{"stroke":simplestyle.svgcolors["magenta"]})
				if con is not None :
					con.set("id",self.uniqueId("con"))
			for node in node_pos :
				con=simpleprimitive.connect(parent,box,node,{"stroke":simplestyle.svgcolors["green"]})
				con.set("id",self.uniqueId("con"))
		else :
			raise UserWarning("must select at least 3 elements")

# Create effect instance and apply it.
if __name__=="__main__" :
	effect = CellCornerEffect()
	effect.affect()

