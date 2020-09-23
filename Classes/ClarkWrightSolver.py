'''
This class initialize the solution of a CVRP instance. It implements the Clark and Wright savings algorithm to merge routes that initially visit 
exaclty one customer, then the SmallRouteElimination algorithm is applied to try and further reduce the number of used vehicles.

The attributes of this class are:
    num_customers: integer that specify the number of customers in the CVRP instance
    num_vehicles: integer that specify the number of available vehicles to solve the CVRP instance
    num_routes: integer that counts the number of routes found in the initial solution
    distance_matrix: matrix that contains all the pair distances between custumers and depot locations
    demand: numpy array containing all the customers' demands expressed in kg
    service_time: numpy array containing all the customers' service times expressed in minutes
    customers: dictionary for the customers in the CVRP instance, the key is the identifier of the customer and the value is the customer's object
    routes: dictionary to memorize the routes of the CVRP solution, the key is the identifier of the route and the value is the route's object
    route_of_customers: dictionary containing, for each customer's identifier (key), the corresponding identifier (value) of the route to which he
                        is assigned
    small_routes: list containing all the identifier of small routes, i.e. routes that visit less then 3 customers 
    total_cost: total travel and service time cost associated with the initial solution

These attributes can be managed using the public methods:
    solve(self)
    print_solution(self, day, file_path='./Solution/routes.sol')
    
'''

# import Classes
from Classes.Customer import Customer
from Classes.Route import Route
# import libraries
import numpy as np
from scipy.spatial import distance
import random
import itertools
# import constant for fixed values
import constant


class ClarkWrightSolver():

    # ------------------------------------------ CONSTRUCTOR ----------------------------------------------------------

    def __init__(self, selected_customer, depot):
        '''
        Construction of class ClarkWrightSolver.
        INPUTS:
            selected_customer: dataframe containing all the data about customers of the CVRP instance
            depot: depot locations expressed in numpy coordinates

        '''
        # Compute the number of customers in the CVRP instance
        self.num_customers = len(selected_customer)
        # Set number of available vehicles
        self.num_vehicles = constant.NUM_VEHICLES
        # At the begining each customer is visit by a route, so the initial number of route is equal to the number of customers
        self.num_routes = self.num_customers
        # Select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
        clients_coords = selected_customer[['x', 'y']].to_numpy()
        # Add at the beginning of the coordinates array the coordinates of depot
        coords = np.vstack ((depot, clients_coords)) 
        # Compute the distance matrix
        self.distance_matrix = np.round(distance.cdist(coords, coords),3)
        # Convert the column 'kg' of the dataframe selected_customer into a numpy array
        self.demand = selected_customer['kg'].to_numpy()
        # Convert the column 'service_time' of the dataframe selected_customer into a numpy array
        self.service_time = selected_customer['service_time'].to_numpy()
        # Initialize an empty dictionary for the customers' objects
        self.customers = {}
        # Initialize an empty dictionary for the routes' objects
        self.routes = {}
        # Initialize an empty dictionary for the association of customers with routes
        self.route_of_customers = {}
        # Initialize an empty list for the small routes
        self.small_routes = []
        # Initialize the total cost of the initial solution
        self.total_cost = 0
        
        for k in range(self.num_customers):
            # Instantiate the customer's objects
            cust = Customer(k+1, self.demand[k], self.service_time[k])
            # Instantiate the route's object
            route = Route()
            # Initialize the route by inserting the customer in the route
            route.initialize_route(cust, self.distance_matrix[0][k+1])
            # Update dictionaries
            self.route_of_customers[k+1] = route.id
            self.routes[route.id] = route            
            self.customers[k+1] = cust
        

    # ------------------------------------------ PRIVATE METHODS ------------------------------------------------------


    def _compute_savings_matrix(self):
        '''
        Compute Clarke and Wright savings matrix SM: it is a matrix containing the savings indexes between pairs of customers' locations.
            SM(i,j)= c(0,i) + c(0,j) - c(i,j)
        where c(h,k) indicates the travel cost of going from location h to location k

        OUTPUT:
            saving_matrix: the savings matrix (numpy matrix)
        
        '''
        # Initialize the savings matrix
        saving_matrix = np.zeros((self.num_customers,self.num_customers))
        # Iterate over customers' pairs
        for i in range(self.num_customers):
            for j in range( self.num_customers):
                if j != i:   
                    # saving index of including cell i and cell j in the same route         
                    saving_matrix[i][j] = self.distance_matrix[0][i+1]+self.distance_matrix[0][j+1]-self.distance_matrix[i+1][j+1]
        return saving_matrix


    def _find_best_routes_for_cust(self, cust_id, small_route):
        '''
        Given a customer belonging to a small route, find the best route to insert him, among the other routes of the CVRP initial solution.

        INPUTS:
            cust_id: customer's identifier
            small_route: small route object
        OUTPUTS:
            feasible_route: flag that specifies if the insertion has led to a feasible route, it is True if the a feasible route was found, False
                            otherwise
            best_route: route object of the best route in which the customer could be inserted
            small_route: small route object (updated)       
        
        '''

        dist_matrix = self.distance_matrix
        # Select all the distances between the considered customer and all other customers' locations
        distances  = np.array(dist_matrix[cust_id][1:])
        # find indexes corresponding to increasing sorting of distances
        best_indexes = np.argpartition(distances, self.num_customers-1) 
        # Customer object
        cust = self.customers[cust_id]
        # Initialize flag
        feasible_route = False
        # Try and insert the customer in the same route of his nearest neighbours
        for best_index in best_indexes:
            # The customers's identifiers start from 1, the indexes in Python start from 0
            best_near_cust = best_index+1
            # Route identifier of the route on which the best neighbour is situated
            best_route_id = self.route_of_customers[best_near_cust]
            # Route object
            best_route = self.routes[best_route_id]
            # check if the customer could be inserted without violating the constraints on customers-capacity and load-capacity
            if best_route.load_cust+1 <= best_route.cap_cust and best_route.load_kg+cust.demand<=best_route.cap_kg:
                # Indexes of the neighbour customer in the route list
                idx_best_near = best_route.route.index(best_near_cust)
                # Preceding customer of the neighbour customer
                prec_cust = best_route.route[idx_best_near-1]
                # Succeding customer of the neighbour customer
                post_cust = best_route.route[idx_best_near+1]
                if dist_matrix[cust_id][post_cust] < dist_matrix[prec_cust][cust_id]:
                    # The best inserttion is between the neighbour customer and his successor in the route
                    # Compute the difference in travel cost of the hypothetical insertion
                    delta_load_min = dist_matrix[best_near_cust][post_cust] - dist_matrix[best_near_cust][cust_id] - dist_matrix[cust_id][post_cust]
                    # Compute the hypothetical new load of the route
                    new_load_min = best_route.load_min - delta_load_min + cust.service_time
                    # Update the new hypothetical path of the route
                    new_route = best_route.route[:idx_best_near+1]+[cust_id]+best_route.route[idx_best_near+1:]
                else:
                    # The best inserttion is between the neighbour customer and his predecessor in the route
                    # Compute the difference in travel cost of the hypothetical insertion
                    delta_load_min = dist_matrix[prec_cust][best_near_cust] - dist_matrix[prec_cust][cust_id] - dist_matrix[cust_id][best_near_cust]
                     # Compute the hypothetical new load of the route
                    new_load_min = best_route.load_min - delta_load_min + cust.service_time
                    # Update the new hypothetical path of the route
                    new_route = best_route.route[:idx_best_near]+[cust.id]+best_route.route[idx_best_near:]
                # Check if the insertion satisfies the time-constraint
                if new_load_min <= best_route.cap_min:
                    # Update the loads of the new route
                    best_route.load_min = new_load_min
                    best_route.load_cust += 1
                    best_route.load_kg += cust.demand
                    # Update the path of the new route
                    best_route.route = new_route
                    # Update route for the customer in the dictionary
                    self.route_of_customers[cust_id] = best_route.id
                    # Find index of the customer on the small route
                    small_cust_idx = small_route.route.index(cust_id)
                    # Preceding customer on the small route of the moved customer
                    prec_small_cust = small_route.route[small_cust_idx-1]
                    # Succeding customer on the small route of the moved customer
                    post_small_cust = small_route.route[small_cust_idx+1]
                    # Compute the difference in the travel cost due to the removal of the customer from the small route
                    delta_small_min = dist_matrix[prec_small_cust][cust_id] + dist_matrix[cust_id][post_small_cust] - dist_matrix[prec_small_cust][post_small_cust]
                    # Update the loads for the small route
                    small_route.load_min = small_route.load_min - delta_small_min - cust.service_time
                    small_route.load_cust -= 1
                    small_route.load_kg -= cust.demand
                    # Update the path of the small route
                    small_route.route.remove(cust_id)
                    # We found a feasible insertion
                    feasible_route = True
                    # We exit the for cycle
                    break
        return feasible_route, best_route, small_route
                            

    @staticmethod
    def _merge_routes(route1, route2, customer1, customer2, savings):
        '''
        Try and merge two routes in the fusion points represented by the customers.
        INPUTS:
            route1: first route that we try to merge
            route2: second route that we try to merge
            customer1: fusion point in the first route
            customer2: fusion point in the second route
            savings: savings associated with the merge
        OUTPUTS:
            feasible_route: boolean variables that states if the merge led to a feasible route, it is True if the merge was feasible, False
                            otherwise
            new_route: Route object of the merged route

        '''

        # New instance of a route
        new_route = Route()
        # load of the new merged route
        new_route.load_kg = route1.load_kg+route2.load_kg
        # duration of the new merged route
        new_route.load_min = route1.load_min+route2.load_min - savings
        # number of customers visited by the new merged route
        new_route.load_cust = route1.load_cust+route2.load_cust
        # check if the merged route is feasible
        feasible_route = new_route.check_constraints()

        if feasible_route:
            # Initialize the empty route list
            new_route_list = []
            # Index of the first customer in the first route's path
            idx_cus1 = route1.route.index(customer1+1)
            # Index of the second customer in the second route's path
            idx_cus2 = route2.route.index(customer2+1)
            # Update the route's path by merging the two routes
            if route1.route[idx_cus1-1]==0:
                if route2.route[idx_cus2-1]==0:
                    new_route_list = route1.route[idx_cus1 :][::-1] + route2.route[idx_cus2 :]
                elif route2.route[idx_cus2+1]==0:
                    new_route_list = route2.route[: idx_cus2+1] + route1.route[idx_cus1 :]
            elif route1.route[idx_cus1+1]==0:
                if route2.route[idx_cus2-1]==0:
                    new_route_list = route1.route[: idx_cus1+1] + route2.route[idx_cus2 :]
                elif route2.route[idx_cus2+1]==0:
                    new_route_list = route2.route[: idx_cus2+1] + route1.route[: idx_cus1+1][::-1]
            # Update the path of the merged route
            new_route.route = new_route_list

            if not(new_route_list):
                # new_route_list is empty
                feasible_route = False

        return feasible_route, new_route


    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------


    def solve(self):
        '''
        Solve the CVRP applying 2 algortithms:
        Clarke and Wright algorithm: to merge the routes
        SmallRoutesElimination algorithm: to try and eliminate small routes (routes with less than 3 customers)

        OUTPUT:
            feasible_solution: boolean variable that specify if a feasible initial solution to CVRP was found, it is True if the initial solution
                               is feasible, False otherwise

        '''

        # CLARK AND WRIGHT ALGORITHM

        # Compute the savings matrix
        savings_matrix = self._compute_savings_matrix()
        # Set all elements in the lower triangular matrix of savings_matrix to 0
        savings_matrix[np.tril_indices_from(savings_matrix, -1)] = 0
        # Number of elements in the upper triangular matrix
        num_elem_tridiag = int((self.num_customers-1)*self.num_customers/2)
        # Takes pair of row-column indexes of the savings matrix that correspond to its upper triangular elements sorted in decreasing order:
        # the first pair is the one associated with the highest saving in the matrix
        best_savings_indexes = np.unravel_index(np.argsort(savings_matrix.ravel())[-num_elem_tridiag:], savings_matrix.shape)

        # Iterate over all sorted pairs
        for i in range(num_elem_tridiag):
            # The first customer corresponds to the row index
            customer1=best_savings_indexes[0][num_elem_tridiag-1-i]
            # The second customer corresponds to the column index
            customer2=best_savings_indexes[1][num_elem_tridiag-1-i]
            # Identifier of the route on which is situated the first customer
            route1_idx=self.route_of_customers[customer1+1]
            # Identifier of the route on which is situated the seoond customer
            route2_idx=self.route_of_customers[customer2+1]
            # First route object
            route1 = self.routes[route1_idx]
            # Second route object
            route2 = self.routes[route2_idx]
            # Check that the two customers don't belong to the same route yet
            if route1_idx != route2_idx:
                # saving associated with the pair of customers
                savings = savings_matrix[customer1][customer2]
                # Try to merge the two routes
                feasible_route, new_route = self._merge_routes(route1, route2, customer1, customer2, savings)
                if feasible_route:
                    # Update route_of_customers for all the customers belonging to the new route
                    for cust_id in new_route.route[1:-1]:
                        self.route_of_customers[cust_id]=new_route.id
                    # Add the new route to the dictionary of the routes
                    self.routes[new_route.id]=new_route
                    # Decrement the number of used vehicles
                    self.num_routes -= 1
                    # Delete old routes
                    del self.routes[route1_idx]
                    del self.routes[route2_idx]
                else:
                    # The new merged route is not feasible, delete it
                    Route.delete_route()

        # SMALL-ROUTES-ELIMINATION ALGORITHM

        # Initialize list for the identifier of small routes 
        route_try_to_reduce = []
        for v in self.routes.values():
            if v.load_cust <= 2:
                # if the route is a small route, we will try to eliminate it
                route_try_to_reduce.append(v.id)

        # Iterate over all small routes identifiers
        for small_route_id in route_try_to_reduce:
            # Small route object
            small_route = self.routes[small_route_id]
            # Iterate over the customers in the small route
            for cust_id in small_route.route[1:-1]:
                # Try to remove a customer from the small ruote
                feasible_route, insertion_route, small_route = self._find_best_routes_for_cust(cust_id, small_route)
                if feasible_route:
                    # We succeeded in removing the customer from the small route
                    if small_route.load_cust == 0:
                        # The small route is empty, we eliminate it
                        del self.routes[small_route_id]
                        # Decrement the number of used vehicles
                        self.num_routes -= 1
                    if insertion_route.id in route_try_to_reduce:
                        # The route in which I inserted the customer was a small route, check if it still a small route
                        if insertion_route.load_cust > 2:
                            # The route is no more a small route
                            route_try_to_reduce.remove(insertion_route.id)        
        
        # Check if the number of used vehicles is feasible
        if self.num_routes <= self.num_vehicles:
            # Iterate over the routes
            for k, v in self.routes.items():
                # Update the total cost of the initial solution
                self.total_cost += v.load_min
                # The solution is feasible because it uses a number of vehicles that is <= the number of all available vehicles
                feasible_solution = True
                # Save the small routes at the end of the algorithm
                if v.load_cust <= 2:
                    self.small_routes.append(k)
        else:
            # The initial solution is not feasible
            feasible_solution = False
        return feasible_solution    


    def print_solution(self, day, file_path='./Solution/routes.sol'):
        '''
        Save the solution on a file and compute the number of empty vehicles.

        INPUTS:
            day: object of class Day representing the current day
            [file_path]: path to the file in which the solution is saved
        OUTPUT:
            num_empty_vehicles: number of vehicles that were not used in the solution

        '''

        # Initialize the total load of all routes
        total_load = 0
        # Initialize the number of used vehicles
        num_route = 0
        # Initialize the maximum distance of a route
        max_route_distance = 0
        # Compute the number of empty vehicles
        num_empty_vehicles = constant.NUM_VEHICLES-len(self.routes)
        # Save the current day
        with open(file_path, 'a') as fp:            
            fp.write(f'\n DAY: {day.current_day} \n')
        # Iterate over all the routes in the solution
        for k, v in self.routes.items():
            route = 'Route for vehicle {}:\n'.format(num_route)
            # Increment the number of routes
            num_route += 1
            route += ' {} -> '.format(0)
            # Iterate over all customers in the route
            for cust_id in v.route:
                if cust_id !=0:
                    route += ' {} -> '.format(cust_id)
            route += ' {}\n'.format(0)
            # Update the total load
            total_load += v.load_kg
            # Save the duration of the route
            route += 'Travel and service time of the route: {} h\n'.format(round(v.load_min/60,2))
            # Save the load of the route
            route += 'Load of the route: {} kg \n'.format(round(v.load_kg,2))
            # Update the maximum distance of a route
            max_route_distance = max(max_route_distance, v.load_min)
            # Write on the file the information about the route
            with open(file_path, 'a') as fp:          
                fp.write(route)
        # Write on the file the information about all routes in the solution
        with open(file_path, 'a') as fp:    
            total_distance = self.total_cost   
            # Total duration of all routes 
            fp.write('Total travel and service time of all routes: {} h\n'.format(round(total_distance/60,2)))
            # Total load of all routes
            fp.write('Total load of all routes: {} kg\n'.format(round(total_load, 2)))
            # Maximum duration of a route
            fp.write('Maximum of the route travel time: {} h\n'.format(round(max_route_distance/60,2)))
        return num_empty_vehicles


