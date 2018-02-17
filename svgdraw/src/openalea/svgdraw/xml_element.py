# -*- python -*-
#
#       svgdraw: svg library
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

"""
This module defines an abstract xml element
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

from xml.dom.minidom import Document

ELEMENT_TYPE = Document.ELEMENT_NODE #default type used in nodes
SVG_ELEMENT_TYPE = Document.ELEMENT_NODE #default type used in svg nodes
TEXT_TYPE = Document.TEXT_NODE


class XMLElement (object) :
	"""Base class for all xml elements
	
	basic with no interpretation
	just a way to manage all attributes of an element
	"""
	def __init__ (self, parent=None, nodetype=None, nodename=None, nodeid = None) :
		"""Constructor
		
		:Parameters:
		 - `parent` (:class:`XMLElement`) - owner of
		    this node. Default None means that this
		    element is top level.
		 - `nodetype` (TYPE) - type of this particular
		    type of node
		 - `nodename` (str) - name of this particular
		    type of node
		 - `nodeid` (str) - a unique id for this node
		"""
		self._nodetype = nodetype
		self._nodename = nodename
		self._attributes = {}
		if nodeid is not None :
			self.set_id(nodeid)
		#xml tree structure
		self._parent = parent
		self._children = []
	
	def nodetype (self) :
		"""Retrieve type of this node
		
		:Returns Type: TYPE
		"""
		return self._nodetype
	
	def set_nodetype (self, nodetype) :
		"""Set type of this node
		
		:Parameters:
		 - `nodetype` (TYPE)
		"""
		self._nodetype = nodetype
	
	def nodename (self) :
		"""Retrieve name of this node
		
		:Returns Type: str
		"""
		return self._nodename
	
	def set_nodename (self, name) :
		"""Set name of this node
		
		:Parameters:
		 - `name` (str)
		"""
		self._nodename = name
	
	def id (self) :
		"""Retrieve id of this node
		
		:Returns Type: str
		"""
		return self._attributes["id"]
	
	def set_id (self, nodeid) :
		"""Set id of this node
		
		:Parameters:
		 - `nodeid` (str)
		"""
		self._attributes["id"] = nodeid
	
	#####################################################
	#
	#		tree structure
	#
	#####################################################
	def parent (self) :
		"""Retrieve the parent of this node
		
		:Returns Type: :class:`XMLElement`
		"""
		return self._parent
	
	def set_parent (self, parent) :
		"""Set the parent of this node
		
		:Parameters:
		 - `parent` (:class:`XMLElement`)
		"""
		self._parent = parent
	
	def nb_children (self) :
		"""Number of nodes that have
		this node as parent.
		
		:Returns Type: int
		"""
		return len(self._children)
	
	def children (self) :
		"""Iterate on all children of this node
		
		:Returns Type: iter of :class:`XMLElement`
		"""
		return iter(self._children)
	
	def child (self, ind) :
		"""Direct access to a given child
		
		:Parameters:
		 - `ind` (int) - index of child
		
		:Returns Type: :class:`XMLElement`
		"""
		return self._children[ind]
	
	def add_child (self, elm) :
		"""Add a new child to this node
		
		:Parameters:
		 - `elm` (XMLElement)
		"""
		self._children.append(elm)
		elm.set_parent(self)
	
	def set_child (self, ind, elm) :
		"""Replace a child of this node
		by another one.
		
		:Parameters:
		 - `ind` (int) - index of child
		    to replace
		 - `elm` (XMLElement)
		"""
		self._children[ind] = elm
		elm.set_parent(self)
	
	def remove_child (self, child) :
		"""Remove a child from this node
		
		:Parameters:
		 - `child` (XMLElement)
		"""
		self._children.remove(child)
		child.set_parent(None)
	
	def clear_children (self) :
		"""Remove all children from
		this node.
		"""
		for elm in self.children() :
			elm.set_parent(None)
		self._children = []
	
	#####################################################
	#
	#		attributes
	#
	#####################################################
	def has_attribute (self, key) :
		"""Test wether this attribute is
		defined.
		
		:Parameters:
		 - `key` (str)
		
		:Returns Type: bool
		"""
		return key in self._attributes
	
	def attributes (self) :
		"""Iterate on all attribute keys
		
		:Returns Type: iter of str
		"""
		return iter(self._attributes)
	
	def attribute (self, key) :
		"""Retriev value of an attribute
		
		:Parameters:
		 - `key` (str)
		
		:Returns Type: str
		"""
		return self._attributes[key]
	
	def get_default (self, key, default_value) :
		"""Retrieve value of an attribute
		
		If the attribute do not exist,
		return the provided default_value
		
		:Parameters:
		 - `key` (str)
		 - `default_value` (str) - default
		    value to return when key do not
		    exist.
		
		:Returns Type: str
		"""
		try :
			return self._attributes[key]
		except KeyError :
			return default_value
	
	def set_attribute (self, key, val) :
		"""Set the value of an attribute
		
		If the attribute do not exist,
		create it's entry.
		
		:Parameters:
		 - `key` (str)
		 - `val` (str) - new value of the
		   attribute
		"""
		self._attributes[key] = val
	
	def remove_attribute (self, key) :
		"""Remove an attribute
		
		:Parameters:
		 - `key` (str)
		"""
		del self._attributes[key]
	
	#####################################################
	#
	#		XML in out
	#
	#####################################################
	def from_node (self, xmlelm) :
		"""Clone elm attributes
		
		:Parameters:
		 - `xmlelm` (:class:`XMLElement`) -
		    master to clone
		"""
		self.set_nodetype(xmlelm.nodetype() )
		self.set_nodename(xmlelm.nodename() )
		for key in xmlelm.attributes() :
			self.set_attribute(key,xmlelm.attribute(key) )
		for elm in xmlelm.children() :
			self.add_child(elm)
	
	def load (self) :
		"""Load attributes from xml format
		"""
		pass
	
	def save (self) :
		"""Save attributes in an xml format
		"""
		pass
	
	def load_xml (self, xmlnode) :
		self.set_nodetype(xmlnode.nodeType)
		self.set_nodename(xmlnode.nodeName)
		if xmlnode.attributes is not None :
			for k,v in xmlnode.attributes.items() :
				self.set_attribute(str(k),str(v) )
		try :
			self.set_attribute("data",str(xmlnode.data) )
		except AttributeError :
			pass
		for node in xmlnode.childNodes :
			if node.nodeType == Document.TEXT_NODE \
			   and node.data.isspace() :#pretty print node are useless
				pass
			else :
				elm = XMLElement()
				elm.load_xml(node)
				self.add_child(elm)
	
	def save_xml (self, xmlparent=None) :
		typ=self.nodetype()
		if xmlparent is None :
			assert typ == Document.DOCUMENT_NODE
			xmlnode = Document()
			xmlnode.ownerDocument = xmlnode
		else :
			if typ == Document.ATTRIBUTE_NODE :
				xmlnode=xmlparent.ownerDocument.createAttribute(self.name() )
			elif typ == Document.CDATA_SECTION_NODE :
				xmlnode=xmlparent.ownerDocument.createCDATASection()
			elif typ == Document.COMMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createComment(self.attribute("data") )
			elif typ == Document.DOCUMENT_FRAGMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createDocumentFragment()
			elif typ == Document.DOCUMENT_NODE :
				raise UserWarning("cannot create a DOCUMENT_NODE from there")
			elif typ == Document.DOCUMENT_TYPE_NODE :
				raise UserWarning("cannot create a DOCUMENT_TYPE_NODE from there")
			elif typ == Document.ELEMENT_NODE :
				xmlnode=xmlparent.ownerDocument.createElement(self.nodename() )
				for key in self.attributes() :
					xmlnode.setAttribute(key,self.attribute(key) )
			elif typ == Document.ENTITY_NODE :
				raise UserWarning("cannot create a ENTITY_NODE from there")
			elif typ == Document.ENTITY_REFERENCE_NODE :
				raise UserWarning("cannot create a ENTITY_REFERENCE_NODE from there")
			elif typ == Document.NOTATION_NODE :
				raise UserWarning("cannot create a NOTATION_NODE from there")
			elif typ == Document.PROCESSING_INSTRUCTION_NODE :
				xmlnode=xmlparent.ownerDocument.createProcessingInstruction()
			elif typ == Document.TEXT_NODE :
				xmlnode=xmlparent.ownerDocument.createTextNode(self.attribute("data") )
			else :
				raise UserWarning("problem")
			#xml tree save
			xmlparent.appendChild(xmlnode)
		for child in self.children() :
			child.save_xml(xmlnode)
		return xmlnode


