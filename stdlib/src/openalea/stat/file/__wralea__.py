# -*- python -*-
#
#       OpenAlea.StdLib
#
#       Copyright 2006 - 2008 INRIA - CIRAD - INRA  
#
#       File author(s): CHAUBERT Florence <florence.chaubert@cirad.fr>
#                       Da SILVA David <david.da_silva@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#


from openalea.core import Factory as Fa
from openalea.core import IFileStr, IFloat, IInt, ISequence

__name__ = "openalea.stat.file"
__alias__ = ["stat.file"]

__version__ = '0.0.1'
__license__ = 'CECILL-C'
__authors__ = 'OpenAlea consortium'
__institutes__ = 'INRIA/CIRAD/UM2'
__description__ = 'File manipulations.'
__url__ = 'http://rpy.sourceforge.net and http://www.scipy.org/'

__editable__ = 'False'

__all__ = ['loadfile', 'extractrow', 'extractcolumn', ]

loadfile = Fa(uid="ab84e4644e7811e6bff6d4bed973e64a",
              name="load file",
              description="Read .txt file ",
              category="file,IO",
              nodemodule="openalea.stat.file.file",
              nodeclass="Load",
              inputs=(dict(name="file", interface=IFileStr("txt (*.txt)"),
                           showwidget=True),
                      ),
              outputs=(dict(name="data", interface=ISequence),
                       ),
              )

extractrow = Fa(uid="ab84e4654e7811e6bff6d4bed973e64a",
                name="extract row",
                description="Extract the lth row ",
                category="file,codec",
                nodemodule="openalea.stat.file.file",
                nodeclass="ExtractLigne",
                inputs=(dict(name="data", interface=None),
                        dict(name="L", interface=IInt, showwidget=True),
                        dict(name="Test", interface=IFloat, value=-1.,
                             showwidget=True),
                        ),
                outputs=(dict(name="Row", interface=ISequence),
                         ),
                )

extractcolumn = Fa(uid="ab84e4664e7811e6bff6d4bed973e64a",
                   name="extract column",
                   description="Extract the cth column ",
                   category="file, codec",
                   nodemodule="openalea.stat.file.file",
                   nodeclass="ExtractCol",
                   inputs=(dict(name="data", interface=None),
                           dict(name="L", interface=IInt, showwidget=True),
                           dict(name="Test", interface=IFloat, value=-1.,
                                showwidget=True),
                           ),
                   outputs=(dict(name="Column", interface=ISequence),
                            ),
                   )
