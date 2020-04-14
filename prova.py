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
    # create distances' matrix
    data['distance_matrix'] = distance.cdist(coords, coords)
    data['num_vehicles'] = vehicles
    data['depot'] = 0
    # add demands in kg
    data['demands'] = [0]+select_clients_df.kg
    data['vehicle_capacities'] = [capacity_kg] * vehicles
    return data


def _print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):            
            node_index = manager.IndexToNode(index)
            print(node_index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)        
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {} km\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {} km'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    print('Maximum of the route distances: {} km'.format(max_route_distance))


def VRP_optimization(select_clients_df, depot, vehicles, capacity_small):
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    print('VRP begins')
    data = _create_data_model(select_clients_df, depot, vehicles, capacity_small)
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

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        350,# vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    """# Add constraint on number of clients served by each vehicle
    plus_one_callback_index = routing.RegisterUnaryTransitCallback(lambda index : 1)
    dimension_name = 'Counter'
    routing.AddDimension(
        plus_one_callback_index,
        0,  # null capacity slack
        7,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Counter')
    counter_dimension = routing.GetDimensionOrDie(dimension_name)
    for vehicle_id in range(vehicles):
        index = routing.End(vehicle_id)
        counter_dimension.CumulVar(index).SetRange(0, 7)"""

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Setting maximum time limit for search (in seconds)
    search_parameters.time_limit.seconds = 300

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        #pass
        _print_solution(data, manager, routing, solution)
    else:
        print('no solution found')

    return  data, manager, routing, solution
