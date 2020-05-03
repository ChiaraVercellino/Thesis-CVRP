import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import sys


# Parse command line and check if the arguments are correct
def check_arguments(argv):   
    error = False
    input_path = ''
    policy = ''
    n_days= ''
    if len(argv)==6:
        # file with initial distribution of clients
        input_path = argv[1]
        if argv[2]=="-p" and (argv[3]=="EP" or argv[3]=="DP"):
            # policy for customer selections
            policy = argv[3]
        else:
            sys.stderr.write("Error: inserted policy\n")
            error = True
        if argv[4]=="-d":
            # number of simulated days
            n_days = int(argv[5])
        else:
            sys.stderr.write("Error: number of days\n")
            error = True
    else:
        error = True
    if error:
        sys.stderr.write("Run code with command line arguments:\n input_file_path -p policy -d days_simulation\n WHERE:\n\
        - input_file_path is the file containing density distribution (i.e. grid.txt)\n\
        - policy is the desired policy to select which customers to serve \n\
        \t EP : early policy\n \t\t DP : delayed policy\n\
        - days_simulation is the number of day you want to simulate")
    return error, input_path, policy, n_days
    
    
# Clean pre-existing files
def clean_files():    
    with open('./Data/simulated_clients.txt', 'r+') as fp:
        fp.truncate(0)    
    with open('./Data/selected_customers.txt', 'r+') as fp:
        fp.truncate(0)
    with open('./Solution/routes.sol', 'r+') as fp:
        fp.truncate(0)


# Read data distribution from file in file_path and create the corresponding data frame
def load_distribution(file_path):
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
                # assign each value to the corresponding column
                data_lines['cell_name'].append(elements[0])
                data_lines['x'].append(float(elements[1]))
                data_lines['y'].append(float(elements[2]))
                data_lines['length'].append(float(elements[4]))
                data_lines['height'].append(float(elements[4]))
                data_lines['probability'].append(float(elements[5]))
    df = pd.DataFrame(data_lines)
    # make all probabilities sum up to 1
    total_prob = df['probability'].sum()
    df['probability'] = df['probability'].apply(lambda x: x/total_prob)
    # calculate depot position
    depot = np.array( [(df['x'].min()+df['x'].max())/2 , (df['y'].min()+df['y'].max())/2] ) 
    return df, depot


# Save routes found by VRP solver
def save_routes(day, data, manager, routing, solution, file_path='./Solution/routes.sol'):
    max_route_distance = 0
    total_distance = 0
    total_load = 0
    num_empty_route = 0
    with open(file_path, 'a') as fp:            
        fp.write(f'\n DAY: {day.current_day} \n')
    routes_list = []
    for vehicle_id in range(data['num_vehicles']):
        single_route = []
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        empty_route = 0
        while not routing.IsEnd(index):
            empty_route += 1
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            single_route.append(manager.IndexToNode(index))
            plan_output += ' {} -> '.format(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        single_route.append(manager.IndexToNode(index))
        plan_output += 'Travel and service time of the route: {} h\n'.format(round(route_distance/60,2))
        plan_output += 'Load of the route: {} kg \n'.format(round(route_load,2))
        total_distance += route_distance
        total_load += route_load
        max_route_distance = max(max_route_distance, route_distance)
        if empty_route<=1 :
            num_empty_route += 1
        with open(file_path, 'a') as fp:          
            fp.write(plan_output)
        routes_list.append(single_route)
    with open(file_path, 'a') as fp:          
            fp.write('Total travel and setup time of all routes: {} h\n'.format(round(total_distance/60,2)))
            fp.write('Total load of all routes: {} kg\n'.format(round(total_load, 2)))
            fp.write('Maximum of the route travel time: {} h\n'.format(round(max_route_distance/60,2)))
    return routes_list, num_empty_route


    