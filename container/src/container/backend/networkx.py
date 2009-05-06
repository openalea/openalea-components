# -*- coding: utf-8 -*-
# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2008-2009 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.pradal.at.cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

'''
This module provides an implementation of the graph interface using networkx backend.
Backend implementation provide a way to reuse existing algorithms implemented
in different graph libraries, and to compare algorithms and graph implementation.
'''

__docformat__ = "restructuredtext"
__license__ = "Cecill-C"
__revision__ = " $Id: $ "

import networkx as nx

def to_networkx(g):
    """ Return a NetworkX Graph from a graph.

    :Parameters: 
        - `g`: a graph implementing :class:`openalea.container.interface.IEdgeListGraph` interface.

    :Returns: 
        - A NetworkX graph.

    """
    graph = nx.DiGraph()
    graph.add_node_from(g.vertices())
    graph.add_edge_from(( (g.source(eid), g.target(eid)) for eid in g.edges()))
    return graph


