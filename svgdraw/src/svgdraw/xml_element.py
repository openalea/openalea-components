from xml.dom.minidom import Document

ELEMENT_TYPE = Document.ELEMENT_NODE #default type used in nodes
SVG_ELEMENT_TYPE = Document.ELEMENT_NODE #default type used in svg nodes
TEXT_TYPE = Document.TEXT_NODE


class XMLElement (object) :
	"""
	base class for all xml elements
	basic with no interpretation
	just a way to manage all attributes of an element
	"""
	def __init__ (self, parent=None, nodetype=None, nodename=None) :
		self._nodetype=nodetype
		self._nodename=nodename
		self._attributes={}
		#xml tree structure
		self._parent=parent
		self._children=[]
	
	def nodetype (self) :
		return self._nodetype
	
	def set_nodetype (self, nodetype) :
		self._nodetype=nodetype
	
	def nodename (self) :
		return self._nodename
	
	def set_nodename (self, name) :
		self._nodename=name
	#####################################################
	#
	#		tree structure
	#
	#####################################################
	def parent (self) :
		return self._parent
	
	def set_parent (self, parent) :
		self._parent=parent
	
	def nb_children (self) :
		return len(self._children)
	
	def children (self) :
		return iter(self._children)
	
	def child (self, ind) :
		return self._children[ind]
	
	def add_child (self, elm) :
		self._children.append(elm)
		elm.set_parent(self)
	
	def set_child (self, ind, elm) :
		self._children[ind]=elm
		elm.set_parent(self)
	
	def remove_child (self, child) :
		self._children.remove(child)
		child.set_parent(None)
	
	def clear_children (self) :
		for elm in self.children() :
			elm.set_parent(None)
		self._children=[]
	#####################################################
	#
	#		attributes
	#
	#####################################################
	def has_attribute (self, key) :
		return key in self._attributes
	
	def attributes (self) :
		return iter(self._attributes)
	
	def attribute (self, key) :
		return self._attributes[key]
	
	def get_default (self, key, default_value) :
		try :
			return self._attributes[key]
		except KeyError :
			return default_value
	
	def set_attribute (self, key, val) :
		self._attributes[key]=val
	
	def remove_attribute (self, key) :
		del self._attributes[key]
	#####################################################
	#
	#		XML in out
	#
	#####################################################
	def from_node (self, xmlelm) :
		self.set_nodetype(xmlelm.nodetype())
		self.set_nodename(xmlelm.nodename())
		for key in xmlelm.attributes() :
			self.set_attribute(key,xmlelm.attribute(key))
		for elm in xmlelm.children() :
			self.add_child(elm)
	
	def load (self) :
		"""
		load attributes from xml attributes style
		"""
		pass
	
	def save (self) :
		"""
		save attributes in an xml style
		"""
		pass
	
	def load_xml (self, xmlnode) :
		self.set_nodetype(xmlnode.nodeType)
		self.set_nodename(xmlnode.nodeName)
		if xmlnode.attributes is not None :
			for k,v in xmlnode.attributes.items() :
				self.set_attribute(str(k),str(v))
		try :
			self.set_attribute("data",str(xmlnode.data))
		except AttributeError :
			pass
		for node in xmlnode.childNodes :
			if node.nodeType==Document.TEXT_NODE and node.data.isspace() :#pretty print node are useless
				pass
			else :
				elm=XMLElement()
				elm.load_xml(node)
				self.add_child(elm)
	
	def save_xml (self, xmlparent=None) :
		typ=self.nodetype()
		if xmlparent is None :
			assert typ==Document.DOCUMENT_NODE
			xmlnode=Document()
			xmlnode.ownerDocument=xmlnode
		else :
			if typ == Document.ATTRIBUTE_NODE :
				xmlnode=xmlparent.ownerDocument.createAttribute(self.name())
			elif typ == Document.CDATA_SECTION_NODE :
				xmlnode=xmlparent.ownerDocument.createCDATASection()
			elif typ == Document.COMMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createComment(self.attribute("data"))
			elif typ == Document.DOCUMENT_FRAGMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createDocumentFragment()
			elif typ == Document.DOCUMENT_NODE :
				raise UserWarning("cannot create a DOCUMENT_NODE from there")
			elif typ == Document.DOCUMENT_TYPE_NODE :
				raise UserWarning("cannot create a DOCUMENT_TYPE_NODE from there")
			elif typ == Document.ELEMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createElement(self.nodename())
				for key in self.attributes() :
					xmlnode.setAttribute(key,self.attribute(key))
			elif typ == Document.ENTITY_NODE :
				raise UserWarning("cannot create a ENTITY_NODE from there")
			elif typ == Document.ENTITY_REFERENCE_NODE :
				raise UserWarning("cannot create a ENTITY_REFERENCE_NODE from there")
			elif typ == Document.NOTATION_NODE :
				raise UserWarning("cannot create a NOTATION_NODE from there")
			elif typ == Document.PROCESSING_INSTRUCTION_NODE :
				xmlnode=xmlparent.ownerDocument.createProcessingInstruction()
			elif typ == Document.TEXT_NODE :
				xmlnode=xmlparent.ownerDocument.createTextNode(self.attribute("data"))
			else :
				raise UserWarning("problem")
			#xml tree save
			xmlparent.appendChild(xmlnode)
		for child in self.children() :
			child.save_xml(xmlnode)
		return xmlnode


