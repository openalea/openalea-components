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


class ImageInterfacePlugin(object):

    def __call__(self):
        from openalea.image_wralea.image_interface import IImage
        return [IImage]


from openalea.oalab.mimedata import QMimeCodecPlugin


class IImageCodecPlugin(QMimeCodecPlugin):
    qtdecode = [
        ('openalealab/data', 'openalea/interface.IImage'),
        ('text/uri-list', 'openalea/interface.IImage'),
    ]

    def __call__(self):
        from openalea.image.mimedata import IImageCodec
        return IImageCodec


class ImageMimeDataCodecPlugin(object):
    category = 'openalea.codec.mimetype'
    plugins = [IImageCodecPlugin]
