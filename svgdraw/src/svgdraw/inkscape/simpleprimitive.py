import inkex,simpletransform,simplepath,simplestyle

def element_center (node) :
	if node.tag == inkex.addNS('path','svg') :#assume circle
		x=float(node.get(inkex.addNS("cx","sodipodi")))
		y=float(node.get(inkex.addNS("cy","sodipodi")))
	elif node.tag == inkex.addNS('rect','svg') :
		x=float(node.get("x"))+float(node.get("width"))/2.
		y=float(node.get("y"))+float(node.get("height"))/2.
	else :
		raise UserWarning("unrecognized node")
	pt=[x,y]
	if node.get("transform") is not None :
		mat=simpletransform.parseTransform(node.get("transform"))
		simpletransform.applyTransformToPoint(mat,pt)
	return pt

def box (parent, x=0, y=0, width=10, height=10, style_dict={}) :
	new = inkex.etree.SubElement(parent,inkex.addNS('rect','svg'))
	#new.set("id",self.uniqueId("rect"))
	new.set("x",str(x))
	new.set("y",str(y))
	new.set("width",str(width))
	new.set("height",str(height))
	new.set("style",simplestyle.formatStyle(style_dict))
	return new

def connectors (parent) :
	for node in parent.iterchildren() :
		if node.get(inkex.addNS('connector-type','inkscape')) is not None :
			yield node

def already_connected (parent, start_node, end_node) :
	start_id=start_node.get("id")
	end_id=end_node.get("id")
	for node in parent.iterchildren() :
		if node.tag == inkex.addNS('path','svg') :#maybe a connector
			if node.get(inkex.addNS('connector-type','inkscape')) is not None : #a connector
				sid=node.get(inkex.addNS('connection-start','inkscape'))[1:]
				eid=node.get(inkex.addNS('connection-end','inkscape'))[1:]
				if (sid==start_id and eid==end_id) or (eid==start_id and sid==end_id) :
					return True
	return False

def connect (parent, start_node, end_node, style_dict, overwrite=False) :
	if overwrite or not already_connected(parent,start_node,end_node) :
		con = inkex.etree.SubElement(parent,inkex.addNS('path','svg'))
		#con.set("id",self.uniqueId("con"))
		con.set(inkex.addNS('connection-start','inkscape'),"#%s" % start_node.get("id"))
		con.set(inkex.addNS('connection-end','inkscape'),"#%s" % end_node.get("id"))
		con.set(inkex.addNS('connector-type','inkscape'),"polyline")
		path=[['M',element_center(start_node)],['L',element_center(end_node)]]
		con.set("d",simplepath.formatPath(path))
		style={"stroke":simplestyle.svgcolors["magenta"]}
		con.set("style",simplestyle.formatStyle(style_dict))
		return con

