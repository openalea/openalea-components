# -*- coding: utf-8 -*-
# -*- python -*-
#
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Guillaume Baty <guillaume.baty@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

import numpy as np

from openalea.vpltk.qt import QtGui, QtCore

from openalea.image.spatial_image import SpatialImage

from openalea.image.gui.slide_viewer import PixmapStackView, ScalableLabel
from openalea.image.gui.pixmap import to_img


def to_image(data, axis=2):
    # Manage also colored images.
    if len(data.shape) == 4 and data.shape[-1] in (3, 4):
        if data.dtype != np.uint8:
            raise Exception("Only uint8 RGB[A] images supported, got %s instead" % str(data.dtype))
        pal = None
    for z in xrange(data.shape[axis]):
        if axis == 0:
            dat = data[z, :,:] 
        elif axis == 1:
            dat = data[:, z, :] 
        else:
            dat = data[:, :, z]

        if pal is not None:
            dat = pal[dat]
            if isinstance(data, SpatialImage):
                dat = SpatialImage(dat)
        #img = QImage(dat,
        #             data.shape[0],
        #             data.shape[1],
        #             QImage.Format_ARGB32)
        return to_img(dat)


class ImageViewerWidget(ScalableLabel):

    """
    Simple SpatialImage viewer
    """
    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        ScalableLabel.__init__(self, parent)
        self._img = None

    def setValue(self, img):
        self._img = img
        pix = QtGui.QPixmap.fromImage(to_image(img))
        self.setPixmap(pix)
        self.valueChanged.emit(img)

    def value(self):
        return self._img


class SliderViewerWidget(QtGui.QWidget):

    """
    Widget based on openalea.image.gui.slide_viewer.PixmapStackView

    ..todo::

        Reimplement colormaps, stacks, sliders, ...
    """
    valueChanged = QtCore.Signal(object)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self._im_view = PixmapStackView()
        self._label = ScalableLabel()

        self._layout = QtGui.QVBoxLayout(self)
        self._layout.addWidget(self._label)

    def setValue(self, img):
        if img is self.value():
            return
        self._im_view.set_image(img)
        self._im_view._reconstruct_pixmaps()
        pix = self._im_view.pixmap()
        if pix is not None:
            self._label.setPixmap(pix)
            self.valueChanged.emit(pix)

    def value(self):
        return self._im_view.image()


if __name__ == '__main__':
    from openalea.deploy.shared_data import shared_data
    from openalea.image.serial.basics import imread
    import openalea.oalab
    img_path = shared_data(openalea.oalab, 'icons/Crystal_Clear_app_clock.png')
    img = imread(img_path)

    instance = QtGui.QApplication.instance()
    if instance is None:
        app = QtGui.QApplication([])
    else:
        app = instance

    slider = SliderViewerWidget()
    slider.setValue(img)
    slider.show()

    viewer = ImageViewerWidget()
    viewer.setValue(img)
    viewer.show()

    if instance is None:
        app.exec_()
