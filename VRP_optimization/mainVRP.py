"""
Capacitated Vehicles Routing Problem (CVRP):
We have selected a set costumers to be served in this specific day, each one is characterized by 
- position: (x,y) coordinates in the considered region
- demand: kg of required ware
- service time: time to install the ware
We consider only one depot, from which all vehicles start their routes. We want to minimize the daily travel time and vehicles used,
subject to the following constraints:
- The capacity (kg) of each vehicle is limited to 1000 kg
- Each vehicle has a working day of maximum 480 min, taking into account both travel time and service time of the customers
- Each vehicle can serve up to 5 customers
Remember that those fixed values for constraints can be modified in file constant.py

The CVRP is solved using routing optimization tools from library OR-Tools, which gives as a result the best routes found.

A reference for the code can be found at
https://developers.google.com/optimization/routing/cvrp
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from scipy.spatial import distance
import numpy as np
import constant


def _create_data_model(select_clients_df, depot, vehicles, capacity_kg): 
    """
    Stores the data for the CVRP problem: build the data structure to solve the optimization problem.
    INPUTS:
        select_clients_df: dataframe containing in each row information that refers to a specific customer to be served
        depot: numpy array containing (x,y) coordinates of the depot
        vehicles: number of available vehicles
        capacity_kg: capacity constraint in kg for a single vehicle
    OUTPUT:
        data: dictionary containing
            'distance_matrix': adjacency matrix of the problem, taking into account all times to travel from customer-to-customer
                               or from customer-to-depot
            'num_vehicles': number of available vehicles
            'depot': index of depot in adjacency matrix
            'demands': list of demands of all customers (in kg)
            'vehicle_capacities': list of vehicles' capacities
    """ 
    # Initialize empty dictionary
    data = {}
    # select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
    clients_coords = select_clients_df[['x', 'y']].to_numpy()
    # add at the beginning of the coordinates array the coordinates of depot
    coords = np.vstack ((depot, clients_coords)) 
    # the service time of depot is 0
    service_time = np.array([0])
    # creare a numpy array containig the service times of all nodes (=depot+customers)
    service_time = np.append(service_time, select_clients_df[['service_time']].to_numpy())
    # I'll add all service times column-wise to adjacency matrix to obtain a time constraint that consider both the travel time
    # and the service time: element (i,j) of adjacenty matrix is time to travel from i to j + service time of j 
    service_time_matrix = np.tile(service_time,(len(service_time),1))
    # calculate adjacency matrix considering only travel time: actually this matrix contains distances, but assuming that those
    # distances are in km and that vehicles travel at an average speed of 60km/h, those numerical values correspond also to minutes
    # of travel time
    data['distance_matrix'] = distance.cdist(coords, coords)
    # add service times
    data['distance_matrix'] += service_time_matrix
    # number of available vehicles
    data['num_vehicles'] = vehicles
    # the depot is the first node, so its corresponding index is 0
    data['depot'] = 0
     # add demands in kg of all nodes: depot has 0 demand
    data['demands'] = [0]+select_clients_df.kg.tolist()
    # all vehicles has the same capacity
    data['vehicle_capacities'] = [capacity_kg] * vehicles
    return data


def VRP_optimization(select_clients_df, depot, vehicles, capacity_kg):
    """
    Solve the CVRP problem: given the selected costumers and the problem's specifications, such as capacity constraints, depot
    position, OR-Tools library is used to find optimal routes that minimize travel time and number of vehicles used.
    INPUTS:
        select_clients_df: dataframe containing in each row information that refers to a specific customer to be served
        depot: numpy array containing (x,y) coordinates of the depot
        vehicles: number of available vehicles
        capacity_kg: capacity constraint in kg for a single vehicle
    OUTPUTS:
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
    """
    # Instantiate the data problem
    data = _create_data_model(select_clients_df, depot, vehicles, capacity_kg)
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the travel + service time between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    # Define time distances between locations
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc = cost of each travel.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        """Returns the demand in kg of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    # Define demands of each customer
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    # Add Time constraint
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        constant.TIME,  # vehicle maximum travel time and service time (in minutes)
        True,  # start cumul to zero
        dimension_name)

    # Add constraint on number of costumers served by each vehicle
    plus_one_callback_index = routing.RegisterUnaryTransitCallback(lambda index : 1)
    dimension_name = 'Counter'
    routing.AddDimension(
        plus_one_callback_index,
        0,  # null capacity slack
        constant.CUSTOMER_CAPACITY+1,  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name)
    counter_dimension = routing.GetDimensionOrDie(dimension_name)
    for vehicle_id in range(vehicles):
        index = routing.End(vehicle_id)
        counter_dimension.CumulVar(index).SetRange(0, constant.CUSTOMER_CAPACITY+1)
    
    # Add Capacity constraint
    dimension_name = 'Capacity'
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name)    
    
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # Use CHRISTOFIDES to minimize the number of vehicles used
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
    
    # Setting maximum time limit for search (in seconds)
    search_parameters.time_limit.seconds = constant.TIME_LIMIT

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    return  data, manager, routing, solution
