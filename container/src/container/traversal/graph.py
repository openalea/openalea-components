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

"""
This module provides several implementation of traversal on a directed graph. 
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

def topological_sort(graph, vtx_id, visited = None):
    ''' 
    Topolofgical sort of a directed graph implementing the
    :class:`openalea.container.interface.graph.IGraph` interface.
    Return an iterator on the vertices.

    :Parameters:
        - `graph`: a directed graph 
        - vtx_id: a vertex_identifier 
    .. note :: This is a non recursive implementation.
    '''
    if visited is None:
        visited = {}

    yield vtx_id
    visited[vtx_id] = True
    for vid in g.out_neighbors(vtx_id):
        if vid in visited:
            continue
        for node in topological_sort(g, vid):
            yield node


