# All functions
import nibabel as nib
import numpy as np
from scipy.spatial.distance import pdist
import pandas as pd
from scipy import ndimage
from scipy import stats
import csv
import scipy.spatial.distance as ssd


def atlas_centroids(atlas_filepath):
    # read in atlas
    V = nib.load(atlas_filepath)
    atlas = V.get_fdata()

    # get distance matrix for all electrodes and atlas ROIs
    labels = np.unique(atlas[np.where(atlas)])
    centroid = np.zeros((len(labels), 3))
    for i in range(len(labels)):
        idx = np.where(atlas == labels[i])
        centroid[i, :] = np.mean(idx, axis=1)

    return centroid

def gen_sphere(radius):
    # generates a 3D matrix that labels voxels as inside our outside a given
    # radius.
    dim = 2*radius + 1 # size of box containing sphere
    mid = radius + 1 # midpoint of the box ([mid mid mid] is centroid)
    my_sphere = np.zeros((dim, dim, dim)) # build box
    for i in range(np.size(my_sphere)): # loop through each location in box
        X, Y, Z = np.unravel_index(i, (dim, dim, dim)) # get coordinates
        D = pdist(np.array([[mid, mid, mid], [X, Y, Z]]).T, 'euclidean') # distance from centroid
        # if D <= radius in any dimension, put in box
        # if D <= radius
        if (D[0] <= radius and D[1] <= radius and D[2] <= radius): # if less than radius, put in box
            my_sphere[X, Y, Z] = 1

    # get coordinates and offset by center voxel
    coords = np.where(my_sphere)
    coords = np.array(coords) - mid

    return my_sphere, coords

def mni2cor(mni, T=None):
    if mni.size == 0:
        return np.array([])
    if T is None:
        T = np.array([
            [-2, 0, 0, 92],
            [0, 2, 0, -124],
            [0, 0, 2, -74],
            [0, 0, 0, 1]
        ])
    coordinate = np.matmul(mni, np.linalg.inv(T))
    coordinate = np.round(coordinate)
    return coordinate

def mniCoord2Label(coords_filepath, atlas_name):
    # read in default AAL116 if not specified
    if not atlas_name:
        atlas_name = 'AAL116'

    # read in AAL116 image
    atlas_filepath = atlas_name + '.nii'
    mni_coords, mni_labels, NN_flag = nifti_values(coords_filepath, atlas_filepath)

    # get AAL atlas info
    with open(atlas_name + '.txt') as fileID:
        atlas_info = csv.reader(fileID, delimiter='\t')
        atlas_info = list(atlas_info)

    # Get label names (ex: HIP 4101 & 4102)
    for i in range(len(mni_labels)):
        C, ia, ib = np.intersect1d(mni_labels[i], atlas_info[1], return_indices=True)
        ib = ib[0]
        atlas_info[1][ib] = atlas_info[0][ib] + ' ' + atlas_info[1][ib]

    # output AAL116 roi names and atlas labels
    electrode_regions = [atlas_info[1][ib] for ib in ib]
    electrode_regions = [electrode_regions, mni_labels, NN_flag]

    # get distance matrix for all electrodes and atlas ROIs
    centroid = atlas_centroids(atlas_filepath)
    distance_matrix = ssd.pdist(np.vstack((centroid, mni_coords)), 'euclidean')

    return electrode_regions, distance_matrix, atlas_info

def nifti_values(coords_filepath, atlas_filepath):
    """takes in a csv file where the first 3 columns are (x,y,z) MNI
    coordinates and an atlas file in mni space and outputs the atlas labels
    for the csv coordiantes.

    Test:
      [mni_labels] = nifti_values('test_input.csv','AAL116.nii')

    Input:
      csv_filepath (str): filepath to coordinate file organized (Nx3)
      atlas_filepath (str): filepath to atlas file in MNI space (.gz unzip)

    Output:
      mni_labels (double): atlas values at each given coordinate
      NN_flag (double): flags coordinates where nearest neighbor was
          indicated due to atlas value 0

    Thomas Campbell Arnold

    modifications
    7/11/19 - changed dlmread to readtable, resolve string/numeric read error
    10/16/19 - extracted gen_sphere subroutine and included as seperate function
    """
    # Read in AAL image
    V = nib.load(atlas_filepath)  # get header
    atlas = V.get_fdata()  # get 3D matrix
    T = V.affine  # get transformation matrix
    T = T.T  # transpose transformation matrix

    # get mni coordinates from csv and transfer to matlab coordinate space
    # csv_coords = readtable(coords_filepath);
    csv_coords = coords_filepath
    # csv_coords = table2array(csv_coords(:,2:4)); % only get coordinates
    mni_coords = mni2cor(csv_coords, T)

    NN_flag = np.zeros((mni_coords.shape[0], 2))  # variable indicating no label initial found in atlas

    # get AAL label based on coordinates
    for i in range(mni_coords.shape[0]):
        # initialize variable mni_labels ### may be wrong
        mni_labels = np.zeros((mni_coords.shape[0], 1)) ### may be wrong
        # assign initial value
        try:
            mni_labels[i] = atlas[mni_coords[i, 0], mni_coords[i, 1], mni_coords[i, 2]]
        except:
            print("Problem with ", i, "th coordinate [", mni_coords[i, 0], " ", mni_coords[i, 1], " ", mni_coords[i, 2], "].  Assigning a label of 0.")
            mni_labels[i] = 0

        radius = 0
        while mni_labels[i] == 0:  # get mode of cubes until answer is achieved
            NN_flag[i, 0] = 1  # store value indicating label not localizaed
            radius = radius + 1  # increase radius
            my_sphere, coords = gen_sphere(radius)  # get coordinates to sample
            x = coords.x + mni_coords[i, 0]
            y = coords.y + mni_coords[i, 1]
            z = coords.z + mni_coords[i, 2]

            # get sample values
            try:
                ind = np.ravel_multi_index((x, y, z), atlas.shape)  # convert to indices
            except:
                break
            sphere_vals = atlas[ind]  # sample sphere
            vals = sphere_vals[sphere_vals != 0]  # find nonzero and non-NaN values
            if vals:  # if there are nonzero values, update label
                mni_labels[i] = stats.mode(vals)[0][0]  # get mode
                NN_flag[i, 1] = radius  # store distance to NN
                
            # break while loop if radius is larger than 3 voxels
            if radius >= 3:
                break

    return mni_labels, NN_flag
