# -*- python -*-
#
#       OpenAlea.Image
#
#       Copyright 2006 - 2012 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@sophia.inria.fr>
#                       Jonathan LEGRAND <jonathan.legrand@ens-lyon.fr>
#                       Frederic BOUDON <frederic.boudon@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import warnings, math, copy, gzip, time
import numpy as np, scipy.ndimage as nd, cPickle as pickle
from numpy.linalg import svd, norm
from os.path import exists, splitext, split

from openalea.image.spatial_image import SpatialImage

get_path_from_filename = split
#~ def get_path_from_filename(fname):
    #~ """
    #~ Example:
        #~ - input: "/home/jonathan/Softwares/scripts_python/basics.py"
        #~ - output: "/home/jonathan/Softwares/scripts_python/"
    #~ """
    #~ split_fname = fname.rsplit("/")
    #~ if len(split_fname)>1:
        #~ path, fname = "/".join(split_fname[:-1])+"/", split_fname[-1]
    #~ else:
        #~ path, fname = "", split_fname
#~ 
    #~ return path, fname


def fname_NoExt(fname):
    """
    Return the filename without extension.
    """
    # First we take care of possible gzip compression
    if fname.endswith(".gz"):
        fname = fname[:-3]

    if fname.endswith(".tiff"):
        fname = fname[:-5]
    elif fname.endswith(".tif") or fname.endswith(".inr") or fname.endswith(".vtk"):
        fname = fname[:-4]

    return fname


def dilation(slices):
    """
    Function dilating slices: extend the boundingbox of one voxel.
    """
    return [ slice(max(0,s.start-1), s.stop+1) for s in slices ]


def dilation_by(slices, amount=2):
    """
    Function dilating slices: extend the boundingbox of one voxel.
    """
    return [ slice(max(0,s.start-amount), s.stop+amount) for s in slices ]


def wall(mask_img, label_id):
    """
    TODO
    """
    img = (mask_img == label_id)
    dil = nd.binary_dilation(img)
    contact = dil - img
    return mask_img[contact]


def contact_surface(mask_img, label_id):
    """
    TODO
    """
    img = wall(mask_img,label_id)
    return set( np.unique(img) )


def real_indices(slices, resolutions):
    """
    TODO
    """
    return [ (s.start*r, s.stop*r) for s,r in zip(slices,resolutions) ]


def hollow_out_cells(image, background, remove_background = True, verbose = True):
    """
    Laplacian filter used to dectect and return an Spatial Image containing only cell walls.
    (The Laplacian of an image highlights regions of rapid intensity change.)

    :Parameters:
     - `image` (SpatialImage) - Segmented image (tissu).
     - `background` (int) - label representing the background (to remove).

    :Return:
     - `m` (SpatialImage) - Spatial Image containing hollowed out cells (only walls).
    """
    if verbose: print 'Hollowing out cells... ',
    b = nd.laplace(image)
    mask = b!=0
    m = image * mask
    if remove_background:
        mask = m!=background
        m = m*mask
    if verbose: print 'Done !!'
    return m


def sort_boundingbox(boundingbox, label_1, label_2):
    """
    Use this to determine which label as the smaller boundingbox !
    """
    assert isinstance(boundingbox, dict)
    if (not boundingbox.has_key(label_1)) and boundingbox.has_key(label_2):
        return (label_2, label_1)
    if boundingbox.has_key(label_1) and (not boundingbox.has_key(label_2)):
        return (label_1, label_2)
    if (not boundingbox.has_key(label_1)) and (not boundingbox.has_key(label_2)):
        return (None, None)

    bbox_1 = boundingbox[label_1]
    bbox_2 = boundingbox[label_2]
    vol_bbox_1 = (bbox_1[0].stop - bbox_1[0].start)*(bbox_1[1].stop - bbox_1[1].start)*(bbox_1[2].stop - bbox_1[2].start)
    vol_bbox_2 = (bbox_2[0].stop - bbox_2[0].start)*(bbox_2[1].stop - bbox_2[1].start)*(bbox_2[2].stop - bbox_2[2].start)

    return (label_1, label_2) if vol_bbox_1<vol_bbox_2 else (label_2, label_1)


def find_smallest_boundingbox(image, label_1, label_2):
    """
    
    """
    boundingbox = nd.find_objects(image, max_label=max([label_1, label_2]))
    boundingbox = {label_1:boundingbox[label_1-1], label_2:boundingbox[label_2-1]}
    label_1, label_2 = sort_boundingbox(boundingbox, label_1, label_2)
    return bbox[label_1]


def coordinates_centering3D(coordinates):
    """
    Center coordinates around their mean.
    """
    try:
        x,y,z = coordinates
    except:
        x,y,z = coordinates.T
    # Now perform centering operation:
    x = x - center[0]
    y = y - center[1]
    z = z - center[2]
    return np.array([x,y,z])

def compute_covariance_matrix(coordinates):
    """
    Function computing the covariance matrix of a given pointset (of coordinates).
    :Parameters:
     - `coordinates` (np.array) - poinset of coordinates
    """
    if not isinstance(coordinates, np.ndarray):
        coordinates = np.array(coordinates)
    if coord.shape[0]>3:
        coord = coord.T
    return 1./max(coord.shape()) * np.dot(coord,coord.T)

def eigen_values_vectors(cov_matrix):
    """
    Function extracting the eigen vectors and associated values for a variance-covariance matrix.
    :Parameters:
     - `coordinates` (np.array) - poinset of coordinates
    :Returns:
     - eig_val (list) - lenght 3 list of sorted eigen values associated to the eigen vectors
     - eig_vec (np.array) - 3x3 np.array of eigen vectors --by rows-- associated to sorted eigen values 
    """
    assert max(cov.shape)<=3
    eig_val, eig_vec = np.linalg.eig(cov)
    decreasing_index = eig_val.argsort()[::-1]
    eig_val, eig_vec = eig_val[decreasing_index], eig_vec[:,decreasing_index] # np.linalg.eig return eigenvectors by column !!
    eig_vec = np.array(eig_vec).T # ... our standard is by rows !
    return eig_val, eig_vec

#~ def closest_from_A(A, pts2search):
    #~ """
    #~ Find the closest point from A in a list of points 'pts2search'.
    #~ Return the 3D coordinates of the closest point from A.
#~ 
    #~ :Parameters:
     #~ - `A` (list/numpy.array) - 2D/3D coordinates of the point of interest (xA, yA)/(xA, yA, zA);
     #~ - `pts2search` (list) - list of 2D/3D coordinates
    #~ """
    #~ dist_1 = float('inf')
    #~ for k in pts2search:
        #~ dist_2 = norm( A, k)
        #~ if dist_2 < dist_1:
            #~ pts_min_dist = k
            #~ dist_1 = copy.copy(dist_2)
#~ 
    #~ return pts_min_dist

def return_list_of_vectors(tensor, by_row=True):
    """
    Return a standard list of list from an array, if sorted 'by_row' or not.
    """
    if isinstance(tensor, dict):
        return dict([(k,return_list_of_vectors(t,by_row)) for k,t in tensor.iteritems()])
    elif isinstance(tensor, list) and tensor[0].shape == (3,3):
        return [return_list_of_vectors(t,by_row) for t in tensor]
    else:
        if by_row:
            return [tensor[v] for v in xrange(len(tensor))]
        else:
            return [tensor[:,v] for v in xrange(len(tensor))]


NPLIST, LIST, DICT = range(3)

class AbstractSpatialImageAnalysis(object):
    """
    This object can extract a number of 2D or 3D geometric estimator from a SpatialImage
    (cells volume...) and the neighborhood structure (also the shared surface area of two neighboring cells).
    """

    def __init__(self, image, ignoredlabels = [], return_type = DICT, background = None):
        """
        ..warning :: Label features in the images are an arithmetic progression of continous integers.

        By default, we create cache of a property only if it can be used by several functions.
        """
        if isinstance(image, SpatialImage):
            self.image = image
        else:
            self.image = SpatialImage(image)

        # -- We use this to avoid (when possible) computation of properties on background and other cells (ex: cell in image margins)
        if isinstance(ignoredlabels, int):
            ignoredlabels = [ignoredlabels]
        self._ignoredlabels = set(ignoredlabels)

        # -- Sounds a bit paranoiac but usefull !!
        if background is not None:
            if not isinstance(background,int):
                raise ValueError("The label you provided as background is not an integer !")
            if background not in self.image:
                raise ValueError("The background you provided has not been detected in the image !")
            self._ignoredlabels.update([background])
        else:
            warnings.warn("No value defining the background, some functionalities won't work !")

        # -- Variables for caching informations:
        self._voxelsize = image.voxelsize
        self._background = background
        self._labels = None
        self._bbox = None
        self._kernels = None
        self._neighbors = None
        self._cell_layer1 = None
        self._center_of_mass = {} # voxel units

        # -- Variables for meta-informations:
        try:
            filepath, filename = get_path_from_filename(image.info["Filename"])
            self.filepath, self.filename, self.fileext = filepath, fname_NoExt(filename), filename.strip(fname_NoExt(filename))
        except:
            self.filepath, self.filename, self.fileext = None, None, None
        self.info = dict([(k,v) for k,v in image.info.iteritems() if k != "Filename"])

        self.return_type = return_type


    def is3D(self): return False

    def background(self): return self._background

    def ignoredlabels(self): return self._ignoredlabels

    def add2ignoredlabels(self, list2add, verbose = False):
        """
        Add labels to the ignoredlabels list (set) and update the self._labels cache.
        """
        if isinstance(list2add, int):
            list2add = [list2add]

        if verbose: print 'Adding labels', list2add,'to the list of labels to ignore...'
        self._ignoredlabels.update(list2add)
        if verbose: print 'Updating labels list...'
        self._labels = self.__labels()

    def consideronlylabels(self, list2consider, verbose = False):
        """
        Add labels to the ignoredlabels list (set) and update the self._labels cache.
        """
        if isinstance(list2consider, int):
            list2consider = [list2consider]

        toignore = set(np.unique(self.image))-set(list2consider)
        integers = np.vectorize(lambda x : int(x))
        toignore = integers(list(toignore)).tolist()


        if verbose: print 'Adding labels', list2add,'to the list of labels to ignore...'
        self._ignoredlabels.update(toignore)
        if verbose: print 'Updating labels list...'
        self._labels = self.__labels()


    def save_analysis(self, filename = ""):
        """
        Save a 'SpatialImageAnalysis' object, under the name 'filename'.
        :Parameters:
         - `filename` (str) - name of the file to create WITHOUT extension.
        """
        # If no filename is given, we create one based on the name of the SpatialImage (if possible).
        if ( filename == "" ) and ( self.filename != None ): # None is the default value in self.__init__
            filename = self.filename
        elif filename != "":
            assert isinstance(filename, str)
        else:
            raise ValueError("The filename is missing, and there's no information about it in "+str(self)+". Saving process ABORTED.")

        # -- We make sure the file doesn't already exist !
        if exists(filename):
            raise ValueError("The file "+filename+" already exist. Saving process ABORTED.")
            return None

        if filename.endswith(".inr.gz"):
            filename = filename[:-7]+"_analysis.pklz"
        if filename.endswith(".inr"):
            filename = filename[:-4]+"_analysis.pklz"

        # -- We save a compresed version of the file:
        f = gzip.open(filename, 'w')
        pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        print "File {} succesfully created !!".format(filename)

    @staticmethod
    def load(filename):
        """
        Load a SpatialImageAnalysis from the file `filename`.
        """
        f = gzip.open(filename, 'rb')
        spia = pickle.load( f )
        f.close()
        print "File {} succesfully loaded !!".format(filename)
        return spia
        

    def save_image(self, filename= "", overwrite= False):
        """
        Save the image in 'SpatialImageAnalysis' object (self.image), under the name 'filename'.
        :Parameters:
         - `filename` (str) - name of the file to create WITHOUT extension (automatically add '.inr.gz').
         - `overwrite` (bool) - (Optional) if True overwrite the file if found on the disk, otherwise abort.
        """
        from openalea.image.serial.basics import write_inrimage
        # If no filename is given, we create one based on the name of the SpatialImage (if possible).
        if ( filename == "" ) and ( self.filename != None ): # None is the default value in self.__init__
            filename = self.filename
        elif filename != "":
            assert isinstance(filename, str)
        else:
            raise ValueError("The filename is missing, and there's no information about it in "+str(self)+". Saving process ABORTED.")

        # -- We make sure the file doesn't already exist !
        if exists(filename) and not overwrite:
            raise ValueError("The file "+filename+" already exist. Saving process ABORTED.")
            return None

        if filename.endswith(".inr"):
            filename = filename+'.gz'
        elif not filename.endswith(".inr.gz"):
            filename = filename+'.inr.gz'

        # -- We save a compresed version of the file:
        write_inrimage(filename, self.image)
        print "File " + filename + " succesfully created !!"


    def convert_return(self, values, labels = None, overide_return_type = None):
        """
        This function convert outputs of analysis functions.
        """
        tmp_save_type = copy.copy(self.return_type)
        if not overide_return_type is None:
            self.return_type = overide_return_type
        # -- In case of unique label, just return the result for this label
        if not labels is None and isinstance(labels,int):
            self.return_type = copy.copy(tmp_save_type)
            return values
        # -- return a numpy array
        elif self.return_type == NPLIST:
            self.return_type = copy.copy(tmp_save_type)
            return values
        # -- return a standard python list
        elif self.return_type == LIST:
            if isinstance(values,list):
                return values
            else:
                self.return_type = copy.copy(tmp_save_type)
                return values.tolist()
        # -- return a dictionary
        else:
            self.return_type = copy.copy(tmp_save_type)
            return dict(zip(labels,values))


    def labels(self):
        """
        Return the list of labels used.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.labels()
        [1,2,3,4,5,6,7]
        """
        if self._labels is None: self._labels = self.__labels()
        return self._labels

    def __labels(self):
        """
        Compute the actual list of labels.
        :IMPORTANT: `background` is not in the list of labels.
        """
        labels = set(np.unique(self.image))-self._ignoredlabels
        return list(map(int, labels))

    def nb_labels(self):
        """
        Return the number of labels.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.nb_labels()
        7
        """
        if self._labels is None : self._labels = self.__labels()
        return len(self._labels)

    def label_request(self, labels):
        """
        The following lines are often needed to ensure the correct format of labels, as well as their presence within the image.
        """
        if isinstance(labels, int):
            if not labels in self.labels():
                print "The following id was not found within the image labels: {}".format(labels)
            labels = [labels]
        elif isinstance(labels, list):
            labels = list( set(labels) & set(self.labels()) )
            not_in_labels = list( set(labels) - set(self.labels()) )
            if not_in_labels != []:
                print "The following ids were not found within the image labels: {}".format(not_in_labels)
        elif (labels is None):
            labels = self.labels()
        elif isinstance(labels, str):
            if (labels.lower() == 'all'):
                labels = self.labels()
            if (labels.lower() == 'l1'):
                labels = self.cell_first_layer()
            if (labels.lower() == 'l2'):
                labels = self.cell_second_layer()
        else:
            raise ValueError("This is not usable as `labels`: {}".format(labels))

        return labels


    def center_of_mass(self, labels=None, real=True, verbose=False):
        """
        Return the center of mass of the labels.

        :Parameters:
         - `labels` (int) - single label number or a sequence of label numbers of the objects to be measured.
            If labels is None, all labels are used.
         - `real` (bool) - If True (default), center of mass is in real-world units else in voxels.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.center_of_mass(7)
        [0.75, 2.75, 0.0]

        >>> analysis.center_of_mass([7,2])
        [[0.75, 2.75, 0.0], [1.3333333333333333, 0.66666666666666663, 0.0]]

        >>> analysis.center_of_mass()
        [[1.8, 2.2999999999999998, 0.0],
         [1.3333333333333333, 0.66666666666666663, 0.0],
         [1.5, 4.5, 0.0],
         [3.0, 3.0, 0.0],
         [1.0, 2.0, 0.0],
         [1.0, 1.0, 0.0],
         [0.75, 2.75, 0.0]]
        """
        # Check the provided `labels`:
        labels = self.label_request(labels)

        if verbose: print "Computing cells center of mass:"
        center = {}; N = len(labels); percent = 0
        for n,l in enumerate(labels):
            if verbose and (n*100/N>=percent): print "{}%...".format(percent),; percent += 5
            if verbose and (n+1==N): print "100%"
            if self._center_of_mass.has_key(l):
                center[l] = self._center_of_mass[l]
            else:
                try:
                    slices = self.boundingbox(l,real=False)
                    crop_im = self.image[slices]
                    c_o_m = np.array(nd.center_of_mass(crop_im, crop_im, index=l))
                    c_o_m = [c_o_m[i] + slice.start for i,slice in enumerate(slices)]
                except:
                    crop_im = self.image
                    c_o_m = np.array(nd.center_of_mass(crop_im, crop_im, index=l))
                self._center_of_mass[l] = c_o_m
                center[l] = c_o_m

        if real:
            center = dict([(l,np.multiply(center[l],self._voxelsize)) for l in labels])

        if len(labels)==1:
            return center[labels[0]]
        else:
            return center


    def boundingbox(self, labels = None, real = False):
        """
        Return the bounding box of a label.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.boundingbox(7)
        (slice(0, 3), slice(2, 4), slice(0, 1))

        >>> analysis.boundingbox([7,2])
        [(slice(0, 3), slice(2, 4), slice(0, 1)), (slice(0, 3), slice(0, 2), slice(0, 1))]

        >>> analysis.boundingbox()
        [(slice(0, 4), slice(0, 6), slice(0, 1)),
        (slice(0, 3), slice(0, 2), slice(0, 1)),
        (slice(1, 3), slice(4, 6), slice(0, 1)),
        (slice(3, 4), slice(3, 4), slice(0, 1)),
        (slice(1, 2), slice(2, 3), slice(0, 1)),
        (slice(1, 2), slice(1, 2), slice(0, 1)),
        (slice(0, 3), slice(2, 4), slice(0, 1))]
        """
        if labels == 0:
            return nd.find_objects(self.image==0)[0]

        if self._bbox is None:
            self._bbox = nd.find_objects(self.image)

        if labels is None:
            labels = copy.copy(self.labels())
            if self.background() is not None:
                labels.append(self.background())

        # bbox of object labelled 1 to n are stored into self._bbox. To access i-th element, we have to use i-1 index
        if isinstance (labels, list):
            bboxes = [self._bbox[i-1] for i in labels]
            if real : return self.convert_return([real_indices(bbox,self._voxelsize) for bbox in bboxes],labels)
            else : return self.convert_return(bboxes,labels)

        else :
            try:
                if real:  return real_indices(self._bbox[labels-1], self._voxelsize)
                else : return self._bbox[labels-1]
            except:
                return None


    def neighbors(self, labels=None, min_contact_area=None, real_area=True, verbose=True):
        """
        Return the list of neighbors of a label.

        :WARNING:
            If `min_contact_area` is given it should be in real world units.

        :Parameters:
         - `labels` (None|int|list) - label or list of labels of which we want to return the neighbors. If none, neighbors for all labels found in self.image will be returned.
         - `min_contact_area` (None|int|float) - value of the min contact area threshold.
         - `real_area` (bool) - indicate wheter the min contact area is a real world value or a number of voxels.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.neighbors(7)
        [1, 2, 3, 4, 5]

        >>> analysis.neighbors([7,2])
        {7: [1, 2, 3, 4, 5], 2: [1, 6, 7] }

        >>> analysis.neighbors()
        {1: [2, 3, 4, 5, 6, 7],
         2: [1, 6, 7],
         3: [1, 7],
         4: [1, 7],
         5: [1, 6, 7],
         6: [1, 2, 5],
         7: [1, 2, 3, 4, 5] }
        """
        if (min_contact_area is not None) and verbose:
            if real_area:
                try: print u"Neighbors will be filtered according to a min contact area of %.2f \u03BCm\u00B2" %min_contact_area
                except: print u"Neighbors will be filtered according to a min contact area of %.2f micro m 2" %min_contact_area
            else:
                print "Neighbors will be filtered according to a min contact area of %d voxels" %min_contact_area
        if labels is None:
            return self._all_neighbors(min_contact_area, real_area)
        elif not isinstance (labels , list):
            return self._neighbors_with_mask(labels, min_contact_area, real_area)
        else:
            return self._neighbors_from_list_with_mask(labels, min_contact_area, real_area)

    def _neighbors_with_mask(self, label, min_contact_area=None, real_area=True):
        if not self._neighbors is None and label in self._neighbors.keys():
            result = self._neighbors[label]
            if  min_contact_area is None:
                return result
            else:
                return self._neighbors_filtering_by_contact_area(label, result, min_contact_area, real_area)

        try:
            slices = self.boundingbox(label)
            ex_slices = dilation(slices)
            mask_img = self.image[ex_slices]
        except:
            mask_img = self.image
        neigh = list(contact_surface(mask_img,label))
        if min_contact_area is not None:
            neigh = self._neighbors_filtering_by_contact_area(label, neigh, min_contact_area, real_area)

        return neigh

    def _neighbors_from_list_with_mask(self, labels, min_contact_area=None, real_area=True):
        if not self._neighbors is None :
            result = dict([(i,self._neighbors[i]) for i in labels])
            if  min_contact_area is None:
                return result
            else:
                return self._filter_with_area(result, min_contact_area, real_area)

        edges = {}
        for label in labels:
            try:
                slices = self.boundingbox(label)
                ex_slices = dilation(slices)
                mask_img = self.image[ex_slices]
            except:
                mask_img = self.image
            neigh = list(contact_surface(mask_img,label))
            if min_contact_area is not None:
                neigh = self._neighbors_filtering_by_contact_area(label, neigh, min_contact_area, real_area)
            edges[label] = neigh

        return edges

    def _all_neighbors(self, min_contact_area=None, real_area=True):
        if not self._neighbors is None:
            result = self._neighbors
            if  min_contact_area is None:
                return result
            else:
                return self._filter_with_area(result, min_contact_area, real_area)

        edges = {} # store src, target
        slice_label = self.boundingbox()
        if self.return_type == 0 or self.return_type == 1:
            slice_label = dict( (label+1,slices) for label, slices in enumerate(slice_label))
            # label_id = label +1 because the label_id begin at 1
            # and the enumerate begin at 0.
        for label_id, slices in slice_label.items():
            # sometimes, the label doesn't exist ans slices is None
            try:
                ex_slices = dilation(slices)
                mask_img = self.image[ex_slices]
            except:
                mask_img = self.image
            neigh = list(contact_surface(mask_img,label_id))
            edges[label_id]=neigh

        self._neighbors = edges
        if min_contact_area is None:
            return edges
        else:
            return self._filter_with_area(edges, min_contact_area, real_area)

    def _filter_with_area(self, neigborhood_dictionary, min_contact_area, real_area):
        """
        Function filtering a neighborhood dictionary according to a minimal contact area between two neigbhors.

        :Parameters:
         - `neigborhood_dictionary` (dict) - dictionary of neighborhood to be filtered.
         - `min_contact_area` (None|int|float) - value of the min contact area threshold.
         - `real_area` (bool) - indicate wheter the min contact area is a real world value or a number of voxels.
        """
        filtered_dict = {}
        for label in neigborhood_dictionary.keys():
            filtered_dict[label] = self._neighbors_filtering_by_contact_area(label, neigborhood_dictionary[label], min_contact_area, real_area)

        return filtered_dict

    def _neighbors_filtering_by_contact_area(self, label, neighbors, min_contact_area, real_area):
        """
        Function used to filter the returned neighbors according to a given minimal contact area between them!

        :Parameters:
         - `label` (int) - label of the image to threshold by the min contact area.
         - `neighbors` (list) - list of neighbors of the `label` to be filtered.
         - `min_contact_area` (None|int|float) - value of the min contact area threshold.
         - `real_area` (bool) - indicate wheter the min contact area is a real world value or a number of voxels.
        """
        areas = self.cell_wall_area(label, neighbors, real_area)
        for i,j in areas.keys():
            if areas[(i,j)] < min_contact_area:
                neighbors.remove( i if j==label else j )

        return neighbors

    def neighbor_kernels(self):
        if self._kernels is None:
            if self.is3D():
                X1kernel = np.zeros((3,3,3),np.bool)
                X1kernel[:,1,1] = True
                X1kernel[0,1,1] = False
                X2kernel = np.zeros((3,3,3),np.bool)
                X2kernel[:,1,1] = True
                X2kernel[2,1,1] = False
                Y1kernel = np.zeros((3,3,3),np.bool)
                Y1kernel[1,:,1] = True
                Y1kernel[1,0,1] = False
                Y2kernel = np.zeros((3,3,3),np.bool)
                Y2kernel[1,:,1] = True
                Y2kernel[1,2,1] = False
                Z1kernel = np.zeros((3,3,3),np.bool)
                Z1kernel[1,1,:] = True
                Z1kernel[1,1,0] = False
                Z2kernel = np.zeros((3,3,3),np.bool)
                Z2kernel[1,1,:] = True
                Z2kernel[1,1,2] = False
                self._kernels = (X1kernel,X2kernel,Y1kernel,Y2kernel,Z1kernel,Z2kernel)
            else:
                X1kernel = np.zeros((3,3),np.bool)
                X1kernel[:,1] = True
                X1kernel[0,1] = False
                X2kernel = np.zeros((3,3),np.bool)
                X2kernel[:,1] = True
                X2kernel[2,1] = False
                Y1kernel = np.zeros((3,3),np.bool)
                Y1kernel[1,:] = True
                Y1kernel[1,0] = False
                Y2kernel = np.zeros((3,3),np.bool)
                Y2kernel[1,:] = True
                Y2kernel[1,2] = False
                self._kernels = (X1kernel,X2kernel,Y1kernel,Y2kernel)

        return self._kernels

    def neighbors_number(self, labels=None, min_contact_area=None, real_area=True):
        """
        Return the number of neigbors of each label.
        """
        nei = self.neighbors(labels, min_contact_area, real_area)
        return dict([(k,len(v)) for k,v in nei.iteritems()])


    def get_voxel_face_surface(self):
        a = self._voxelsize
        if len(a)==3:
            return np.array([a[1] * a[2],a[2] * a[0],a[0] * a[1] ])
        if len(a)==2:
            return np.array([a[0],a[1]])


    def wall_voxels_between_two_cells(self, label_1, label_2, bbox = None, verbose = False):
        """
        Return the voxels coordinates defining the contact wall between two labels.

        :Parameters:
         - `image` (ndarray of ints) - Array containing objects defined by labels
         - `label_1` (int) - object id #1
         - `label_2` (int) - object id #2
         - `bbox` (dict, optional) - If given, contain a dict of slices

        :Return:
         - xyz 3xN array.
        """

        if bbox is not None:
            if isinstance(bbox, dict):
                label_1, label_2 = sort_boundingbox(bbox, label_1, label_2)
                boundingbox = bbox[label_1]
            elif isinstance(bbox, tuple) and len(bbox)==3:
                boundingbox = bbox
            else:
                try:
                    boundingbox = find_smallest_boundingbox(self.image, label_1, label_2)
                except:
                    print "Could neither use the provided value of `bbox`, nor gess it!"
                    boundingbox = tuple([(0,s-1,None) for s in self.image.shape])
            dilated_bbox = dilation( boundingbox )
            dilated_bbox_img = self.image[dilated_bbox]
        else:
            try:
                boundingbox = find_smallest_boundingbox(self.image, label_1, label_2)
            except:
                dilated_bbox_img = self.image

        mask_img_1 = (dilated_bbox_img == label_1)
        mask_img_2 = (dilated_bbox_img == label_2)

        struct = nd.generate_binary_structure(3, 2)
        dil_1 = nd.binary_dilation(mask_img_1, structure=struct)
        dil_2 = nd.binary_dilation(mask_img_2, structure=struct)
        x,y,z = np.where( ( (dil_1 & mask_img_2) | (dil_2 & mask_img_1) ) == 1 )

        if bbox is not None:
            return np.array( (x+dilated_bbox[0].start, y+dilated_bbox[1].start, z+dilated_bbox[2].start) )
        else:
            return np.array( (x, y, z) )


    def walls_voxels_per_cell(self, label_1, bbox = None, neighbors = None, neighbors2ignore = [], background = None, try_to_use_neighbors2ignore = False, verbose = False ):
        """
        Return the voxels coordinates of all walls from one cell.
        There must be a contact defined between two labels, the given one and its neighbors.

        :Parameters:
         - `image` (ndarray of ints) - Array containing objects defined by labels
         - `label_1` (int): cell id #1.
         - `bbox` (dict, optional) - dictionary of slices defining bounding box for each labelled object.
         - `neighbors` (list, optional) - list of neighbors for the object `label_1`.
         - `neighbors2ignore` (list, optional) - labels of neighbors to ignore while considering separation between the object `label_1` and its neighbors. All ignored labels will be returned as 0.
        :Return:
         - `coord` (dict): *keys= [min(labels_1,neighbors[n]), max(labels_1,neighbors[n])]; *values= xyz 3xN array.
        """
        # -- We use the bounding box to work faster (on a smaller image)
        if isinstance(bbox,dict):
            boundingbox = bbox(label_1)
        elif (isinstance(bbox,tuple) or isinstance(bbox,list)) and isinstance(bbox[0],slice):
            boundingbox = bbox
        elif bbox is None:
            boundingbox = self.boundingbox(label_1)
        dilated_bbox = dilation(dilation( boundingbox ))
        dilated_bbox_img = self.image[dilated_bbox]

        # -- Binary mask saying where the label_1 can be found on the image.
        mask_img_1 = (dilated_bbox_img == label_1)
        struct = nd.generate_binary_structure(3, 2)
        dil_1 = nd.binary_dilation(mask_img_1, structure=struct)

        # -- We edit the neighbors list as required:
        if neighbors is None:
            neighbors = np.unique(dilated_bbox_img)
            neighbors.remove(label_1)
        if isinstance(neighbors,int):
            neighbors = [neighbors]
        if isinstance(neighbors,dict):
            neighborhood = neighbors
            neighbors = copy.copy(neighborhood[label_1])
        if background in neighbors2ignore:
            neighbors.remove(background) # We don't want the voxels coordinates with the background.
            if try_to_use_neighbors2ignore:
                neighbors2ignore.remove(background) # And we don't want to replace it by '0' (fuse or group all voxels coordinates to an "unlabelled" set of points)

        coord = {}
        neighbors_not_found = []
        for label_2 in neighbors:
            # -- Binary mask saying where the label_2 can be found on the image.
            mask_img_2 = (dilated_bbox_img == label_2)
            dil_2 = nd.binary_dilation(mask_img_2, structure=struct)
            # -- We now intersect the two dilated binary mask to find the voxels defining the contact area between two objects:
            x,y,z = np.where( ( (dil_1 & mask_img_2) | (dil_2 & mask_img_1) ) == 1 )
            if x != []:
                if label_2 not in neighbors2ignore:
                    coord[min(label_1,label_2),max(label_1,label_2)] = np.array((x+dilated_bbox[0].start, y+dilated_bbox[1].start, z+dilated_bbox[2].start))
                elif try_to_use_neighbors2ignore: # in case we want to ignore the specific position of some neighbors we replace its id by '0':
                    if are_these_labels_neighbors(neighbors2ignore, neighborhood): # we check that all neighbors to ignore are themself a set of connected neighbors!
                        if not coord.has_key((0,label_1)):
                            coord[(0,label_1)] = np.array((x+dilated_bbox[0].start, y+dilated_bbox[1].start, z+dilated_bbox[2].start))
                        else:
                            coord[(0,label_1)] = np.hstack( (coord[(0,label_1)], np.array((x+dilated_bbox[0].start, y+dilated_bbox[1].start, z+dilated_bbox[2].start))) )
                    #~ else:
                        #~ coord[(0,label_1)] = None
            else:
                if verbose:
                    print "Couldn't find a contact between neighbor cells {} and {}".format(label_1, label_2)
                neighbors_not_found.append(label_2)

        if neighbors_not_found:
            print "Some walls have not been found comparing to the `neighbors` list of {}: {}".format(label_1, neighbors_not_found)

        return coord


    def cells_walls_coords(self, hollow_out = True, verbose = True):
        """
        Return coordinates of the voxels belonging to the cell wall.

        .. warning :: Apply only to full 3D image, and not if only the first layer of voxel is provided (external envelope).

        :Parameters:
         - image (SpatialImage) - Segmented image (tissu)

        :Return:
         - x,y,z (list) - coordinates of the voxels defining the cell boundaries (walls).
        """
        if hollow_out:
            image = hollow_out_cells(self.image, self.background, verbose=verbose)
        else:
            image = copy.copy(self.image)
            image[np.where(image==self.background)] = 0

        if len(image.shape) == 3:
            x,y,z = np.where(image!=0)
            return list(x), list(y), list(z)

        if len(image.shape) == 2:
            x,y = np.where(image!=0)
            return list(x), list(y)


    def all_cell_vertex_extraction(self, hollow_out = True):
        """
        Calculates cell's vertices positions according to the rule: a vertex is the point where you can find 4 differents cells (in 3D!!)
        For the surface, the outer 'cell' #1 is considered as a cell.

        :Parameters:
         - image (SpatialImage) - Segmented image (tissu). Can be a full spatial image or an extracted surface.

        :Return:
         - barycentric_vtx (dict) -
                *keys = the 4 cells ids associated with the vertex position(values);
                *values = 3D coordinates of the vertex in the Spatial Image;
        """
        x, y, z = self.cells_walls_coords(hollow_out)
        ## Compute vertices positions by findind the voxel belonging to each vertex.
        vertex_voxel = {}; N = len(x); percent = 0
        for n in xrange(N):
            if n*100/N>=percent: print "{}%...".format(percent),; percent += 5
            if n+1==N: print "100%"
            i, j, k = x[n], y[n], z[n]
            sub_image = self.image[(i-1):(i+2),(j-1):(j+2),(k-1):(k+2)] # we extract a sub part of the matrix...
            sub_image = tuple(np.unique(sub_image))
            # -- Now we detect voxels defining cells' vertices.
            if ( len(sub_image) == 4 ): # ...in which we search for 4 different labels
                if vertex_voxel.has_key(sub_image):
                    vertex_voxel[sub_image] = np.vstack( (vertex_voxel[sub_image], np.array((i,j,k)).T) ) # we group voxels defining the same vertex by the IDs of the 4 cells.
                else:
                    vertex_voxel[sub_image] = np.ndarray((0,3))
        ## Compute the barycenter of the voxels associated to each vertex (correspondig to the 3 cells detected previously).
        barycentric_vtx = {}
        for i in vertex_voxel.keys():
            barycentric_vtx[i] = np.mean(vertex_voxel[i],0)
        
        print 'Done !!'
        return barycentric_vtx


    def cell_wall_area(self, label_id, neighbors, real = True):
        """
        Return the area of contact between a label and its neighbors.
        A list or a unique id can be given as neighbors.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.cell_wall_area(7,2)
        1.0
        >>> analysis.cell_wall_area(7,[2,5])
        {(2, 7): 1.0, (5, 7): 2.0}
        """

        resolution = self.get_voxel_face_surface()
        try:
            dilated_bbox =  dilation(self.boundingbox(label_id))
            dilated_bbox_img = self.image[dilated_bbox]
        except:
            #~ dilated_bbox = tuple( [slice(0,self.image.shape[i]-1) for i in xrange(len(self.image.shape))] ) #if no slice can be found we use the whole image
            dilated_bbox_img = self.image

        mask_img = (dilated_bbox_img == label_id)

        xyz_kernels = self.neighbor_kernels()

        unique_neighbor = not isinstance(neighbors,list)
        if unique_neighbor:
            neighbors = [neighbors]

        wall = {}
        for a in xrange(len(xyz_kernels)):
            dil = nd.binary_dilation(mask_img, structure=xyz_kernels[a])
            frontier = dilated_bbox_img[dil-mask_img]

            for n in neighbors:
                nb_pix = len(frontier[frontier==n])
                if real:  area = float(nb_pix*resolution[a//2])
                else : area = nb_pix
                i,j = min(label_id,n), max(label_id,n)
                wall[(i,j)] = wall.get((i,j),0.0) + area

        if unique_neighbor: return wall.itervalues().next()
        else : return wall


    def wall_areas(self, neighbors = None, real = True):
        """
        Return the area of contact between all neighbor labels.
        If neighbors is not given, it is computed first.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.wall_areas({ 1 : [2, 3], 2 : [6] })
       {(1, 2): 5.0, (1, 3): 4.0, (2, 6): 2.0 }

        >>> analysis.wall_areas()
        {(1, 2): 5.0, (1, 3): 4.0, (1, 4): 2.0, (1, 5): 1.0, (1, 6): 1.0, (1, 7): 2.0, (2, 6): 2.0, (2, 7): 1.0, (3, 7): 2, (4, 7): 1, (5, 6): 1.0, (5, 7): 2.0 }
        """
        if neighbors is None : neighbors = self.neighbors()
        areas = {}
        for label_id, lneighbors in neighbors.iteritems():
            # To avoid computing twice the same wall area, we select walls between i and j with j > i.
            neigh = [n for n in lneighbors if n > label_id]
            if len(neigh) > 0:
                lareas = self.cell_wall_area(label_id, neigh, real = real)
                for i,j in lareas.iterkeys():
                    areas[(i,j)] = areas.get((i,j),0.0) + lareas[(i,j)]
        return areas


    def cell_first_layer(self, filter_by_area = True, minimal_external_area=10, real_area=True):
        """
        Extract a list of labels corresponding to the external layer of cells.

        """
        integers = lambda l : map(int, l)
        if self._cell_layer1 is None : # _cell_layer1 contains always all the l1-cell labels.
            self._cell_layer1 = integers(self.neighbors(self.background()))
            if filter_by_area:
                vids_area = self.cell_wall_area(self.background(),self._cell_layer1, real_area)
                self._cell_layer1 = [vid for vid in self._cell_layer1 if ((vids_area.has_key(tuple([self.background(),vid]))) and (vids_area[(self.background(),vid)]>minimal_external_area))]

        self._cell_layer1 = list( set(self._cell_layer1)-self._ignoredlabels )
        return self._cell_layer1

    def cell_second_layer(self, filter_by_area = True, minimal_L1_area=10, real_area=True):
        """
        Extract a list of labels corresponding to the second layer of cells.
        """
        L1_neighbors=self.neighbors(self.cell_first_layer(),minimal_L1_area,real_area,True)
        l2 =set([])
        for nei in L1_neighbors.values():
            l2.update(nei)

        self._cell_layer2 = list(l2-set(self._cell_layer1)-self._ignoredlabels)
        return self._cell_layer2

    def __first_voxel_layer(self, keep_background = True):
        """
        Extract the first layer of voxels at the surface of the biological object.
        """
        print "Extracting the first layer of voxels..."
        mask_img_1 = (self.image == self.background())
        struct = nd.generate_binary_structure(3, 1)
        dil_1 = nd.binary_dilation(mask_img_1, structure=struct)

        layer = dil_1 - mask_img_1

        if keep_background:
            return self.image * layer + mask_img_1
        else:
            return self.image * layer

    def voxel_first_layer(self, keep_background = True):
        """
        Function extracting the first layer of voxels detectable from the outer surface.
        """
        if self._voxel_layer1 is None :
            self._voxel_layer1 = self.__first_voxel_layer(keep_background)
        return self._voxel_layer1


    def wall_voxels_per_cells_pairs(self, labels=None, neighborhood=None, only_epidermis=False, ignore_background=False, min_contact_area=None, real_area=True):
        """
        Extract the coordinates of voxels defining the 'wall' between a pair of labels.
        :WARNING: if dimensionality = 2, only the cells belonging to the outer layer of the object will be used.

        :Parameters:
         - `labels` (int|list) - label or list of labels to extract walls coordinate with its neighbors.
         - `neighborhood` (list|dict) - list of neighbors of label if isinstance(labels,int), if not neighborhood should be a dictionary of neighbors by labels.
         - `only_epidermis` (bool) - indicate if we work with the whole image or just the first layer of voxels (epidermis).
         - `ignore_background` (bool) - indicate whether we want to return the coordinate of the voxels defining the 'epidermis wall' (in contact with self.background()) or not.
         - `min_contact_area` (None|int|float) - value of the min contact area threshold.
         - `real_area` (bool) - indicate wheter the min contact surface is a real world value or a number of voxels.
        """
        if only_epidermis:
            image = self.first_voxel_layer(True)
        else:
            image = self.image

        compute_neighborhood=False
        if neighborhood is None:
            compute_neighborhood=True
        if isinstance(labels,list) and isinstance(neighborhood,dict):
            labels = [label for label in labels if neighborhood.has_key(label)]

        if labels is None and not only_epidermis:
            labels=self.labels()
        elif labels is None and only_epidermis:
            labels=np.unique(image)
        elif isinstance(labels,list):
            labels.sort()
            if not isinstance(neighborhood,dict):
                compute_neighborhood=True
        elif isinstance(labels,int):
            labels = [labels]
        else:
            raise ValueError("Couldn't find any labels.")

        dict_wall_voxels = {}
        for label in labels:
            # - We compute or use the neighborhood of `label`:
            if compute_neighborhood:
                neighbors = self.neighbors(label, min_contact_area, real_area)
            else:
                if isinstance(neighborhood,dict):
                    neighbors = copy.copy( neighborhood[label] )
                if isinstance(neighborhood,list):
                    neighbors = neighborhood
            # - We create a list of neighbors to ignore:
            if ignore_background:
                neighbors2ignore = [ n for n in neighbors if n not in labels ]
            else:
                neighbors2ignore = [ n for n in neighbors if n not in labels+[self.background()] ]
            # - We remove the couples of labels from wich the "wall voxels" are already extracted:
            for nei in neighbors:
                if dict_wall_voxels.has_key( (min(label,nei),max(label,nei)) ):
                    neighbors.remove(nei)
            # - If there are neighbors left in the list, we extract the "wall voxels" between them and `label`:
            if neighbors != []:
                dict_wall_voxels.update(walls_voxels_per_cell(image, label, self.boundingbox(label), neighbors, neighbors2ignore, self.background()))

        return dict_wall_voxels


    def wall_orientation(self, dict_wall_voxels, fitting_degree = 2, plane_projection = False, dict_coord_points_ori = None):
        """
        Compute wall orientation according to fitting degree and dimensionality.
        :WARNING: if plane_projection, voxels will projected on a plane according to a least square regression (made here by a base projection from a SVD)

        :Parameters:
         - `dict_wall_voxels` (dict) - dictionary of voxels to be fitted by a surface (*keys = couple of neighbor labels; *values = set of coordinates)
         - `fitting_degree` (int) - number of 'curvature' (local differential properties) allowed for the fitted surface.
         - `plane_projection` (bool) - if True, the voxels coordinates will projected on a plane according to a least square regression.
         - `dict_coord_points_ori` (None|dict) - dictionary of coordinate defining the origin point where to fit the surface. If None, will be computed as the geometric median of the point set.
        """
        from openalea.plantgl.all import principal_curvatures
        integers = np.vectorize(lambda x : int(x))

        pc_values, pc_normal, pc_directions, pc_origin = {},{},{},{}
        ## For each 3D points (*keys = couple of neighbor labels) set of coordinates (defining a wall), we will fit a "plane":
        for label_1, label_2 in dict_wall_voxels:
            if dict_wall_voxels[(label_1, label_2)] == None:
                if label_1 != 0:
                    print "There might be something wrong between cells %d and %d" %label_1  %label_2
                continue # if None, means no points to estimate wall orientation !!
            x, y, z = dict_wall_voxels[(label_1, label_2)] # the points set
            if plane_projection:
                fitting_degree = 0 #there will be no curvature since the wall will be flatenned !
                x_bar, y_bar, z_bar = np.mean(dict_wall_voxels[(label_1, label_2)],axis=1)
                centered_point_set_3D = np.array( [x-x_bar,y-y_bar,z-z_bar] )
                U, S, V = np.linalg.svd(centered_point_set_3D.T, full_matrices=False)
                proj_points = np.dot(centered_point_set_3D.T, np.dot(V[:2,:].T,V[:2,:]))
                x,y,z = proj_points[:,0]+x_bar, proj_points[:,1]+y_bar, proj_points[:,2]+z_bar
            ## We need to find an origin: the closest point in set set from the geometric median
            if (dict_coord_points_ori is not None) and dict_coord_points_ori.has_key((label_1, label_2)):
                closest_voxel_coords = dict_coord_points_ori[(label_1, label_2)]
            else:
                closest_voxel_coords = find_wall_median_voxel( {(label_1, label_2):dict_wall_voxels[(label_1, label_2)]}, verbose=False)

            pts = [tuple([int(x[i]),int(y[i]),int(z[i])]) for i in xrange(len(x))]
            id_min_dist = pts.index(tuple(closest_voxel_coords))
            ## We can now compute the curvature values, direction, normal and origin (Monge):
            pc = principal_curvatures(pts, id_min_dist, range(len(x)), fitting_degree, 2)
            pc_values[(label_1, label_2)] = [pc[1][1], pc[2][1]]
            pc_normal[(label_1, label_2)] = pc[3]
            pc_directions[(label_1, label_2)] = [pc[1][0], pc[2][0]]
            pc_origin[(label_1, label_2)] = pc[0]

        if len(dict_wall_voxels)==1:
            return pc_values.values()[0], pc_normal.values()[0], pc_directions.values()[0], pc_origin.values()[0]
        else:
            return pc_values, pc_normal, pc_directions, pc_origin


    def inertia_axis_normal_to_surface(self, labels=None, inertia_axis=None, real=False, verbose=True):
        """
        Find the inertia axis defining the "Z" orientation of the cell.
        We define it to be the one correlated to the normal vector to the surface.

        :Parameters:
         - `labels` (int) - single label number or a sequence of label numbers of the objects to be measured.
            If labels is None, all labels are used.
         - `real` (bool) - If real = True, center of mass is in real-world units else in voxels.
        """

        # -- If 'labels' is `None`, we apply the function to all L1 cells:
        if labels == None:
            labels = self.cell_first_layer()
        else:
            tmp_labels = [label for label in labels if label in self.cell_first_layer()]
            diff = set(labels)-set(tmp_labels)
            if diff != set([]):
                labels=tmp_labels
                print "Some of the provided `labels` does not belong to the L1."
                if verbose:
                    print "Unused labels: {}".format(diff)

        # -- If 'inertia_axis' is `None`, we compute them:
        if inertia_axis == None:
            inertia_axis, inertia_length = self.inertia_axis(labels, real=real)

        surface_normal_axis=[]; N = len(labels); percent = 0
        for n_cell, cell in enumerate(labels):
            if verbose and n_cell*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and n+1==N: print "100%"
            try:
                normal = self.principal_curvatures_normal[cell]
            except:
                self.compute_principal_curvatures( cell, radius=30, fitting_degree=1, monge_degree=2, verbose=False)
                normal = self.principal_curvatures_normal[cell]
            max_corr = 0
            n_corr = 3
            for n_vect,inertia_vect in enumerate(inertia_axis[cell]):
                corr = vector_correlation(normal, inertia_vect)
                if abs(corr)>max_corr:
                    max_corr=copy.copy(abs(corr))
                    n_corr=copy.copy(n_vect)

            surface_normal_axis.append(n_corr)

        return self.convert_return(surface_normal_axis, labels)


    def remove_cells(self, vids, erase_value = 0, verbose = True):
        """
        Use remove_cell to iterate over a list of cell to remove if there is more cells to keep than to remove.
        If there is more cells to remove than to keep, we fill a "blank" image with those to keep.
        :!!!!WARNING!!!!:
        This function modify the SpatialImage on self.image
        :!!!!WARNING!!!!:
        """

        if isinstance(vids,int):
            vids= [vids]

        if (len(vids)!=1) and (self.background() in vids) :
            vids.remove(self.background())

        assert isinstance(vids,list)

        N=len(vids); percent = 0
        if verbose: print "Removing", N, "cells."
        for n, vid in enumerate(vids):
            if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 5
            if verbose and n+1==N: print "100%"
            try:
                xyz = np.where( (self.image[self.boundingbox(vid)]) == vid )
                self.image[tuple((xyz[0]+self.boundingbox(vid)[0].start, xyz[1]+self.boundingbox(vid)[1].start, xyz[2]+self.boundingbox(vid)[2].start))]=erase_value
            except:
                print "No boundingbox found for cell id #{}, skipping...".format(vid)
                continue
        ignoredlabels = copy.copy(self._ignoredlabels)
        ignoredlabels.update([erase_value])
        return_type = copy.copy(self.return_type)
        self.__init__(self.image, ignoredlabels, return_type)

        if verbose: print 'Done !!'


    def remove_margins_cells(self, erase_value = 0, verbose = False):
        """
        :!!!!WARNING!!!!:
        This function modify the SpatialImage on self.image
        :!!!!WARNING!!!!:
        Function removing cells at the margins, because most probably cut during stack aquisition.

        :INPUTS:
            .save: text (if present) indicating under which name to save the Spatial Image containing the cells of the first layer;
            .display: boolean indicating if we should display the previously computed image;

        :OUPUT:
            Spatial Image without the cell's at the margins.
        """

        if verbose: print "Removing cells at the margins of the stack..."

        # -- We start by making sure that there is not only one cell in the image (appart from 0 and 1)
        labels = copy.copy(list(self.labels()))
        if 0 in labels: labels.remove(0)
        if self.background() in labels: labels.remove(self.background())
        if len(labels)==1:
            warnings.warn("Only one cell left in your image, we won't take it out !")
            return self.__init__(self.image)

        # -- Then we recover the list of border cells and delete the from the image:
        cells_in_image_margins = self.cells_in_image_margins()
        if erase_value in cells_in_image_margins: cells_in_image_margins.remove(erase_value)

        N = len(cells_in_image_margins); percent= 0
        for n,c in enumerate(cells_in_image_margins):
            if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and n+1==N: print "100%"
            try:
                xyz = np.where( (self.image[self.boundingbox(c)]) == c )
                self.image[tuple((xyz[0]+self.boundingbox(c)[0].start,xyz[1]+self.boundingbox(c)[1].start,xyz[2]+self.boundingbox(c)[2].start))]=erase_value
            except:
                print "No boundingbox found for cell id #{}, skipping...".format(vid)
                continue

        ignoredlabels = copy.copy(self._ignoredlabels)
        ignoredlabels.update([erase_value])
        return_type = copy.copy(self.return_type)
        self.__init__(self.image, ignoredlabels, return_type, self._background)
        self._erase_value = erase_value

        if verbose: print 'Done !!'


class SpatialImageAnalysis2D (AbstractSpatialImageAnalysis):
    """
    Class dedicated to 2D objects.
    """

    def __init__(self, image, ignoredlabels = [], return_type = DICT, background = None):
        AbstractSpatialImageAnalysis.__init__(self, image, ignoredlabels, return_type, background)


    def cells_in_image_margins(self):
        """
        Return a list of cells in contact with the margins of the stack (SpatialImage).
        """
        margins = []
        margins.extend(np.unique(self.image[0,:]))
        margins.extend(np.unique(self.image[-1,:]))
        margins.extend(np.unique(self.image[:,0]))
        margins.extend(np.unique(self.image[:,-1]))

        return list(set(margins)-set([self._background]))


    def inertia_axis(self, labels = None, center_of_mass = None, real = True):
        """
        Return the inertia axis of cells, also called the shape main axis.
        Returns 2 (2D-oriented) vectors and 2 (length) values.
        """
        if labels is None: labels = self.labels()
        else: labels = [labels]

        # results
        inertia_eig_vec = []
        inertia_eig_val = []
        for i,label in enumerate(labels):
            if verbose and i*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and i+1==N: print "100%"
            slices = self.boundingbox(label, real=False)
            center = copy.copy(self.center_of_mass(label, real=False))
            # project center into the slices sub_image coordinate
            if slices is not None:
                for i,slice in enumerate(slices):
                    center[i] = center[i] - slice.start
                label_image = (self.image[slices] == label)
            else:
                print 'No boundingbox found for label {}'.format(label)
                label_image = (self.image == label)

            # compute the indices of voxel with adequate label
            x,y,z = label_image.nonzero()
            if len(x)==0:
                continue # obviously no reasons to go further !
            # difference with the center
            x = x - center[0]
            y = y - center[1]
            z = z - center[2]
            coord = np.array([x,y,z])

            # compute 1/N*P.P^T
            cov = 1./len(x)*np.dot(coord,coord.T)

            # Find the eigen values and vectors.
            eig_val, eig_vec = np.linalg.eig(cov)
            eig_vec = np.array(eig_vec).T

            if real:
                for i in xrange(2):
                    eig_val[i] *= np.linalg.norm( np.multiply(eig_vec[i],self._voxelsize) )

            inertia_eig_vec.append(eig_vec)
            inertia_eig_val.append(eig_val)

        if len(labels)==1 :
            return return_list_of_vectors(inertia_eig_vec[0],by_row=1), inertia_eig_val[0]
        else:
            return self.convert_return(return_list_of_vectors(inertia_eig_vec,by_row=1),labels), self.convert_return(inertia_eig_val,labels)



class SpatialImageAnalysis3DS (AbstractSpatialImageAnalysis):
    """
    Class dedicated to surfacic 3D objects.
    Only one layer of voxel is extracted (representing the external envelope of the biological object to analyse).
    """

    def __init__(self, image, ignoredlabels = [], return_type = DICT, background = None):
        AbstractSpatialImageAnalysis.__init__(self, image, ignoredlabels, return_type, background)



class SpatialImageAnalysis3D(AbstractSpatialImageAnalysis):
    """
    Class dedicated to 3D objects.
    """

    def __init__(self, image, ignoredlabels = [], return_type = DICT, background = None):
        AbstractSpatialImageAnalysis.__init__(self, image, ignoredlabels, return_type, background)
        self._voxel_layer1 = None
        self.principal_curvatures = {}
        self.principal_curvatures_normal = {}
        self.principal_curvatures_directions = {}
        self.principal_curvatures_origin = {}
        self.curvatures_tensor = {}
        self.external_wall_geometric_median = {}
        self.epidermis_wall_median_voxel = {}

    def is3D(self): return True

    def volume(self, labels = None, real = True):
        """
        Return the volume of the labels.

        :Parameters:
         - `labels` (int) - single label number or a sequence of
            label numbers of the objects to be measured.
            If labels is None, all labels are used.

         - `real` (bool) - If real = True, volume is in real-world units else in voxels.

        :Examples:

        >>> import numpy as np
        >>> a = np.array([[1, 2, 7, 7, 1, 1],
                          [1, 6, 5, 7, 3, 3],
                          [2, 2, 1, 7, 3, 3],
                          [1, 1, 1, 4, 1, 1]])

        >>> from openalea.image.algo.analysis import SpatialImageAnalysis
        >>> analysis = SpatialImageAnalysis(a)

        >>> analysis.volume(7)
        4.0

        >>> analysis.volume([7,2])
        [4.0, 3.0]

        >>> analysis.volume()
        [10.0, 3.0, 4.0, 1.0, 1.0, 1.0, 4.0]
        """
        # Check the provided `labels`:
        labels = self.label_request(labels)

        volume = nd.sum(np.ones_like(self.image), self.image, index=np.int16(labels))
        # convert to real-world units if asked:
        if real is True:
            if self.image.ndim == 2:
                volume = np.multiply(volume,(self._voxelsize[0]*self._voxelsize[1]))
            elif self.image.ndim == 3:
                volume = np.multiply(volume,(self._voxelsize[0]*self._voxelsize[1]*self._voxelsize[2]))
            volume.tolist()

        if not isinstance(labels, int):
            return self.convert_return(volume, labels)
        else:
            return volume


    def inertia_axis(self, labels = None, real = True, verbose=False):
        """
        Return the inertia axis of cells, also called the shape main axis.
        Return 3 (3D-oriented) vectors by rows and 3 (length) values.
        """
        # Check the provided `labels`:
        labels = self.label_request(labels)

        # results
        inertia_eig_vec = []
        inertia_eig_val = []
        N = len(labels); percent=0
        for i,label in enumerate(labels):
            if verbose and i*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and i+1==N: print "100%"
            slices = self.boundingbox(label, real=False)
            center = copy.copy(self.center_of_mass(label, real=False))
            # project center into the slices sub_image coordinate
            if slices is not None:
                for i,slice in enumerate(slices):
                    center[i] = center[i] - slice.start
                label_image = (self.image[slices] == label)
            else:
                print 'No boundingbox found for label {}'.format(label)
                label_image = (self.image == label)

            # compute the indices of voxel with adequate label
            xyz = label_image.nonzero()
            if len(x)==0:
                continue # obviously no reasons to go further !
            coord = coordinates_centering3D(xyz)
            # compute the variance-covariance matrix (1/N*P.P^T):
            cov = compute_covariance_matrix(coord)
            # Find the eigen values and vectors.
            eig_val, eig_vec = eigen_values_vectors(cov)
            # convert to real-world units if asked:
            if real:
                for i in xrange(3):
                    eig_val[i] *= np.linalg.norm( np.multiply(eig_vec[i],self._voxelsize) )

            inertia_eig_vec.append(eig_vec)
            inertia_eig_val.append(eig_val)

        if len(labels)==1 :
            return return_list_of_vectors(inertia_eig_vec[0]), inertia_eig_val[0]
        else:
            return self.convert_return(return_list_of_vectors(inertia_eig_vec),labels), self.convert_return(inertia_eig_val,labels)


    def reduced_inertia_axis(self, labels = None, real = True, verbose=False):
        """
        Return the REDUCED (centered coordinates standardized) inertia axis of cells, also called the shape main axis.
        Return 3 (3D-oriented) vectors by rows and 3 (length) values.
        """
        # Check the provided `labels`:
        labels = self.label_request(labels)

        # results
        inertia_eig_vec = []
        inertia_eig_val = []
        N = len(labels); percent=0
        for i,label in enumerate(labels):
            if verbose and i*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and i+1==N: print "100%"
            slices = self.boundingbox(label, real=False)
            center = copy.copy(self.center_of_mass(label, real=False))
            # project center into the slices sub_image coordinate
            if slices is not None:
                for i,slice in enumerate(slices):
                    center[i] = center[i] - slice.start
                label_image = (self.image[slices] == label)
            else:
                print 'No boundingbox found for label {}'.format(label)
                label_image = (self.image == label)

            # compute the indices of voxel with adequate label
            xyz = label_image.nonzero()
            if len(x)==0:
                continue # obviously no reasons to go further !
            coord = coordinates_centering3D(xyz)
            # compute the variance-covariance matrix (1/N*P.P^T):
            cov = compute_covariance_matrix(coord)
            # Find the eigen values and vectors.
            eig_val, eig_vec = eigen_values_vectors(cov)
            # convert to real-world units if asked:
            if real:
                for i in xrange(3):
                    eig_val[i] *= np.linalg.norm( np.multiply(eig_vec[i],self._voxelsize) )

            inertia_eig_vec.append(eig_vec)
            inertia_eig_val.append(eig_val)

        if len(labels)==1 :
            return return_list_of_vectors(inertia_eig_vec[0],by_row=1), inertia_eig_val[0]
        else:
            return self.convert_return(return_list_of_vectors(inertia_eig_vec,by_row=1),labels), self.convert_return(inertia_eig_val,labels)


    def epidermal_walls_shape_anisotropy(self, vids=None, real=False, flatten=False, verbose=False):
        """
        Compute anisotropy of epidermis cell from inertia axis length.
        Based on the first layer of voxels only!!

        :Parameters:
         - vids (list): list of ids.
         - real (bool): if True, return the eigenvalues in real world units.
        """
        first_voxel_layer = self.first_voxel_layer(keep_background=True)
        # Check the provided `labels`:
        labels = self.label_request(labels)

        anisotropy = []; N=len(vids); percent=0
        for n,label in enumerate(vids):
            if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and n+1==N: print "100%"
            # compute the indices of voxel with adequate label
            xyz = np.array(np.where(first_voxel_layer[self.boundingbox(label)] == label))
            if len(x)==0:
                continue # obviously no reasons to go further !
            # difference with the center
            coord = coordinates_centering3D(xyz)
            # compute the variance-covariance matrix (1/N*P.P^T):
            cov = compute_covariance_matrix(coord)
            # Find the eigen values and vectors.
            eig_val, eig_vec = eigen_values_vectors(cov)
            # convert to real-world units if asked:
            if real:
                for i in xrange(3):
                    eig_val[i] *= np.linalg.norm( np.multiply(eig_vec[i],self._voxelsize) )
            #Now compute the anisotropy as (v0-v1) / (v0+v1)
            anisotropy.append( (eig_val[0]-eig_val[1]) / (eig_val[0]+eig_val[1]) )

        return self.convert_return(anisotropy, vids)


    def cells_in_image_margins(self, voxel_distance_from_margin=5):
        """
        Return a list of cells in contact with the margins of the stack (SpatialImage).
        All ids within a defined (5 by default) voxel distance form the margins will be used to define cells as 'in image margins'.
        """
        vx_dist=voxel_distance_from_margin
        margins = []
        margins.extend(np.unique(self.image[:vx_dist,:,:]))
        margins.extend(np.unique(self.image[-vx_dist:,:,:]))
        margins.extend(np.unique(self.image[:,:vx_dist,:]))
        margins.extend(np.unique(self.image[:,-vx_dist:,:]))
        margins.extend(np.unique(self.image[:,:,:vx_dist]))
        margins.extend(np.unique(self.image[:,:,-vx_dist:]))

        return list(set(margins)-set([self._background]))


    def region_boundingbox(self, labels):
        """
        This function return a boundingbox of a region including all cells (provided by `labels`).

        :Parameters:
         - `labels` (list): list of cells ids;
        :Returns:
         - [x_start,y_start,z_start,x_stop,y_stop,z_stop]
        """
        if isinstance(labels,list) and len(labels) == 1:
            return self.boundingbox(labels[0])
        if isinstance(labels,int):
            return self.boundingbox(labels)

        dict_slices = self.boundingbox(labels)
        #-- We start by making sure that all cells have an entry (key) in `dict_slices`:
        not_found=[]
        for c in labels:
            if c not in dict_slices.keys():
                not_found.append(c)
        if len(not_found)!=0:
            warnings.warn('You have asked for unknown cells labels: '+" ".join([str(k) for k in not_found]))

        #-- We now define a slice for the region including all cells:
        x_start,y_start,z_start,x_stop,y_stop,z_stop=np.inf,np.inf,np.inf,0,0,0
        for c in labels:
            x,y,z=dict_slices[c]
            x_start=min(x.start,x_start)
            y_start=min(y.start,y_start)
            z_start=min(z.start,z_start)
            x_stop=max(x.stop,x_stop)
            y_stop=max(y.stop,y_stop)
            z_stop=max(z.stop,z_stop)

        return [x_start,y_start,z_start,x_stop,y_stop,z_stop]


    def __principal_curvature_parameters_CGAL(func):
        def wrapped_function(self, vids = None, radius = 70, fitting_degree = 2, monge_degree = 2, verbose = False):
            """
            Decorator wrapping function `compute_principal_curvatures` allowing use of various input for `vids` and preparing the necessary variables for the wrapped function.
            """
            from openalea.plantgl.algo import k_closest_points_from_ann
            # -- If 'vids' is an integer...
            if isinstance(vids,int):
                if (vids not in self.cell_first_layer()): # - ...but not in the L1 list, there is nothing to do!
                    warnings.warn("Cell "+str(vids)+" is not in the L1. We won't compute its curvature.")
                    return 0
                else: # - ... and in the L1 list, we make it iterable.
                    vids=[vids]

            # -- If 'vids' is a list, we make sure to keep only its 'vid' present in the L1 list!
            if isinstance(vids,list):
                tmp = copy.deepcopy(vids) # Ensure to scan all the elements of 'vids'
                no_curvature = [vid for vid in tmp if vid not in self.cell_first_layer()]
                if no_curvature != []:
                    warnings.warn("Cells {} are not in the L1. We won't compute their curvature.")
                    vids = list(set(vids)-set(no_curvature))
                if len(vids) == 0: # if there is no element left in the 'vids' list, there is nothing to do!
                    warnings.warn('None of the cells you provided belong to the L1.')
                    return 0

            # -- If 'vids' is `None`, we apply the function to all L1 cells:
            if vids == None:
                vids = self.cell_first_layer()

            # -- Now we need the SpatialImage of the first layer of voxels without the background.
            # - If the first layer of voxels has been extracted already, we make sure that we have exluded the background.
            if self._voxel_layer1 is not None and self.background() in self._voxel_layer1:
                self._voxel_layer1[self._voxel_layer1 == self.background()]=0
            else:
                self.first_voxel_layer(keep_background = False)

            # -- We make sure the radius hasn't been changed and if not defined, we save the value for further evaluation and information.
            try:
                self.used_radius_for_curvature
            except:
                self.used_radius_for_curvature = radius
                recalculate_all = True
            else:
                if self.used_radius_for_curvature == radius:
                    recalculate_all = False
                else:
                    self.used_radius_for_curvature = radius
                    recalculate_all = True

            # -- We create voxels adjacencies
            curvature={}
            x,y,z = np.where(self.first_voxel_layer() != 0)
            pts = [tuple([int(x[i]),int(y[i]),int(z[i])]) for i in xrange(len(x))]
            adjacencies = k_closest_points_from_ann(pts, k=20)

            # -- Now we can compute the principal curvatures informations
            from openalea.image.algo.analysis import geometric_median
            if verbose: print 'Computing curvature :'
            N = len(vids); percent = 0
            for n,vid in enumerate(vids):
                if (recalculate_all) or (not self.principal_curvatures.has_key(vid)) :
                    if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 5
                    if verbose and n+1==N: print "100%"
                    func( self, vid, pts, adjacencies, fitting_degree, monge_degree )

        return wrapped_function


    @__principal_curvature_parameters_CGAL
    def compute_principal_curvatures(self, vid, pts, adjacencies, fitting_degree, monge_degree):
        """
        Function computing principal curvature using a CGAL c++ wrapped function: 'principal_curvatures'.
        It's only doable for cells of the first layer.
        """
        from openalea.plantgl.algo import r_neighborhood, principal_curvatures
        # - Try to use the position of the closest voxel to the wall geometric median
        if self.epidermis_wall_median_voxel.has_key(vid):
            closest_voxel_coords = self.epidermis_wall_median_voxel[vid]
        else:
            # - Recover `vid` position in the image:
            bbox = self.boundingbox(vid)
            coord = np.where(self.first_voxel_layer()[bbox] == vid)
            x_vid, y_vid, z_vid = [coord[i] + slice.start for i,slice in enumerate(bbox)]
            # find the median voxel (more precisely, the closest voxel to the median)
            closest_voxel_coords = find_wall_median_voxel( {(1, vid): [x_vid, y_vid, z_vid]}, verbose=False)
            self.epidermis_wall_median_voxel[vid] = closest_voxel_coords

        id_min_dist = pts.index(tuple(closest_voxel_coords))
        neigborids = r_neighborhood(id_min_dist, pts, adjacencies, self.used_radius_for_curvature)
        # - Principal curvature computation:
        pc = principal_curvatures(pts, id_min_dist, neigborids, fitting_degree, monge_degree)
        self.principal_curvatures[vid] = pc[1][1], pc[2][1], 1.
        self.principal_curvatures_directions[vid] = return_list_of_vectors(np.array([pc[1][0], pc[2][0], pc[3][0]]),by_row=1)
        self.principal_curvatures_normal[vid] = self.principal_curvatures_directions[vid][2]
        self.principal_curvatures_origin[vid] = pc[0]
        #~ k1 = pc[1][1]; k2 = pc[2][1]
        #~ R = np.array( [pc[1][0], pc[2][0], pc[0]] ).T
        #~ D = [ [k1,0,0], [0,k2,0], [0,0,0] ]
        #~ self.curvatures_tensor[vid] = np.dot(np.dot(R,D),R.T)


    def __curvature_parameters_CGAL(func):
        def wrapped_function(self, vids = None, radius=70, verbose = False):
            """
            """
            # -- If 'vids' is `None`, we apply the function to all L1 cells:
            if vids == None:
                vids = self.cell_first_layer()

            # -- If 'vids' is an integer...
            if isinstance(vids,int):
                if (vids not in self.cell_first_layer()): # - ...but not in the L1 list, there is nothing to do!
                    warnings.warn("Cell"+str(vids)+"is not in the L1. We won't compute it's curvature.")
                    return 0
                else: # - ... and in the L1 list, we make it iterable.
                    vids=[vids]

            try:
                self.principal_curvatures
            except:
                print('Principal curvature not pre-computed... computing it !')
                self.compute_principal_curvatures(vids, radius=radius, verbose = True)

            curvature = {}; N = len(vids); percent=0
            for n,vid in enumerate(vids):
                if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
                if verbose and n+1==N: print "100%"
                if not self.principal_curvatures.has_key(vid):
                    c = self.compute_principal_curvatures(vid, radius = radius)
                else:
                    c = self.principal_curvatures[vid]
                if c != 0: # 'compute_principal_curvatures' return a 0 when one of the vids is not in the L1.
                    curvature[vid] = func( self, vid )

            return curvature
        return wrapped_function


    @__curvature_parameters_CGAL
    def gaussian_curvature_CGAL( self, vid ):
        """
        Gaussian curvature is the product of principal curvatures 'k1*k2'.
        """
        return self.principal_curvatures[vid][0] * self.principal_curvatures[vid][1]

    @__curvature_parameters_CGAL
    def mean_curvature_CGAL( self, vid ):
        """
        Mean curvature is the product of principal curvatures '1/2*(k1+k2)'.
        """
        return 0.5*(self.principal_curvatures[vid][0] + self.principal_curvatures[vid][1])

    @__curvature_parameters_CGAL
    def curvature_ratio_CGAL( self, vid ):
        """
        Curvature ratio is the ratio of principal curvatures 'k1/k2'.
        """
        return float(self.principal_curvatures[vid][0])/float(self.principal_curvatures[vid][1])

    @__curvature_parameters_CGAL
    def curvature_anisotropy_CGAL( self, vid ):
        """
        Curvature Anisotropy is defined as '(k1-k2)/(k1+k2)'.
        Where k1 is the max value of principal curvature and k2 the min value.
        """
        return float(self.principal_curvatures[vid][0] - self.principal_curvatures[vid][1])/float(self.principal_curvatures[vid][0] + self.principal_curvatures[vid][1])


    def moment_invariants(self, vids = None, order = [], verbose = True):
        """
        Computation of 3D invariant moment (invariant to translation, rotation and scale).

        2nd order moments are calculated from:
         - Sadjadi, F. A. & Hall, E. L. Three-Dimensional Moment Invariants. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1980, PAMI-2, 127-136.

        3rd and 4th order moments are calculated from:
         - Xu, D. & Li, H. Geometric moment invariants. Pattern Recognition, 2008, 41, 240-249
        """
        # -- If 'vids' is an integer...
        if isinstance(vids,int):
            vids=[vids]

        # -- If 'vids' is `None`, we apply the function to all L1 cells:
        if vids == None:
            vids = self.labels()

        central_moments = {}
        I1, I2, I3, I4, I5, I6 = {}, {}, {}, {}, {}, {}

        usefull_combinations = [ [4, 0, 0], [0, 4, 0], [0, 0, 4], [2, 2, 0], [2, 0, 2], [0, 2, 2], [0, 0, 0], \
        [1, 0, 3], [3, 0, 1], [1, 3, 0], [3, 1, 0], [0, 1, 3], [0, 3, 1], [1, 2, 1], \
        [1, 1, 2], [2, 1, 1], [3, 0, 0], [0, 3, 0], [0, 0, 3], [1, 2, 0], [1, 0, 2], \
        [0, 1, 2], [2, 1, 0], [0, 2, 1], [2, 0, 1], [1, 1, 1], [2, 0, 0], [0, 2, 0], \
        [0, 0, 2], [1, 1, 0], [1, 0, 1], [0, 1, 1] ]

        N=len(vids); percent=0
        for n,vid in enumerate(vids):
            if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and n+1==N: print "100%"
            x,y,z = np.where( (self.image[self.boundingbox(vid)]) == vid )
            x_mean,y_mean,z_mean = self.center_of_mass(vid,False)
            x_res, y_res, z_res = self._voxelsize

            x_bar = x+self.boundingbox(vid)[0].start-x_mean
            y_bar = y+self.boundingbox(vid)[1].start-y_mean
            z_bar = z+self.boundingbox(vid)[2].start-z_mean

            #~ for l in xrange(5):
                #~ for m in xrange(5):
                    #~ for n in xrange(5):
                        #~ central_moments[l,m,n] = sum( (x_bar*x_res)**l * (y_bar*y_res)**m * (z_bar*z_res)**n )
            for l, m, n in usefull_combinations:
                central_moments[l,m,n] = sum( (x_bar*x_res)**l * (y_bar*y_res)**m * (z_bar*z_res)**n )

            I1[vid] = ( 1/(central_moments[0,0,0])**(7/3) ) * \
             ( central_moments[4,0,0] + central_moments[0,4,0] + central_moments[0,0,4] + 2*central_moments[2,2,0] + 2*central_moments[2,0,2] + 2*central_moments[0,2,2] )

            I2[vid] = ( 1/(central_moments[0,0,0])**(14/3) ) * \
             ( central_moments[4,0,0]*central_moments[0,4,0] + central_moments[4,0,0]*central_moments[0,0,4] + central_moments[0,0,4]*central_moments[0,4,0] \
             + 3*central_moments[2,2,0]**2 + 3*central_moments[2,0,2]**2 + 3*central_moments[0,2,2]**2 \
             - 4*central_moments[1,0,3]*central_moments[3,0,1] - 4*central_moments[1,3,0]*central_moments[3,1,0] - 4*central_moments[0,1,3]*central_moments[0,3,1] \
             + 2*central_moments[0,2,2]*central_moments[2,0,2] + 2*central_moments[0,2,2]*central_moments[2,2,0] + 2*central_moments[2,2,0]*central_moments[2,0,2] \
             + 2*central_moments[0,2,2]*central_moments[4,0,0] + 2*central_moments[0,0,4]*central_moments[2,2,0] + 2*central_moments[0,4,0]*central_moments[2,0,2] \
             - 4*central_moments[1,0,3]*central_moments[1,2,1] - 4*central_moments[1,3,0]*central_moments[1,1,2] - 4*central_moments[0,1,3]*central_moments[2,1,1] \
             - 4*central_moments[1,2,1]*central_moments[3,0,1] - 4*central_moments[1,1,2]*central_moments[3,1,0] - 4*central_moments[2,1,1]*central_moments[0,3,1] \
             + 4*central_moments[2,1,1]**2 + 4*central_moments[1,1,2]**2 + 4*central_moments[1,2,1]**2 )

            I3[vid] = ( 1/(central_moments[0,0,0])**(14/3) ) * \
             ( central_moments[4,0,0]**2 + central_moments[0,4,0]**2 + central_moments[0,0,4]**2 \
             + 4*central_moments[1,3,0]**2 + 4*central_moments[1,0,3]**2 + 4*central_moments[0,1,3]**2 + 4*central_moments[0,3,1]**2 + 4*central_moments[3,0,1]**2 \
             + 4*central_moments[3,0,1]**2 + 6*central_moments[2,2,0]**2 + 6*central_moments[2,0,2]**2 \
             + 6*central_moments[0,2,2]**2 + 12*central_moments[1,1,2]**2 + 12*central_moments[1,2,1]**2 + 12*central_moments[2,1,1]**2 )

            I4[vid] = ( 1/(central_moments[0,0,0])**4 ) * \
             ( central_moments[3,0,0]**2 + central_moments[0,3,0]**2 + central_moments[0,0,3]**2 + 3*central_moments[1,2,0]**2 + 3*central_moments[1,0,2]**2 \
             + 3*central_moments[0,1,2]**2 + 3*central_moments[2,1,0]**2 + 3*central_moments[0,2,1]**2 + 3*central_moments[2,0,1]**2 + 6*central_moments[1,1,1]**2 )

            I5[vid] = ( 1/(central_moments[0,0,0])**4 ) * \
             ( central_moments[3,0,0]**2 + central_moments[0,3,0]**2 + central_moments[0,0,3]**2 + central_moments[1,2,0]**2 + central_moments[1,0,2]**2 + central_moments[0,1,2]**2 + central_moments[2,1,0]**2 \
             + central_moments[0,2,1]**2 + central_moments[2,0,1]**2 + 2*central_moments[3,0,0]*central_moments[1,2,0] \
             + 2*central_moments[3,0,0]*central_moments[1,0,2] + 2*central_moments[1,2,0]*central_moments[1,0,2] + 2*central_moments[0,0,3]*central_moments[2,0,1] \
             + 2*central_moments[0,0,3]*central_moments[0,2,1] + 2*central_moments[0,2,1]*central_moments[2,0,1] + 2*central_moments[0,3,0]*central_moments[0,1,2] \
             + 2*central_moments[0,3,0]*central_moments[2,1,0] + 2*central_moments[0,1,2]*central_moments[2,1,0] )

            I6[vid] = ( 1/(central_moments[0,0,0])**4 ) * \
             ( central_moments[2,0,0]*(central_moments[4,0,0] + central_moments[2,2,0] + central_moments[2,0,2]) \
             + central_moments[0,2,0]*(central_moments[2,2,0] + central_moments[0,4,0] + central_moments[0,2,2]) \
             + central_moments[0,0,2]*(central_moments[2,0,2] + central_moments[0,2,2] + central_moments[0,0,4]) \
             + 2*central_moments[1,1,0]*(central_moments[3,1,0] + central_moments[1,3,0] + central_moments[1,1,2]) \
             + 2*central_moments[1,0,1]*(central_moments[3,0,1] + central_moments[1,2,1] + central_moments[1,0,3]) \
             + 2*central_moments[0,1,1]*(central_moments[2,1,1] + central_moments[0,3,1] + central_moments[0,1,3]) )

        return I1, I2, I3, I4, I5, I6


def outliers_exclusion( data, std_multiplier = 3, display_data_plot = False):
    """
    Return a list or a dict (same type as `data`) cleaned out of outliers.
    Outliers are detected according to a distance from standard deviation.
    """
    from numpy import std,mean
    tmp = copy.deepcopy(data)
    if isinstance(data,list):
        borne = mean(tmp) + std_multiplier*std(tmp)
        N = len(tmp)
        n=0
        while n < N:
            if (tmp[n]>borne) or (tmp[n]<-borne):
                tmp.pop(n)
                N = len(tmp)
            else:
                n+=1
    if isinstance(data,dict):
        borne = mean(tmp.values()) + std_multiplier*std(tmp.values())
        for n in data:
            if (tmp[n]>borne) or (tmp[n]<-borne):
                tmp.pop(n)
    if display_data_plot:
        import matplotlib.pyplot as plt
        if isinstance(data,list):
            plt.plot( data )
            plt.plot( tmp )
        plt.show()
        if isinstance(data,dict):
            plt.plot( data.values() )
            plt.plot( tmp.values() )
        plt.show()
    return tmp


def vector_correlation(vect1,vect2):
    """
    Compute correlation between two vector, which is the the cosine of the angle between two vectors in Euclidean space of any number of dimensions.
    The dot product is directly related to the cosine of the angle between two vectors if they are normed !!!
    """
    # -- We make sure that we have normed vectors.
    from numpy.linalg import norm
    if (np.round(norm(vect1)) != 1.):
        vect1 = vect1/norm(vect1)
    if (np.round(norm(vect2)) != 1.):
        vect2 = vect2/norm(vect2)

    return np.round(np.dot(vect1,vect2),3)


def find_wall_median_voxel(dict_wall_voxels, labels2exclude = [], verbose = True):
    """
    """
    from numpy import ndarray

    if isinstance(labels2exclude,int):
        labels2exclude = [labels2exclude]

    if isinstance(dict_wall_voxels, dict):
        wall_median = {}; N = len(dict_wall_voxels); percent = 0
        for n,(label_1, label_2) in enumerate(dict_wall_voxels):
            if verbose and n*100/float(N) >= percent: print "{}%...".format(percent),; percent += 10
            if verbose and n+1==N: print "100%"
            if label_1 in labels2exclude or label_2 in labels2exclude:
                continue
            xyz = np.array(dict_wall_voxels[(label_1, label_2)])
            if xyz.shape[0] == 3:
                xyz = xyz.T
            median_vox_id = _find_wall_median_voxel(xyz)
            wall_median[(label_1, label_2)] = xyz[median_vox_id]

        if len(dict_wall_voxels) == 1:
            return wall_median.values()[0]
        else:
            return wall_median

    if isinstance(dict_wall_voxels, ndarray):
        xyz = dict_wall_voxels
        if xyz.shape[0] == 3:
            xyz = np.array(xyz).T
        median_vox_id = _find_wall_median_voxel(xyz)

        return xyz[median_vox_id]
    else:
        return "Failed to recognise the type of data."

def _find_wall_median_voxel(array):
    """
    """
    from openalea.plantgl.math import Vector3
    from openalea.plantgl.algo import approx_pointset_median, pointset_median
    # Need an array with 3D coordinates as rows:
    if array.shape[0] == 3:
        xyz = np.array(array).T
    else:
        xyz = np.array(array)
    # Coordinates `Vector3` conversion:
    xyz = [Vector3(list([float(i) for i in k])) for k in xyz]
    # Compute geometric median:
    if len(xyz) <= 100:
        median_vox_id = pointset_median( xyz )
    else:
        median_vox_id = approx_pointset_median( xyz )

    return median_vox_id


def geometric_median(X, numIter = 200):
    """
    Compute the geometric median of a point sample.
    The geometric median coordinates will be expressed in the Spatial Image reference system (not in real world metrics).
    We use the Weiszfeld's algorithm (http://en.wikipedia.org/wiki/Geometric_median)

    :Parameters:
     - `X` (list|np.array) - voxels coordinate (3xN matrix)
     - `numIter` (int) - limit the length of the search for global optimum

    :Return:
     - np.array((x,y,z)): geometric median of the coordinates;
    """
    # -- Initialising 'median' to the centroid
    y = np.mean(X,1)
    # -- If the init point is in the set of points, we shift it:
    while (y[0] in X[0]) and (y[1] in X[1]) and (y[2] in X[2]):
        y+=0.1

    convergence=False # boolean testing the convergence toward a global optimum
    dist=[] # list recording the distance evolution

    # -- Minimizing the sum of the squares of the distances between each points in 'X' and the median.
    i=0
    while ( (not convergence) and (i < numIter) ):
        num_x, num_y, num_z = 0.0, 0.0, 0.0
        denum = 0.0
        m = X.shape[1]
        d = 0
        for j in range(0,m):
            div = math.sqrt( (X[0,j]-y[0])**2 + (X[1,j]-y[1])**2 + (X[2,j]-y[2])**2 )
            num_x += X[0,j] / div
            num_y += X[1,j] / div
            num_z += X[2,j] / div
            denum += 1./div
            d += div**2 # distance (to the median) to miminize
        dist.append(d) # update of the distance evolution

        if denum == 0.:
            warnings.warn( "Couldn't compute a geometric median, please check your data!" )
            return [0,0,0]

        y = [num_x/denum, num_y/denum, num_z/denum] # update to the new value of the median
        if i > 3:
            convergence=(abs(dist[i]-dist[i-2])<0.1) # we test the convergence over three steps for stability
            #~ print abs(dist[i]-dist[i-2]), convergence
        i += 1
    if i == numIter:
        raise ValueError( "The Weiszfeld's algoritm did not converged after"+str(numIter)+"iterations !!!!!!!!!" )
    # -- When convergence or iterations limit is reached we assume that we found the median.

    return np.array(y)


def are_these_labels_neighbors(labels, neighborhood):
    """
    This function allows you to make sure the provided labels are all connected neighbors according to a known neighborhood.
    """
    intersection=set()
    for label in labels:
        try:
            inter = set(neighborhood[label])&set(labels) # it's possible that `neighborhood` does not have key `label`
        except:
            inter = set()
        if inter == set(labels)-set([label]):
            return True
        if inter != set():
            intersection.update(inter)

    if intersection == set(labels):
        return True
    else:
        return False


def SpatialImageAnalysis(image, *args, **kwd):
    """
    Constructeur. Detect automatically if the image is 2D or 3D.
    """
    #~ print args, kwd
    assert len(image.shape) in [2,3]

    # -- Check if the image is 2D
    if len(image.shape) == 2 or image.shape[2] == 1:
        return SpatialImageAnalysis2D(image, *args, **kwd)
    # -- Else it's considered as a 3D image.
    else:
        return SpatialImageAnalysis3D(image, *args, **kwd)


def read_id_list( filename, sep='\n' ):
    """
    Read a *.txt file containing a list of ids separated by `sep`.
    """
    f = open(filename, 'r')
    r = f.read()

    k = r.split(sep)

    list_cell = []
    for c in k:
        if c != '':
            list_cell.append(int(c))

    return list_cell


def save_id_list(id_list, filename, sep='\n' ):
    """
    Read a *.txt file containing a list of ids separated by `sep`.
    """
    f = open(filename, 'w')
    for k in id_list:
        f.write(str(k))
        f.write(sep)

    f.close()


def projection_matrix(point_set, subspace_rank = 2):
    """
    Compute the projection matrix of a set of point depending on the subspace rank.

    :Parameters:
     - point_set (np.array): list of coordinates of shape (n_point, init_dim).
     - dimension_reduction (int) : the dimension reduction to apply
    """
    point_set = np.array(point_set)
    nb_coord = point_set.shape[0]
    init_dim = point_set.shape[1]
    assert init_dim > subspace_rank
    assert subspace_rank > 0

    centroid = point_set.mean(axis=0)
    if sum(centroid) != 0:
        # - Compute the centered matrix:
        centered_point_set = point_set - centroid
    else:
        centered_point_set = point_set

    # -- Compute the Singular Value Decomposition (SVD) of centered coordinates:
    U,D,V = svd(centered_point_set, full_matrices=False)
    V = V.T

    # -- Compute the projection matrix:
    H = np.dot(V[:,0:subspace_rank], V[:,0:subspace_rank].T)

    return H

def random_color_dict(list_cell, alea_range=None):
    """
    Generate a dict where keys -from a given list `list_cell`- receive a random integer from the list as value.
    """
    import random
    if isinstance(alea_range,int):
        return dict(zip( list_cell, [random.randint(0, alea_range) for k in xrange(len(list_cell))] ))
    elif isinstance(alea_range,list) and (len(alea_range)==2):
        return dict(zip( list_cell, [random.randint(alea_range[0], alea_range[1]) for k in xrange(len(list_cell))] ))
    else:
        return dict(zip( list_cell, [random.randint(0, 255) for k in xrange(len(list_cell))] ))


def geometric_L1(spia):
    """
    """
    background = spia._background
    L1_labels = spia.cell_first_layer()
    L1_cells_bary = spia.center_of_mass(L1_labels, verbose=True)

    background_neighbors = spia.neighbors(L1_labels, min_contact_area=10., real_area=True)
    background_neighbors = set(background_neighbors) & set(L1_labels)
    L1_cells_bboxes = spia.boundingbox(L1_labels)

    print "-- Searching for the median voxel of each epidermis wall ..."
    dict_wall_voxels, epidermis_wall_median, median2bary_dist = {}, {}, {}
    for label_2 in background_neighbors:
        dict_wall_voxels[(background,label_2)] = wall_voxels_between_two_cells(spia.image, background, label_2, bbox = L1_cells_bboxes[label_2], verbose = False)
        epidermis_wall_median[label_2] = find_wall_median_voxel(dict_wall_voxels[(background,label_2)], verbose = False)
        median2bary_dist[label_2] = distance(L1_cells_bary[label_2], epidermis_wall_median[label_2])

    return median2bary_dist, epidermis_wall_median, L1_cells_bary


