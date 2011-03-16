#
#       OpenAlea.SecondNature
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "CeCILL v2"
__revision__ = " $Id$ "


from openalea.secondnature.base_mixins import HasName

class Layout(HasName):
    def __init__(self, name, skeleton, appletmap, easy_name=None):
        HasName.__init__(self, name)
        self.__skeleton  = skeleton
        self.__appletmap = appletmap
        self.__ezname    = easy_name

    skeleton  = property(lambda x: x.__skeleton)
    appletmap = property(lambda x: x.__appletmap)
    easyname  = property(lambda x: x.__ezname or x.name)



class LayoutSpace(object):
    """returned by widget factories"""
    def __init__(self, content, menuList=None, toolbar=None):
        self.__content = content
        self.__menuList    = menuList
        self.__toolbar = toolbar

    content = property(lambda x:x.__content)
    menus   = property(lambda x:x.__menuList)
    toolbar = property(lambda x:x.__toolbar)
