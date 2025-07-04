
# This file has been generated at Sat Mar  6 21:17:54 2010

from openalea.core import Factory
from importlib import metadata

version = metadata.metadata('openalea.pylab')['version']
authors = metadata.metadata('openalea.pylab')['Author']


__name__ = 'openalea.pylab.datasets'

__editable__ = False
__description__ = 'datasets to play with.'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr/doc/openalea/pylab/doc/_build/html/contents.html'
__alias__ = []
__version__ = version
__authors__ = authors
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'icon.png'


__all__ = [
'py_pylab_PyLabBivariateNormal',
'py_pylab_PyLabSinWave',
]



py_pylab_PyLabBivariateNormal = Factory(name='PyLabBivariateNormal',
                description='pylab.fontproperties interface.',
                category='visualization, data processing',
                nodemodule='openalea.pylab_datasets_wralea.py_pylab',
                nodeclass='PyLabBivariateNormal',
                inputs=None, outputs=None, widgetmodule=None, widgetclass=None, lazy=True
                )

py_pylab_PyLabSinWave = Factory(name='PyLabSinWave',
                description='A*sin(2 pi w t)',
                category='visualization, data processing',
                nodemodule='openalea.pylab_datasets_wralea.py_pylab',
                nodeclass='PyLabSinWave',
                inputs=None, outputs=None, widgetmodule=None, widgetclass=None, lazy=True
                )
