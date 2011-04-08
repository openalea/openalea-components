
# This file has been generated at Tue Mar 22 10:54:50 2011

from openalea.core import *


__name__ = 'openalea.image.demo'

__editable__ = True
__description__ = 'Image manipulation'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.8.0'
__authors__ = 'OpenAlea Consortium'
__institutes__ = 'INRIA/CIRAD'
__icon__ = ''


__all__ = ['display', '_4854880720']



display = CompositeNodeFactory(name='display',
                             description='',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('openalea.image.serial', 'imread'), 3: ('openalea.image.gui', 'display')},
                             elt_connections={  4297110336: (2, 0, 3, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'imread',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x129ee1510> : "imread"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -349.0,
         'posy': -114.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'display',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x1215b1610> : "display"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -334.0,
         'posy': -49.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [(0, "'/Users/moscardi/Work/trunk/openalea/image/share/lena.bmp'")],
   3: [(1, "'grayscale'"), (2, 'None')],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-349.0, -114.0], 'userColor': None, 'useUserColor': False},
   3: {'position': [-334.0, -49.0], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




_4854880720 = CompositeNodeFactory(name='Geometrical transformations on images',
                             description='Changing orientation, resolution, ..',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('openalea.pylab.plotting', 'PyLabImshow'),
   3: ('openalea.image', 'lena'),
   4: ('openalea.image.interpolation', 'shift'),
   6: ('openalea.image.interpolation', 'shift'),
   8: ('openalea.image.interpolation', 'rotate'),
   10: ('openalea.image.interpolation', 'crop'),
   12: ('openalea.image.interpolation', 'zoom'),
   14: ('openalea.numpy.infos', 'shape'),
   15: ('openalea.numpy.infos', 'shape'),
   16: ('openalea.system', 'vprint')},
                             elt_connections={  4297109968: (15, 0, 16, 0),
   4297109992: (14, 0, 16, 0),
   4297110064: (10, 0, 2, 1),
   4297110088: (8, 0, 2, 1),
   4297110112: (3, 0, 8, 0),
   4297110136: (6, 0, 2, 1),
   4297110160: (4, 0, 2, 1),
   4297110184: (3, 0, 12, 0),
   4297110208: (3, 0, 4, 0),
   4297110232: (3, 0, 10, 0),
   4297110256: (3, 0, 14, 0),
   4297110280: (3, 0, 6, 0),
   4297110304: (12, 0, 15, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'PyLabImshow',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x11716a250> : "PyLabImshow"',
         'hide': True,
         'id': 2,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': -2124.1774163989867,
         'posy': -379.99595999981875,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'lena',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x11bc59510> : "lena"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -2033.910402865203,
         'posy': -674.40544928426516,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   4: {  'block': False,
         'caption': 'shift',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x11bad44d0> : "shift"',
         'hide': True,
         'id': 4,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -2022.1388746848629,
         'posy': -490.3747945468121,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   6: {  'block': False,
         'caption': 'shift',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x11bad44d0> : "shift"',
         'hide': True,
         'id': 6,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -1904.2499706410376,
         'posy': -488.93063350441292,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   8: {  'block': False,
         'caption': 'rotate',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x11bad4850> : "rotate"',
         'hide': True,
         'id': 8,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -1781.0213005130893,
         'posy': -488.54619973764051,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   10: {  'block': False,
          'caption': 'crop',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0x11bad4990> : "crop"',
          'hide': True,
          'id': 10,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -1628.9730024957587,
          'posy': -487.17892272783359,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   12: {  'block': False,
          'caption': 'zoom',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0x11bad4950> : "zoom"',
          'hide': True,
          'id': 12,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -1540.2116252699832,
          'posy': -486.17027071390442,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   14: {  'block': False,
          'caption': 'shape',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0x11be13450> : "shape"',
          'hide': True,
          'id': 14,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -1460.5596662748276,
          'posy': -577.73675324467342,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   15: {  'block': False,
          'caption': 'shape',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0x11be13450> : "shape"',
          'hide': True,
          'id': 15,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -1511.0472370053274,
          'posy': -402.53867369706836,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   16: {  'block': False,
          'caption': 'vprint',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0x11bc10e10> : "vprint"',
          'hide': True,
          'id': 16,
          'lazy': False,
          'port_hide_changed': set(),
          'posx': -1447.4156399884912,
          'posy': -323.77729647129325,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [  (0, 'None'),
         (2, "'gray'"),
         (3, "'None'"),
         (4, "'None'"),
         (5, '1'),
         (6, 'None'),
         (7, 'None'),
         (8, 'None'),
         (9, 'None'),
         (10, 'None'),
         (11, 'None'),
         (12, 'None'),
         (13, '(1, 1)'),
         (14, '{}'),
         (15, '1')],
   3: [],
   4: [  (1, '(50, 50)'),
         (2, 'None'),
         (3, '3'),
         (4, "'constant'"),
         (5, '0.0'),
         (6, 'True')],
   6: [  (1, '(50, 50)'),
         (2, 'None'),
         (3, '3'),
         (4, "'nearest'"),
         (5, '0.0'),
         (6, 'True')],
   8: [  (1, '30'),
         (2, '(1, 0)'),
         (3, 'True'),
         (4, 'None'),
         (5, '3'),
         (6, "'constant'"),
         (7, '0.0'),
         (8, 'True')],
   10: [(1, '50'), (2, '50'), (3, '-50'), (4, '-50')],
   12: [  (1, '2.0'),
          (2, 'None'),
          (3, '3'),
          (4, "'constant'"),
          (5, '0.0'),
          (6, 'True')],
   14: [],
   15: [],
   16: [  (1, "'lena_zoomed shape and lena shape'"),
          (2, 'True'),
          (3, "<type 'str'>")],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {  'position': [-2124.1774163989867, -379.99595999981875],
         'useUserColor': False,
         'userColor': None},
   3: {  'position': [-2033.910402865203, -674.40544928426516],
         'useUserColor': False,
         'userColor': None},
   4: {  'position': [-2022.1388746848629, -490.3747945468121],
         'useUserColor': False,
         'userColor': None},
   5: {  'position': [-2322.9013959763729, -441.76109780119788],
         'useUserColor': False,
         'userColor': None},
   6: {  'position': [-1904.2499706410376, -488.93063350441292],
         'useUserColor': False,
         'userColor': None},
   7: {  'position': [-2323.1053947525429, -396.84329619175082],
         'useUserColor': False,
         'userColor': None},
   8: {  'position': [-1781.0213005130893, -488.54619973764051],
         'useUserColor': False,
         'userColor': None},
   9: {  'position': [-2326.0380642601708, -355.13202904239301],
         'useUserColor': False,
         'userColor': None},
   10: {  'position': [-1628.9730024957587, -487.17892272783359],
          'useUserColor': False,
          'userColor': None},
   11: {  'position': [-2328.0553682880304, -309.74268841557614],
          'useUserColor': False,
          'userColor': None},
   12: {  'position': [-1540.2116252699832, -486.17027071390442],
          'useUserColor': False,
          'userColor': None},
   13: {  'position': [-2328.0553682880304, -266.37065181661785],
          'useUserColor': False,
          'userColor': None},
   14: {  'position': [-1460.5596662748276, -577.73675324467342],
          'useUserColor': False,
          'userColor': None},
   15: {  'position': [-1511.0472370053274, -402.53867369706836],
          'useUserColor': False,
          'userColor': None},
   16: {  'position': [-1447.4156399884912, -323.77729647129325],
          'useUserColor': False,
          'userColor': None},
   '__in__': {  'position': [0, 0], 'useUserColor': True, 'userColor': None},
   '__out__': {  'position': [0, 0], 'useUserColor': True, 'userColor': None}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




