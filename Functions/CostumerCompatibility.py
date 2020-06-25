"""
This file contains a function that is used to calculate an approximate saving index of including two custumers belonging to
different cells along the same route. These indexes will be used in policies NP and NP_1.
This index is an approximation, because we don't know a priori the set of future customers (and their positions),
so we consider as approximate position of customer belonging to a cell the (x,y) coordinate of the centre.
It must be noticed that even if this calculation scales as O(#cells^2), it is performed only once at the begining of the simulation.
"""


import numpy as np
from scipy.spatial import distance


def select_compatible_cells(df_distribution, depot, rho):
    '''
    For each cell (C1) create a list of cells (C2, C3, ...) that lead to a index of saving higher than a threshold rho:
    including customers belonging to a cell of the list (C2, C3, ...) in the same route of a customer belonging to C1 is convenient.
    INPUTS:
        df_distribution: dataframe containg all information about cells, each row represents a cell. 
                        We consider the following columns
                        cell_name: integer number that identifies the cell
                        x: x-coordinate of left corner of the cell
                        y: y-coordinate of lower corner of the cell
                        lenght: lenght of the cell on x-axis
                        height: lenght of the cell on y-axis
                        probability: probability of a simulated customer to belong to this cell
        depot: numpy array containig depot (x,y) coordinates.
        rho: threshold to select convenient cells to put in the list (C2, C3, ...) according to saving indexes.
    OUTPUTS:
        compatibility_list: list of dimension #cells whose elements are list of convenient cells
        compatibility_index: numpy array of dimension #cells*#cells which contains the saving indexes
        distance_matrix[0]: numpy array of dimension #cells+1 containing all distance from depot to each cells (and the depot itself
                            in position 0)
    '''
    # number of cells
    num_cell = len(df_distribution)
    # calculate centers of each cell
    df_distribution['x_center'] = df_distribution.x+df_distribution.length/2
    df_distribution['y_center'] = df_distribution.y+df_distribution.height/2
    # convert to numpy coordinates
    cell_coords = df_distribution[['x_center', 'y_center']].to_numpy()
    # add depot coordinates at the begining
    coords = np.vstack ((depot, cell_coords))
    # initialize the matrix of indexes
    compatibility_index = np.zeros((num_cell,num_cell))
    # calculate distance matrix
    distance_matrix = distance.cdist(coords, coords)
    # initialize list for compatible cell
    compatibility_list = []
    for i in range(num_cell):
        for j in range( num_cell):
            if j != i:   
                # saving index of including cell i and cell j in the same route         
                compatibility_index[i][j] = (distance_matrix[0][i+1]+distance_matrix[0][j+1]-distance_matrix[i+1][j+1])\
                                            /(2*(distance_matrix[0][i+1]+distance_matrix[0][j+1]))
            else:
                # customers in the same cell are always compatible
                compatibility_index[i][j] = 1
        # select convenient cells according to threshold rho
        compatibility_list.append(np.where(compatibility_index[i] > rho)[0])
    return compatibility_list, compatibility_index, distance_matrix[0]