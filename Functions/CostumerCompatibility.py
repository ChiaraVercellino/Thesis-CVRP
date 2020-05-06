import numpy as np
from scipy.spatial import distance

# select lists of customers that are compatible
def select_compatible_cells(df_distribution, depot, rho):
    np.seterr('raise')
    # number of cells
    num_cell = len(df_distribution)
    # calculate centers of each cell
    df_distribution['x_center'] = df_distribution.x+df_distribution.length/2
    df_distribution['y_center'] = df_distribution.y+df_distribution.height/2
    cell_coords = df_distribution[['x_center', 'y_center']].to_numpy()
    coords = np.vstack ((depot, cell_coords))
    compatibility_index = np.zeros((num_cell,num_cell))
    # calculate distance matrix
    distance_matrix = distance.cdist(coords, coords)
    # initialize list for compatible cell
    compatibility_list = []
    for i in range(num_cell):
        for j in range( num_cell):
            if j != i:            
                compatibility_index[i][j] = (distance_matrix[0][i+1]+distance_matrix[0][j+1]-distance_matrix[i+1][j+1])\
                                            /(2*(distance_matrix[0][i+1]+distance_matrix[0][j+1]))                                
        compatibility_list.append(np.where(compatibility_index[i] > rho)[0])
    return compatibility_list