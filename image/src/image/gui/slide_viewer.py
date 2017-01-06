# -*- python -*-
#
#       spatial_image.visu : spatial nd images
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Eric Moscardi <eric.moscardi@gmail.com>
#       File Contributor(s):
#                       Manual Forero
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################
"""
This module provide a simple viewer to display 3D stacks
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

__all__ = ["display","SlideViewer"]

import numpy as np

from Qt import QtCore, QtWidgets

from openalea.image.spatial_image import SpatialImage

from palette import palette_names,palette_factory
from pixmap_view import PixmapStackView,ScalableLabel

from slide_viewer_ui import Ui_MainWindow


if 'bw' in palette_names:
    palette_names.remove('bw')
    palette_names.sort()


class SlideViewer (QtWidgets.QMainWindow) :
    """Display each image in a stack using a slider

    A pure QWidget (instead of QMainWindow) is also available, see openalea.image.gui.slide_viewer_widget.
    """

    viewer_count = 0

    def __init__ (self, parent=None) :
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.axis = 2

        #central label
        self._im_view = PixmapStackView()
        self._label = ScalableLabel()
        self.setCentralWidget(self._label)

        #mouse handling
        self._label.setMouseTracking(True)
        self._last_mouse_x = 0
        self._last_mouse_y = 0

        QtCore.QObject.connect(self._label,
                               QtCore.SIGNAL("mouse_press"),
                               self.mouse_pressed)

        QtCore.QObject.connect(self._label,
                               QtCore.SIGNAL("mouse_move"),
                               self.mouse_pressed)

        #toolbar
        QtCore.QObject.connect(self.ui.action_close,
                               QtCore.SIGNAL("triggered(bool)"),
                               self.close)

        QtCore.QObject.connect(self.ui.action_snapshot,
                               QtCore.SIGNAL("triggered(bool)"),
                               self.snapshot)

        QtCore.QObject.connect(self.ui.action_rotate_left,
                               QtCore.SIGNAL("triggered(bool)"),
                               self.rotate_left)

        QtCore.QObject.connect(self.ui.action_rotate_right,
                               QtCore.SIGNAL("triggered(bool)"),
                               self.rotate_right)

        #palette
        self._palette_select = QtWidgets.QComboBox()
        self.ui.toolbar.addWidget(self._palette_select)
        for palname in palette_names :
            self._palette_select.addItem(palname)

        QtCore.QObject.connect(self._palette_select,
                               QtCore.SIGNAL("currentIndexChanged(int)"),
                               self.palette_name_changed)
        #axis
        self._axis = QtWidgets.QComboBox(self)
        self.ui.toolbar.addWidget(self._axis)
        self._axis.addItem("Z-axis")
        self._axis.addItem("Y-axis")
        self._axis.addItem("X-axis")
        self.connect(self._axis, QtCore.SIGNAL('currentIndexChanged(int)'), self.change_axis )

        #slider
        self._bot_toolbar = QtWidgets.QToolBar("slider")

        self._img_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._img_slider.setEnabled(False)
        QtCore.QObject.connect(self._img_slider,
                               QtCore.SIGNAL("valueChanged(int)"),
                               self.slice_changed)

        self._bot_toolbar.addWidget(self._img_slider)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,self._bot_toolbar)

        #statusbar
        self._lab_coord = QtWidgets.QLabel("coords:")
        self._lab_xcoord = QtWidgets.QLabel("% 4d" % 0)
        self._lab_ycoord = QtWidgets.QLabel("% 4d" % 0)
        self._lab_zcoord = QtWidgets.QLabel("% 4d" % 0)
        self._lab_intens = QtWidgets.QLabel("intens: None")

        self.ui.statusbar.addPermanentWidget(self._lab_coord)
        self.ui.statusbar.addPermanentWidget(self._lab_xcoord)
        self.ui.statusbar.addPermanentWidget(self._lab_ycoord)
        self.ui.statusbar.addPermanentWidget(self._lab_zcoord)
        self.ui.statusbar.addPermanentWidget(self._lab_intens)

        self.set_title("<"+str(self.viewer_count)+">")
        SlideViewer.viewer_count += 1

    ##############################################
    #
    #        update GUI
    #
    ##############################################
    def update_pix (self) :
        pix = self._im_view.pixmap()
        if pix is not None :
            self._label.setPixmap(pix)

    def get_pixel_value_str(self, img, x, y, z):
        px = img[x,y,z]
        if isinstance(px, np.ndarray):
            return str(px)
        else:
            return "%3d"%px

    def fill_infos (self) :
        x,y = self._label.pixmap_coordinates(self._last_mouse_x,
                                             self._last_mouse_y)
        img = self._im_view.image()
        if img is not None :
            i,j,k = self._im_view.data_coordinates(x,y)
            self._lab_xcoord.setText("% 4d" % i)
            self._lab_ycoord.setText("% 4d" % j)
            self._lab_zcoord.setText("% 4d" % k)

            imax,jmax,kmax = img.shape[:3]
            if self.axis==0 : #axis x
                if 0 <= i < jmax and 0 <= j < kmax and 0 <= k < imax :
                    self._lab_intens.setText("intens: %s" % self.get_pixel_value_str(img,k,i,j))
                else :
                    self._lab_intens.setText("intens: None")
            elif self.axis==1 : #axis y
                if 0 <= i < imax and 0 <= j < kmax and 0 <= k < jmax :
                    self._lab_intens.setText("intens: %s" % self.get_pixel_value_str(img,i,k,j))
                else :
                    self._lab_intens.setText("intens: None")
            else : #axis z
                if 0 <= i < imax and 0 <= j < jmax and 0 <= k < kmax :
                    self._lab_intens.setText("intens: %s" % self.get_pixel_value_str(img,i,j,k))
                else :
                    self._lab_intens.setText("intens: None")

    ##############################################
    #
    #        accessors
    #
    ##############################################
    def set_image (self, img) :
        self._im_view.set_image(img)
        try :
            self.resolution = img.resolution[:]
        except AttributeError :
            pass
        self._img_slider.setRange(0,self._im_view.nb_slices() - 1)
        self._img_slider.setEnabled(True)
        self.slice_changed(self._img_slider.value() )

    def set_palette (self, palette, palette_name = None) :
        if palette_name is not None :
            ind = self._palette_select.findText(palette_name)
            self._palette_select.setCurrentIndex(ind)
            self._im_view.set_palette(palette,self.axis)
            self.update_pix()

    def set_title(self, title=None):
        if title is not None :
            self.setWindowTitle(title)

    def change_axis(self,ind):
        self.axis = 2-ind
        try :
            res = list(self.resolution)
            del res[self.axis]
            tr = self._im_view._transform
            if tr % 180 :
                self._label._resolution=res[1],res[0]
            else :
                self._label.set_resolution(*res)
        except AttributeError :
            pass
        self._im_view._reconstruct_pixmaps(self.axis)
        self._img_slider.setRange(0,self._im_view.nb_slices() - 1)
        self._img_slider.setEnabled(True)
        self.update_pix()
        #self.fill_infos()



    ##############################################
    #
    #        slots
    #
    ##############################################
    def palette_name_changed (self, palette_index) :
        palname = str(self._palette_select.currentText() )
        img = self._im_view.image()
        if img is not None :
            self.set_palette(palette_factory(str(palname),img.max()) )

    def slice_changed (self, ind) :
        self._im_view.set_current_slice(ind)
        self.update_pix()
        self.fill_infos()

    def snapshot (self) :
        """write the current image
        """
        pix = self._im_view.pixmap()
        if pix is not None :
            pix.save("slice%.4d.png" % self._img_slider.value() )

    def wheelEvent (self, event) :
        inc = event.delta() / 8 / 15
        self._img_slider.setValue(self._img_slider.value() + inc)

    def rotate_left (self) :
        res=self._label._resolution
        self._label._resolution=res[1],res[0]
        self._im_view.rotate(-1)
        self.update_pix()

    def rotate_right (self) :
        res=self._label._resolution
        self._label._resolution=res[1],res[0]
        self._im_view.rotate(1)
        self.update_pix()

    def mouse_pressed (self, event) :
        self._last_mouse_x = event.x()
        self._last_mouse_y = event.y()
        self.fill_infos()

def display (image, palette_name = "grayscale", title = None , color_index_max = None) :
    """
    """

    w = SlideViewer()

    if not isinstance(image,SpatialImage):
        image = SpatialImage(image)

    if image.ndim < 3 :
        image = image.reshape(image.shape + (1,))

    if color_index_max is None :
        cmax = image.max()
    else :
        cmax = color_index_max

    palette = palette_factory(palette_name,cmax)

    w.set_palette(palette,palette_name)
    w.set_image(image)

    w.set_title(title)

    w.show()
    return w
