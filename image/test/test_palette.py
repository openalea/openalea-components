# -*- python -*-
#
#       image: image manipulation GUI
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Eric Moscardi <eric.moscardi@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""
Test frame manipulator
"""

__license__= "Cecill-C"
__revision__ = " $Id: __init__.py 2245 2010-02-08 17:11:34Z cokelaer $ "

from PyQt4.QtGui import QApplication,QLabel
from openalea.image import rainbow,grayscale
from openalea.image.gui import to_pix
from numpy import array

data = array(range(10000) ).reshape( (100,100) )
pal = rainbow(10000)

img = pal[data]

qapp = QApplication([])

pix = to_pix(img)

w = QLabel()
w.setPixmap(pix)

w.show()

qapp.exec_()


