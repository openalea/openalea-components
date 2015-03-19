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
This module defines functions to display and print an svg scene
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import QByteArray
from PyQt4.QtGui import QApplication, \
                        QColor,QPalette, \
                        QPixmap,QPainter, \
                        QDialog,QVBoxLayout
from PyQt4.QtSvg import QSvgWidget,QSvgRenderer
from svg_file import to_xml

def display (sc, title = "SVG scene") :
	"""Display a scene in a Qdialog
	
	:Parameters:
	 - `sc` (`SVGScene`)
	 - `title` (str) - window title
	"""
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	
	dial = QDialog()
	dial.setWindowTitle(title)
	dial.setPalette(QPalette(QColor(255,255,255) ) )
	lay = QVBoxLayout(dial)
	
	w = QSvgWidget(dial)
	data = QByteArray(str(to_xml(sc) ) )
	w.load(data)
	
	r = w.renderer()
	w.setMinimumSize(r.defaultSize() )
	lay.addWidget(w)
	
	dial.show()
	
	qapp.exec_()

def save_png (filename, sc, background = (255,255,255, 0) ) :
	"""Create a png image from a scene
	
	:Parameters:
	 - `filename` (str) - name to write the image
	 - `sc` (SVGScene)
	 - `background` (int, int, int, int) - background color
	                        as (R, G, B, alpha) 0-255 tuple
	"""
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	
	r = QSvgRenderer(None)
	data = QByteArray(str(to_xml(sc) ) )
	r.load(data)
	
	pix = QPixmap(r.defaultSize() )
	pix.fill(QColor(*background) )
	painter = QPainter(pix)
	r.render(painter)
	painter.end()
	pix.save(filename)




