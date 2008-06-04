#!/usr/bin/env python

import inkex

class RemoveLinksEffect(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
	
	def effect(self):
		for node in self.selected.values() :
			parent=node.getparent()
			nid=node.get("id")
			for child in parent.getchildren() :
				if child.get(inkex.addNS('connector-type','inkscape')) is not None :#connector
					sid=child.get(inkex.addNS('connection-start','inkscape'))[1:]
					eid=child.get(inkex.addNS('connection-end','inkscape'))[1:]
					if nid in (sid,eid) :
						parent.remove(child)
			parent.remove(node)
			#raise UserWarning(dir())

# Create effect instance and apply it.
if __name__=="__main__" :
	effect = RemoveLinksEffect()
	effect.affect()

