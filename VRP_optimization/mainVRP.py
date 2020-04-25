"""Vehicles Routing Problem (VRP)."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from scipy.spatial import distance
import numpy as np


def _create_data_model(select_clients_df, depot, vehicles, capacity_kg):
    """Stores the data for the problem."""
    data = {}
    clients_coords = select_clients_df[['x', 'y']].to_numpy()
    coords = np.vstack ((depot, clients_coords)) 
    # create matrix of times
    set_up_time = np.array([0])
    set_up_time = np.append(set_up_time, select_clients_df[['set_up_time']].to_numpy())
    set_up_time_matrix = np.tile(set_up_time,(len(set_up_time),1))
    data['distance_matrix'] = distance.cdist(coords, coords)
    data['distance_matrix'] += set_up_time_matrix
    data['num_vehicles'] = vehicles
    data['depot'] = 0
     # add demands in kg
    data['demands'] = [0]+select_clients_df.kg.tolist()
    data['vehicle_capacities'] = [capacity_kg] * vehicles
    return data


def VRP_optimization(select_clients_df, depot, vehicles, capacity_kg):
    """Solve the VRP problem."""
    # Instantiate the data problem.
    data = _create_data_model(select_clients_df, depot, vehicles, capacity_kg)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    
    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    # Define distances between locations
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc = cost of each travel.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)


    # Add Time constraint.
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        480,  # vehicle maximum travel time and setup time (in minutes)
        True,  # start cumul to zero
        dimension_name)
    #time_dimension = routing.GetDimensionOrDie(dimension_name)
    # If I want to minimize the longest route
    #time_dimension.SetGlobalSpanCostCoefficient(10000)

    # Add constraint on number of clients served by each vehicle
    plus_one_callback_index = routing.RegisterUnaryTransitCallback(lambda index : 1)
    dimension_name = 'Counter'
    routing.AddDimension(
        plus_one_callback_index,
        0,  # null capacity slack
        6,  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name)
    counter_dimension = routing.GetDimensionOrDie(dimension_name)
    for vehicle_id in range(vehicles):
        index = routing.End(vehicle_id)
        counter_dimension.CumulVar(index).SetRange(0, 6)
    
    # Add Capacity constraint.
    dimension_name = 'Capacity'
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name)
    #capacity_dimension = routing.GetDimensionOrDie(dimension_name)
    
    
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES)
    
    # Setting maximum time limit for search (in seconds)
    search_parameters.time_limit.seconds = 30

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if not(solution):
        print('CVRP error: No solution found')

    return  data, manager, routing, solution
