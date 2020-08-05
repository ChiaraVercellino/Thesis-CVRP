import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model(service_time, distance_matrix, demands):
    """Stores the data for the problem."""
    data = {}
    service_time = np.append(np.array([0]), service_time)
    demands = np.append(np.array([0]), demands)
    data['service_time'] = service_time
    service_time_matrix = np.tile(service_time,(len(service_time),1))
    data['distance_matrix'] = distance_matrix
    data['distance_matrix'] += service_time_matrix
    data['demands'] = demands
    data['vehicle_capacities'] = [1000]*50
    data['num_vehicles'] = 50
    data['depot'] = 0
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load ({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load ({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Total time of the route: {} min\n'.format(route_distance)
        plan_output += 'Total load of the route: {} kg\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}km'.format(total_distance-sum(data['service_time'])))
    print('Total load of all routes: {}kg'.format(total_load))

def main():
    """Solve the CVRP problem."""
    np.random.seed(19)
    num_customer = 195
    distances = np.random.uniform(10,100,int(num_customer*(num_customer+1)/2))
    distance_matrix = np.zeros((num_customer+1,num_customer+1))
    distance_matrix[np.triu_indices(num_customer+1, 1)] = distances
    distance_matrix[np.tril_indices(num_customer+1, -1)] = distance_matrix.T[np.tril_indices(num_customer+1, -1)]
    service_time = np.random.randint(15,80,size=(num_customer,1))
    demand = np.random.randint(100,200,size=(num_customer,1))

    # Instantiate the data problem.
    data = create_data_model(service_time, distance_matrix, demand)
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

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    # Add Time constraint
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        480,  # vehicle maximum travel time and service time (in minutes)
        True,  # start cumul to zero
        dimension_name)

    # Add constraint on number of costumers served by each vehicle
    plus_one_callback_index = routing.RegisterUnaryTransitCallback(lambda index : 1)
    dimension_name = 'Counter'
    routing.AddDimension(
        plus_one_callback_index,
        0,  # null capacity slack
        6,  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name)
    counter_dimension = routing.GetDimensionOrDie(dimension_name)
    for vehicle_id in range(4):
        index = routing.End(vehicle_id)
        counter_dimension.CumulVar(index).SetRange(0, 6)

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
    # Use CHRISTOFIDES to minimize the number of vehicles used
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


main()