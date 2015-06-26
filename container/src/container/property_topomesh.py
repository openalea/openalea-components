# -*- python -*-
#
#       VPlants.Meshing
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Guillaume Cerutti <guillaume.cerutti@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
################################################################################

import numpy as np
from scipy import ndimage as nd

from interface.property_graph    import PropertyError

from topomesh                    import Topomesh
from array_dict                  import array_dict

from openalea.container.utils                       import IdDict

class PropertyTopomesh(Topomesh):

    def __init__(self, degree=3, topomesh=None, **kwds):
        """todo"""
        self._wisp_properties = [{} for d in xrange(degree+1)]
        self._interface_properties = [{} for d in xrange(degree+1)]
        self._topomesh_properties= {}

        self._interface = [None] + [IdDict(idgenerator="set") for i in xrange(degree)]

        Topomesh.__init__(self, degree, **kwds)
        if topomesh is not None:
            self.extend(topomesh)

    def __getitem__(self,key):
        if isinstance(key,tuple) and len(key) == 2:
            degree = key[0]
            wid = key[1]
            if wid in self.wisps(degree):
                property_wid = dict([(wid,{})])
                for property_name in self.wisp_property_names(degree=degree):
                    if self._wisp_properties[degree][property_name].has_key(wid):
                        property_wid[wid][property_name] = self._wisp_properties[degree][property_name][wid]
                return property_wid
            else:
                raise KeyError(str(key))
        elif isinstance(key,int):
            degree = key
            if (degree <= self._degree):
                property_wids = {}
                for wid in self.wisps(degree):
                    property_wids[wid] = {}
                    for property_name in self.wisp_property_names(degree=degree):
                        if self._wisp_properties[degree][property_name].has_key(wid):
                            property_wids[wid][property_name] = self._wisp_properties[degree][property_name][wid]
                return property_wids
            else:
                raise KeyError(str(key))
        else:
            raise KeyError(str(key))

    def wisp_property_names(self,degree):
        """todo"""
        return self._wisp_properties[degree].iterkeys()

    def wisp_properties(self,degree):
        """todo"""
        return self._wisp_properties[degree]

    def wisp_property(self,property_name,degree,wids = None):
        """todo"""
        try:
            if wids is not None:
                return array_dict(self._wisp_properties[degree][property_name].values(wids),wids)
            else:
                return self._wisp_properties[degree][property_name]
        except KeyError:
            raise PropertyError("property "+property_name+" is undefined on wisps of degree "+str(degree))

    def add_wisp_property(self,property_name,degree,values = None):
        """todo"""
        if property_name in self._wisp_properties[degree]:
            raise PropertyError("property "+property_name+" is already defined on wisps of degree "+str(degree))
        if values is None: values = array_dict()  
        elif isinstance(values,np.ndarray):
            keys = np.array(list(self.wisps(degree)))
            values = array_dict(values,keys) 
        elif isinstance(values,dict):
            values = array_dict(values)      
        if not isinstance(values, array_dict):
            raise TypeError("Values are not in an acceptable type (array, dict, array_dict)")  
        self._wisp_properties[degree][property_name] = values

    def update_wisp_property(self,property_name,degree,values,keys=None,erase_property=True):
        """todo"""
        if not (isinstance(values, np.ndarray) or isinstance(values, dict) or isinstance(values, array_dict)):
            raise TypeError("Values are not in an acceptable type (array, dict, array_dict)")                                
        if property_name not in self._wisp_properties[degree]:
            print PropertyError("property "+property_name+" is undefined on elements of degree "+str(degree))
            print "Creating property ",property_name," for degree ",degree
            self._wisp_properties[degree][property_name] = array_dict()
        if isinstance(values,np.ndarray):
            if keys is None:
                keys = np.array(list(self.wisps(degree)))
            #self._wisp_properties[degree][property_name].update(values,keys=keys,ignore_missing_keys=False,erase_missing_keys=erase_property)
            self._wisp_properties[degree][property_name] = array_dict(values,keys)
        elif isinstance(values,dict):
            if keys is None:
                keys = np.array(values.keys())
            #self._wisp_properties[degree][property_name].update(np.array(values.values()),keys=keys,ignore_missing_keys=False,erase_missing_keys=erase_property)
            self._wisp_properties[degree][property_name] = array_dict(values)
        elif isinstance(values,array_dict):
            if keys is None:
                keys = values.keys()
            #self._wisp_properties[degree][property_name].update(values.values(),keys=keys,ignore_missing_keys=False,erase_missing_keys=erase_property)
            self._wisp_properties[degree][property_name] = values

    def has_wisp_property(self,property_name,degree,is_computed=False):
        if property_name in self._wisp_properties[degree]:
            return (not is_computed) or (len(self._wisp_properties[degree][property_name]) == self.nb_wisps(degree))
        else:
            return False

    def interface_property_names(self,degree):
        """todo"""
        return self._interface_properties[degree].iterkeys()

    def interface_properties(self,degree):
        """todo"""
        return self._interface_properties[degree]

    def interface_property(self,property_name,degree,wids = None):
        """todo"""
        try:
            return self._interface_properties[degree][property_name]
        except KeyError:
            raise PropertyError("property "+property_name+" is undefined on interfaces of degree "+str(degree))

    def add_interface_property(self,property_name,degree,values = None):
        """todo"""
        if property_name in self._interface_properties[degree]:
            raise PropertyError("property "+property_name+" is already defined on interfaces of degree "+str(degree))
        if values is None: values = array_dict()  
        elif isinstance(values,np.ndarray):
            keys = np.array(self._interface.keys())
            values = array_dict(values,keys) 
        elif isinstance(values,dict):
            values = array_dict(values)      
        if not isinstance(values, array_dict):
            raise TypeError("Values are not in an acceptable type (array, dict, array_dict)")  
        self._interface_properties[degree][property_name] = values

    def update_interface_property(self,property_name,degree,values,keys=None):
        """todo"""
        if not (isinstance(values, np.ndarray) or isinstance(values, dict) or isinstance(values, array_dict)):
            raise TypeError("Values are not in an acceptable type (array, dict, array_dict)")                                
        if property_name not in self._interface_properties[degree]:
            print PropertyError("property "+property_name+" is undefined on elements of degree "+str(degree))
            print "Creating property ",property_name," for degree ",degree
            self._interface_properties[degree][property_name] = array_dict()
        if isinstance(values,np.ndarray):
            if keys is None:
                keys = np.array(self._interface.keys())
            self._interface_properties[degree][property_name].update(values,keys=keys,ignore_missing_keys=False)
        elif isinstance(values,dict):
            if keys is None:
                keys = np.array(values.keys())
            self._interface_properties[degree][property_name].update(np.array(values.values()),keys=keys,ignore_missing_keys=False)
        elif isinstance(values,array_dict):
            if keys is None:
                keys = values.keys()
            self._interface_properties[degree][property_name].update(values.values(),keys=keys,ignore_missing_keys=False)

    def has_interface_property(self,property_name,degree,is_computed=False):
        if property_name in self._interface_properties[degree]:
            return (not is_computed) or (len(self._interface_properties[degree][property_name]) == len(list(self.interfaces(degree))))
        else:
            return False

    def interface(self,degree,wid1,wid2):
        assert degree>0
        if not wid2 in self.border_neighbors(degree,wid1):
            return None
        else:
            return np.intersect1d(np.where(np.array(self._interface[degree].values()) == wid1)[0],np.where(np.array(self._interface[degree].values()) == wid2)[0])[0]

    def interfaces(self,degree):
        assert degree>0
        return iter(self._interface[degree])

    def extend(self,topomesh):
        """todo"""
        for pid in topomesh.wisps(0):
            self.add_wisp(0,pid)
        for eid in topomesh.wisps(1):
            self.add_wisp(1,eid)
            for pid in topomesh.borders(1,eid):
                for n_eid in self.regions(0,pid):
                    if not (n_eid,eid) in self._interface[1].values():
                        iid = self._interface[1].add((n_eid,eid),None)
                self.link(1,eid,pid)
        if self._degree > 1:
            for fid in topomesh.wisps(2):
                self.add_wisp(2,fid)
                for eid in topomesh.borders(2,fid):
                    for n_fid in self.regions(1,eid):
                        if not (n_fid,fid) in self._interface[2].values():
                            iid = self._interface[2].add((n_fid,fid),None)
                    self.link(2,fid,eid)
        if self._degree > 2:
            for cid in topomesh.wisps(3):
                self.add_wisp(3,cid)
                for fid in topomesh.borders(3,cid):
                    for n_cid in self.regions(2,fid):
                        if not (n_cid,cid) in self._interface[3].values():
                            iid = self._interface[3].add((n_cid,cid),None)
                    self.link(3,cid,fid)

