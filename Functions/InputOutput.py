'''
I/O Management:
The following functions are useful
- to check the correctness of the input arguments
- to manage output files: clean pre-existent solution files and save the new solution to CVRPs
- to manage the input file: read information about the region in which customers are simulated
'''


import pandas as pd
import numpy as np
import sys
import os



def check_arguments(argv):  
    '''
    Parse command line and check if the passed arguments are correct:
    Run code with command line arguments:
        input_file_path -p policy -d days_simulation -s solver
    WHERE:
        - input_file_path is the file containing density distribution (i.e. grid.txt)
        - policy is the desired policy to select which customers to serve
            EP : early policy
            DP : delayed policy
            NP : neighbourhood policy
            NP_1 : neighbourhood policy 1
        - days_simulation is the number of day you want to simulate
        - solver is the solver for CVRP
            ortools : Google ORtools solver
            tabu : Tabù Search
    
    INPUT:
        argv: command line arguments
    OUTPUTS:
        error: True if there is some kind of error in the input arguments
        input_path: path of input file containing cells' distributions
        policy: the selected policy for simulation
        n_days: number of days of simulation
        solver: solver type for CVRP
    ''' 
    # Initialize variables
    error = False
    input_path = ''
    policy = ''
    n_days = ''
    solver = ''
    # Check if the number of input arguments is correct
    if len(argv)==8:
        # file with initial distribution of clients
        input_path = argv[1]
        if argv[2]=="-p" and (argv[3]=="EP" or argv[3]=="DP" or argv[3]=="NP" or argv[3]=="NP_1"):
            # policy for customer selections
            policy = argv[3]
        else:
            sys.stderr.write("Error: not available inserted policy\n")
            error = True
        if argv[4]=="-d":
            # number of simulated days
            n_days = int(argv[5])
        else:
            sys.stderr.write("Error: number of days\n")
            error = True
        if argv[6]=="-s" and (argv[7]=="ortools" or argv[7]=="tabu"):
            # choose the solver for CVRP problem
            solver = argv[7]
        else:
            sys.stderr.write("Error: not available inserted solver\n")
            error = True
    else:
        error = True
    if error:
        print(argv)
        sys.stderr.write("Run code with command line arguments:\n input_file_path -p policy -d days_simulation -s solver\n WHERE:\n\
        - input_file_path is the file containing density distribution (i.e. grid.txt)\n\
        - policy is the desired policy to select which customers to serve \n\
        \t EP : early policy\n \t\t DP : delayed policy\n \t\t NP : neighbourhood policy\n \t\t NP_1 : neighbourhood policy 1\n\
        - days_simulation is the number of day you want to simulate\n\
        - solver is the solver to solve CVRP \n\
        \t ortools: Google ORtools solver\n \t\t tabu: Tabù Seach algorithm\n")
    return error, input_path, policy, n_days, solver
    
    

def clean_files(): 
    '''
    Clean pre-existing files:
        './Data/simulated_clients.txt' will contain all information of the custumers generated by the simulation, each day all
                                       pending customers will be saved
        './Data/selected_customers.txt' will contain all information of selected customer according to the chosen policy, each day
                                        the customers used in a feasible CVRP will be saved
        './Solution/routes.sol' will contain the routes found by CVRP solver, each day the customers served by each vehicle (and
                                their order) will be saved
    '''
    file1 = open('./Data/simulated_clients.txt', 'w+') 
    file1.close()

    file2 = open('./Data/selected_customers.txt', 'w+') 
    file2.close()

    # Create directory, if it doesn't exist yet
    if not os.path.exists('Solution'):
        os.mkdir('Solution')

    file3 = open('./Solution/routes.sol', 'w+') 
    file3.close()    



def load_distribution(file_path):
    """
    Read customers distribution from input file and create the corresponding data-frame:
    INPUT:
        input_path: path to file containig the distribution of customers in the region we want to simulate them.
        The format of this file is the following: in each line there must be the information of a cell

        cell#int \t x_left \t y_low \t lenght \t height \t probability \n

            int: integer number that identifies the cell
            x_left: x-coordinate of left corner of the cell
            y_low: y-coordinate of lower corner of the cell
            lenght: lenght of the cell on x-axis
            height: lenght of the cell on y-axis
            probability: probability of a simulated customer to belong to this cell

        For example
        cell#1	0	0	5	5	0.00000610388817676860

        Cells are not overlapping.

    OUTPUTS:
        df: dataframe containg all information about cells, each row represents a cell. We consider the following columns
            cell_name <- int-1
            x <- x_left
            y <- y_low
            lenght <- lenght
            height <- height
            probability <- probability
        depot: numpy array containig the (x,y) coordinates of the depot
    """
    # Input path
    file_path = './Data/'+file_path
    with open(file_path, "r") as fp:
        # initialize empty dictionary
        data_lines = {'cell_name': [], 'x': [], 'y': [], 'length': [], 'height': [], 'probability': []}
        for line in fp:
            # delete white lines
            line = line.strip()
            if line:
                # Read non empty lines
                elements = line.split('\t')
                # assign each value to the corresponding column (cell numeration starting from 0)
                data_lines['cell_name'].append(int(elements[0].split('#',1)[1])-1)
                data_lines['x'].append(float(elements[1]))
                data_lines['y'].append(float(elements[2]))
                data_lines['length'].append(float(elements[4]))
                data_lines['height'].append(float(elements[4]))
                data_lines['probability'].append(float(elements[5]))
    # create dataframe
    df = pd.DataFrame(data_lines)
    # make all probabilities sum up to 1
    total_prob = df['probability'].sum()
    df['probability'] = df['probability'].apply(lambda x: x/total_prob)
    # calculate depot position: we consider a central depot
    depot = np.array( [(df['x'].min()+df['x'].max())/2 , (df['y'].min()+df['y'].max())/2] ) 
    return df, depot



def save_routes(day, data, manager, routing, solution, file_path='./Solution/routes.sol'):
    '''
    Save routes found by CVRP solver: each day the file containg all the solutions of the simulationis updated.
    INPUTS:
        day: object of class Day referring to the current day solution
        data: dictionary containing
            'distance_matrix': adjacency matrix of the problem, taking into account all times to travel from customer-to-customer
                               or from customer-to-depot
            'num_vehicles': number of available vehicles
            'depot': index of depot in adjacency matrix
            'demands': list of demands of all customers (in kg)
            'vehicle_capacities': list of vehicles' capacities
        manager: routing index manager
        routing: routing model
        solution: solution to CVRP
        [file_path]: path to file in which the solutions to CVRPs are saved
    OUTPUT:
        num_empty_route: number of empty vehicles in the current day
    '''
    # Initialize variables:
    # lenght of the longest route
    max_route_distance = 0
    # total lenght of all routes
    total_distance = 0
    # total load of all routes
    total_load = 0
    # number of empty vehicles
    num_empty_route = 0
    # Save the current day
    with open(file_path, 'a') as fp:            
        fp.write(f'\n DAY: {day.current_day} \n')
    # Save routes of all vehicles
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        # lenght of route for a single vehicle
        route_distance = 0
        # load for a single vehicle
        route_load = 0
        # number of customer for a single vehicle
        empty_route = 0
        # Cycle on all customers served by the considered vehicle
        while not routing.IsEnd(index):
            empty_route += 1
            # index of the customer
            node_index = manager.IndexToNode(index)
            # demand of the customer
            route_load += data['demands'][node_index]
            plan_output += ' {} -> '.format(node_index)
            previous_index = index
            # select following customer
            index = solution.Value(routing.NextVar(index))
            # add lenght of the arc
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        # Save travel and service time of the route (h)
        plan_output += 'Travel and service time of the route: {} h\n'.format(round(route_distance/60,2))
        # Save load of the route (kg)
        plan_output += 'Load of the route: {} kg \n'.format(round(route_load,2))
        total_distance += route_distance
        total_load += route_load
        max_route_distance = max(max_route_distance, route_distance)
        # If the only node in the route for the vehicle is the depot this vehicle is empty
        if empty_route<=1 :
            num_empty_route += 1
        with open(file_path, 'a') as fp:          
            fp.write(plan_output)
    with open(file_path, 'a') as fp:          
            fp.write('Total travel and service time of all routes: {} h\n'.format(round(total_distance/60,2)))
            fp.write('Total load of all routes: {} kg\n'.format(round(total_load, 2)))
            fp.write('Maximum of the route travel time: {} h\n'.format(round(max_route_distance/60,2)))
    return num_empty_route


    