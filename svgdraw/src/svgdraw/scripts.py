#set of scripts to work with svg scenes

def to_svg_namespace (node) :
	"""
	add 'svg:' to all nodenames that represent svg elements
	"""
	if node.has_attribute("xmlns") :
		node.remove_attribute("xmlns")
	if node.nodename() in ("svg","g","path","rect","image","defs","metadata") :
		node.set_nodename("svg:%s" % node.nodename())
	for child in node.children() :
		to_svg_namespace(child)

def remove_attribute (node, attr_name, nodename=None) :
	if (nodename is None) or (node.nodename() == nodename) :
		if node.has_attribute(attr_name) :
			node.remove_attribute(attr_name)
	for child in node.children() :
		remove_attribute(child,attr_name,nodename)

