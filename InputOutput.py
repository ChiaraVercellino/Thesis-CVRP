import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


# Read data distribution from file in file_path and create the corresponding data frame
def load_distribution(file_path):

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


# Save the simulated data of each customer
def save_data_costumers(day, file_path):
    # append new data to the previous ones
    with open(file_path, 'a') as fp:
        fp.write(f'\n DAY: {day.current_day} \n')
        # write all data frame to in a file
        fp.write(day.customer_df.to_string(header=True, index=True))


# Save selected customers customer
def save_selected_costumers(day, selected_customers, file_path='selected_customers.txt'):
    # append new data to the previous ones
    with open(file_path, 'a') as fp:
        fp.write(f'\n DAY: {day.current_day} \n')
        # write all data frame to in a file
        fp.write(selected_customers.to_string(header=True, index=True))


# save routes found by VRP solver
def save_routes(day, data, manager, routing, solution, file_path='routes.txt'):
    with open(file_path, 'a') as fp:            
        fp.write(f'\n DAY: {day.current_day} \n')
    routes_list = []
    for vehicle_id in range(data['num_vehicles']):
        single_route = []
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
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
        plan_output += 'Distance of the route: {} km\n'.format(route_distance)
        plan_output += 'Load of the route: {} kg \n'.format(round(route_load,2))
        with open(file_path, 'a') as fp:          
            fp.write(plan_output)
        routes_list.append(single_route)
    return routes_list


# plot found routes
def plot_routes(customers, depot, route_list, day):
    # create a dictionary with position of each costumer
    pos={0: depot}
    customers.apply(lambda client_line: _add_client(client_line, pos), axis=1)
    G=nx.Graph()
    # add nodes to graph
    G.add_nodes_from(pos.keys())
    # add coordinates to nodes
    for n, p in pos.items():
        G.nodes[n]['pos'] = p
    # add edges in graph
    for route in route_list:
        edges = list(zip(route, route[1:] + route[:1]))
        G.add_edges_from(edges)
    # draw and dispay graph
    nx.draw(G, pos, node_size=2.0)
    # draw labels
    nx.draw_networkx_labels(G, pos,  font_size=6)
    # save graph
    path = "route_day_"+str(day)+".png"
    plt.savefig(path)


def _add_client(client_line, pos):
    pos[client_line.customer_label] = [client_line.x, client_line.y]
    return client_line
    
    