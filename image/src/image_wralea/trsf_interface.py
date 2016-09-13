# -*- coding: utf-8 -*-
# -*- python -*-
#
#       Copyright 2016 INRIA
#
#       File author(s):
#           Sophie Ribes <sophie.ribes@inria.fr>
#
#------------------------------------------------------------------------------

"""
Declaration of ITrsf interface
Interface for BalTransformation transformations
"""

from openalea.core import *
try:
    from timagetk.wrapping.bal_trsf import BalTransformation
except ImportError:
    raise ImportError('Import Error')

class ITrsf(IInterface):
    """
    Interface for BalTransformation transformations
    """
    __pytype__ = BalTransformation
