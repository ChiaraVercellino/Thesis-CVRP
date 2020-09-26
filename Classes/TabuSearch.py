'''
This Class is used to implement the Tabu Search based meta-heuristic: it consist of one iteration of the algorithm that includes:
    - The neighbour generation by means of Swap and Inserition algorithms
    - The Local Search step to improve the convenience of the neighbour solution
    - The acceptance step that applies the Tabu Search principles

The attributes of the class are:
    perms: dictionary of all possible permutations, it has as key the number of customer on a route and as value the list of all permutations
    current_solution: it is the current solution in the considered iteration, it is an object of the class ClarkWrightSolver
    tabu_list: the list of tabu moves, i.e. yet investigated unordered routes
    violate_tabu: boolean that states whether the neighbour solution violates or not the tabu
    best_cost: total cost of the best solution found so far
    best_routes: routes of the best solution found so far
    eliminated_route: boolean that states whether the neighbour solution reduces by one the number of routes
    no_improvement: number of iterations without finding an improving solution
    max_time: time limit to perform the whole CW-TS algorithm
    small_routes_ids: list of the identifiers of the small routes

To deal with this optimization step, the following public methods can be exploited:
    solve(self)
    final_optimization(self)

'''


# import Classes
from Classes.Route import Route
from Classes.ClarkWrightSolver import ClarkWrightSolver
# import libraries
from itertools import permutations
import random
import copy
import numpy as np
# import constant for fixed values
import constant


class TabuSearch():

    def __init__(self, initial_solution, max_time):  
        '''
        Construction of class TabuSearch.
        INPUTS:
            initial_solution: object of the class  ClarkWrightSolver containing the initial feasible solution
            max_time: time limit to perform the whole CW-TS algorithm
        '''  
        # Set seed for pseudo-random sequences' generation
        random.seed(constant.SEED)
        # Initialize the empty dictionary
        self.perms = {}
        # Generate all possible permutations for local search step
        for i in range(3, constant.CUSTOMER_CAPACITY+1):
            perms = list(permutations(range(i))) 
            # eliminate identity permutation
            perms.pop(0)
            for p in perms:
                # remove anti-clockwise permutations
                if p[::-1] in perms:
                    perms.remove(p[::-1])
            self.perms[i]=perms 
        # Initialize the current solution           
        self.current_solution = initial_solution
        # Initialize the tabu list
        self.tabu_list = []
        # Initialize the boolean attributes
        self.violate_tabu = False
        self.eliminated_route = False
        # Initialize the cost of the best solution
        self.best_cost = initial_solution.total_cost
        # Initialize the routes of the best solution
        self.best_routes = copy.copy(initial_solution.routes)
        # Initialize the counter of non improving iterations
        self.no_improvement = 0
        # Set the time limit
        self.max_time = max_time  
        # Save the identifiers of small routes in the current solution     
        self.small_routes_ids = initial_solution.small_routes


# ------------------------------------------------------ PRIVATE METHODS ----------------------------------------------------------


    def _initialize_route(self, all_routes, route_id, custumer_on_route=True):
        '''
        Initialize a new route object, which is the copy of a pre-existent route. By means of flag custumer_on_route, a random customer can
        be sampled on the route.
        INPUTS:
            all_routes: dictionary of pre-existent routes
            route_id: identifier of the route to copy
            [custumer_on_route]: boolean variable that specify if a random customer should be sampled on the route, if True the random customer is
                                 sampled, if False he is not
        OUTPUTS:
            route: copy of the route object
            [cust_id]: identifier of the randomly sampled customer
            [prec_cust]: identifier of the previous customer on the route with respect to cust_id
            [post_cust]: identifier of the next customer on the route with respect to cust_id
            [cust]: customer object corresponding to cust_id

        '''
        # Istantiate a new route
        route = Route()
        # copy the route path
        route.route = copy.copy(all_routes[route_id].route)
        # copy the load of the route
        route.load_kg = all_routes[route_id].load_kg
        # copy the duration of the route
        route.load_min = all_routes[route_id].load_min
        # copy the number of customers visited by the route
        route.load_cust = all_routes[route_id].load_cust
        if custumer_on_route:
            # Randomly sample one customer on the route
            cust_id = random.sample(route.route[1:-1], 1)[0]
            # Preceding customer on the route
            prec_cust = route.route[route.route.index(cust_id)-1]
            # Next customer on the route
            post_cust = route.route[route.route.index(cust_id)+1]
            # Customer object
            cust = self.current_solution.customers[cust_id]
            return route, cust_id, prec_cust, post_cust, cust
        else:
            return route

    
    def _update_routes(self, all_routes, route_ids_no_more, routes_list, tabu_moves):
        '''
        Update the routes in the current solution, update the identifiers of the small routes and save potential tabu moves.
        INPUTS:
            all_routes: dictionary of pre-existent routes
            route_ids_no_more: identifiers of the routes that have been modified in the neighbour solution and so must be removed from all_routes
            routes_list: list of the routes generated for the neighbour solution
            tabu_moves: list of potential tabu moves
        OUTPUTS:
            all_routes: dictionary of pre-existent routes (updated)
            tabu_moves: list of potential tabu moves (updated)

        '''
        # Iterate over the new routes
        for i in range(len(routes_list)):
            # Store the potential tabu move, that is the old route path before the neighbour generation
            tabu_moves.append(all_routes[route_ids_no_more[i]].route)
            # Remove the old route from the dictionary of all routes
            del all_routes[route_ids_no_more[i]]
            # Add to the same dictionary the new route
            all_routes[routes_list[i].id] = routes_list[i] 
            # Check if the removed route was a small route           
            if route_ids_no_more[i] in self.small_routes_ids:
                # Remove old identifier from the small routes' identifiers
                self.small_routes_ids.remove(route_ids_no_more[i])
            # Check if the new route is a small one
            if 1 <= routes_list[i].load_cust <= 2:
                # Add the identifier of the new route to small routes' identifiers
                self.small_routes_ids.append(routes_list[i].id)
        return all_routes, tabu_moves


    def _update_tabu_list(self, route):
        '''
        Update the tabu list inserting a new tabu move, apply a FIFO criterion if the maximum length of the tabu list is reached.
        INPUT:
            route: unordered set of customers that belongs to a route
        '''
        # Check if the route is not yet present in the tabu list
        if route not in self.tabu_list:
            # Check if the tabu move can be added without exceeding the maximum tabu length
            if len(self.tabu_list) < constant.TABU_LENGTH:   
                # Add the tabu move         
                self.tabu_list.append(route)
            else:
                # Remove the oldest tabu move
                self.tabu_list.pop(0)
                # Add the tabu move
                self.tabu_list.append(route)


    def _accept_solution(self, all_routes, diff_cost, tabu_moves, best=False):
        '''
        Accept a solution, it could be accepted as a new current solution or as a new best solution, depending on flag best. When we accept a
        new solution we update the corresponding cost and then we add to the tabu list the tabu moves associated with the neighbour generation.
        INPUTS:
            all_routes: dictionary containing all the routes of the solution to be accepted
            diff_cost: difference between the costs of the preceding solution and the one of the solution to be accepted
            tabu_moves: list of potential tabu moves
            [best]: boolean variable that states if the accepted solution is a new best one (True) or not (False)

        '''
        # Nullify the number of non improving iterations
        self.no_improvement = 0
        if best:
            # Update the routes of the best solution
            self.best_routes = copy.copy(all_routes)
            # Update the cost of the best solution
            self.best_cost -= diff_cost
        else:
            # Update the routes of the current solution
            self.current_solution.routes = copy.copy(all_routes)
            # Update the cost of the current solution
            self.current_solution.total_cost -= diff_cost
        # Iterate over all the tabu moves
        for tabu_move in tabu_moves:
            # Add the tabu move to the tabu list
            self._update_tabu_list(set(tabu_move))           


    def _swap_neighbourhood(self, all_routes):
        '''
        Perform Swap algorithm: select two random routes and one random customer on each route, then try to swap them and see if the obtained
        routes lead to a feasible solution.
        INPUT:
            all_routes: dictionary of all the route in the current solution
        OUTPUTS:
            feasible: boolean variable that state if the obtained solution is feasible (True) or not (False)
            old_cost_routes: costs of the selected routes before the swap
            swapped_routes: list of Route objects containing the new routes after the swap
            route_ids: identifiers of the routes selected for the swap

        '''

        # Identifiers of all the routes
        all_route_ids = all_routes.keys()
        # Select two random routes' identifiers
        route_ids = random.sample(all_route_ids, k=2)
        # Copy the routes and sample one random customer on each of them, store the identifiers of the customers and of the corresponding
        # preceding and next customers on the routes
        route_1, cust_id1, prec_cust1, post_cust1, cust_1 = self._initialize_route(all_routes, route_ids[0])
        route_2, cust_id2, prec_cust2, post_cust2, cust_2 = self._initialize_route(all_routes, route_ids[1])   
        # Store the costs of the copied routes     
        old_cost_routes = route_1.load_min + route_2.load_min
        # List of the routes modified by the swap
        swapped_routes = [route_1, route_2]
        # List of customers involved in the swap
        swapped_cust = [cust_id1, cust_id2]
        # Distance matrix
        dist_matrix = self.current_solution.distance_matrix
        # Compute the new loads of the first route: only the weight and the travel time are modified, the number of visited customer is preserved
        route_1.load_kg = route_1.load_kg + cust_2.demand - cust_1.demand
        route_1.load_min = route_1.load_min + cust_2.service_time - cust_1.service_time - dist_matrix[prec_cust1][cust_id1] \
        - dist_matrix[cust_id1][post_cust1] + dist_matrix[prec_cust1][cust_id2] + dist_matrix[cust_id2][post_cust1]
        # Check if the first route is feasible
        feasible = route_1.check_constraints()
        # Compute the new loads of the second route: only the weight and the travel time are modified, the number of visited customer is preserved
        route_2.load_kg = route_2.load_kg + cust_1.demand - cust_2.demand
        route_2.load_min = route_2.load_min + cust_1.service_time - cust_2.service_time - dist_matrix[prec_cust2][cust_id2] \
        - dist_matrix[cust_id2][post_cust2] + dist_matrix[prec_cust2][cust_id1] + dist_matrix[cust_id1][post_cust2]
        # Check if also the second route is feasible
        feasible = feasible and route_2.check_constraints()        
        if feasible:
            # Update routes' paths
            route_1.route[route_1.route.index(cust_id1)] = cust_id2
            route_2.route[route_2.route.index(cust_id2)] = cust_id1
            # check if the new routes violate tabu
            if set(route_1.route) in self.tabu_list or set(route_2.route) in self.tabu_list:
                self.violate_tabu = True
        return feasible, old_cost_routes, swapped_routes, route_ids
    
    
    def _insert_neighbourhood(self, all_routes):
        '''
        Perform the Insertion algorithm: select two random routes, if possible the first one is sampled among the small routes. Then sample one
        random customer on the first route and try to insert him in the second route's path in the most convenient position. Finally check if the
        obatained routes lead to a feasible solution.
        INPUT:
            all_routes: dictionary of all the route in the current solution
        OUTPUTS:
            feasible: boolean variable that state if the obtained solution is feasible (True) or not (False)
            route_1: Route object, it is the route from which the customer is removed
            route_2: Route object, it is the route in which the customer is inserted
            route_ids: list of identifiers of the routes that have been modified by the insertion

        '''

        # Identifiers of all the routes
        all_route_ids = all_routes.keys()
        # Check if in the current solution there are some small routes        
        if self.small_routes_ids:
            # Initialize the routes' identifiers
            route_id1 = 0
            route_id2 = 0
            # Iterate until two different routes are sampled
            while route_id1 == route_id2:
                # Sample the first route among the small routes
                route_id1 = random.sample(self.small_routes_ids, k=1)[0]
                # Sample the second route
                route_id2 = random.sample(all_route_ids, k=1)[0]
            # List of the routes' identifiers selected for the insertion
            route_ids = [route_id1, route_id2]   
        else:
            # Sample two random routes
            route_ids = random.sample(all_route_ids, k=2)  
        # Create a copy of the first route and select one random customer on it, store also the identifiers of the customer and of his preceding
        # and next customer on the route's path
        route_1, cust_id, prec_cust1, post_cust1, cust = self._initialize_route(all_routes, route_ids[0])
        # Create a copy of the second route
        route_2 = self._initialize_route(all_routes, route_ids[1], custumer_on_route=False)
        # Compute the new weight of the second route
        new_load_kg2 = route_2.load_kg + cust.demand
        # Check whether the new weight exceed the capacity
        cap_kg_constraint2 = new_load_kg2 <= route_2.cap_kg
        # Update the number of visited customers on the second route
        new_load_cust2 = route_2.load_cust +1
        # Check whether the new customers-load exceed the customers-capacity
        cap_cust_constraint = new_load_cust2 <= route_2.cap_cust
        # Initialize the flag
        feasible = False
        # Check if both the constraints are met
        if cap_kg_constraint2 and cap_cust_constraint:
            # Distance matrix
            dist_matrix = self.current_solution.distance_matrix
            # Calculate the new loads for the first
            new_load_kg1 = route_1.load_kg - cust.demand
            new_load_cust1 = route_1.load_cust -1
            new_load_min1 = route_1.load_min - cust.service_time - dist_matrix[prec_cust1][cust_id] \
            - dist_matrix[cust_id][post_cust1] + dist_matrix[prec_cust1][post_cust1]
            # Try to insert the customer in the best position: look for the nearest customer on the second route and put the customer after it
            # Distances between the customer of the first route and the locations of the second route
            distances  = np.array([dist_matrix[cust_id][i] for i in route_2.route])
            # Index associated with the lower distance
            best_idx = np.argpartition(distances, 1) 
            # Customer on the second route that will preceed the inserted customer
            prec_cust2 = route_2.route[best_idx[0]]
            # Customer on the second route that will come next the inserted customer
            post_cust2 = route_2.route[best_idx[0]+1]
            # Compute the new duration of the second route
            new_load_min2 = route_2.load_min + cust.service_time - dist_matrix[prec_cust2][post_cust2] \
            + dist_matrix[prec_cust2][cust_id] + dist_matrix[cust_id][post_cust2]
            # Check if the time-constraint of the second route is met
            cap_min_constraint2 = new_load_min2 <= route_2.cap_min
            # Update the flag
            feasible = cap_min_constraint2
            if feasible:
                # Update the loads of the first route
                route_1.load_kg = new_load_kg1
                route_1.load_min = new_load_min1
                route_1.load_cust -= 1
                # Update the load of the second route
                route_2.load_kg = new_load_kg2
                route_2.load_min = new_load_min2
                route_2.load_cust += 1
                # Update the path of the first route
                route_1.route.remove(cust_id)
                # Update the path of the second route
                route_2.route = route_2.route[:best_idx[0]+1]+[cust_id]+route_2.route[best_idx[0]+1:]
                # Check if the the new routes violate the tabu
                if set(route_1.route) in self.tabu_list or set(route_2.route) in self.tabu_list:
                    self.violate_tabu = True
        return feasible, route_1, route_2, route_ids


    def _local_search(self, route, final=False):
        '''
        Perform the Local Search step on a route modified by neighbourhood functions, find a pseudo-best path for the considered route and
        compute the corresponding cost.
        INPUTS:
            route: Route object of the route on which the Local Search is performed
            [final]: flag that states if the Local Search to perform is the one at the end of the CW-TS algorithm (True) or it is the one
                     that is done in the standard iterations (False)
        OUTPUT:
            route: Route object of the post-optimized and update route
        '''
        # Find the best path, the lower cost of the route by analysing its permuation, store the total service times of the route
        best_route, best_cost, service_times_routes = self._find_best_permutation(route, final)
        # Update the route's path
        route.route = best_route
        # Update the duration of the route
        route.load_min = best_cost + service_times_routes
        return route


    def _find_best_permutation(self, route, final):
        '''
        Given a route path, find the permutation that lead to the lowest travel cost. If we are performing the final optmization of the CW-TS
        algorthm we try all the permutations also for the 5-customers route, otherwise, for those routes, only a subset of the permutations is
        investigated.
        INPUTS:
            route: Route object of the route to be optimized
            final: flag that states if the optimization is the final one (True) or it the Local Search one (False)
        OUTPUTS:
            best_route: path of the best route
            best_cost: travel cost of the best route
            service_times_routes: total service time of the route

        '''

        # Initialize the total service time
        service_times_routes = 0
        # Consider all customers' locations of the route, the first and the last locations in the path must be the depot ones
        route_list = route.route[1:-1]
        # Iterate over customers in the route
        for c in route_list:
            # Update the total service time
            service_times_routes += self.current_solution.customers[c].service_time
        # Travel cost associated with the current order to visit customers on the route
        best_cost = route.load_min - service_times_routes
        # Current path of the route
        best_route = route.route
        # Distance matrix
        dist_matrix = self.current_solution.distance_matrix
        # Only the routes with more than 3 customers can be permutated
        if route.load_cust >= 3:
            # List of all the permutation, given the number of customers in the route
            all_permutation = self.perms[route.load_cust]
            if not final:
                # Local Search optimization
                # Total number of permutations
                total_permutation = len(all_permutation)
                # There is a limit to the number of permutations to try
                if total_permutation >= constant.NUM_PERM:
                    # Sample some random permutations
                    all_permutation = random.sample(all_permutation, constant.NUM_PERM)
            # Iterate over the permutations
            for perm in all_permutation:
                # Permutated route's path
                new_route = [0]+[route_list[x] for x in perm]+[0]
                # Initialize the cost of the permutated route
                route_cost = 0
                for i in range(route.load_cust+1):
                    # Add travel cost
                    route_cost += dist_matrix[new_route[i]][new_route[i+1]]
                    # If the route cost is greater than the best cost, exit the inner for cycle
                    if route_cost>=best_cost:
                        break
                # Check if the route cost is the best found so far
                if route_cost < best_cost: 
                    # Update the best route's path            
                    best_route = new_route
                    # Update the best route's cost
                    best_cost = route_cost
        return best_route, best_cost, service_times_routes      
    

    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------


    def solve(self):    
        '''
        Perform one iteration of the CW-TS algorithm.

        '''              
        
        # INITIALIZATIONS

        # Copy the list of the small routes' identifiers
        current_small_routes_ids = copy.copy(self.small_routes_ids) 
        # Copy the dictionary of all routes 
        all_routes = copy.copy(self.current_solution.routes)
        # Initialize the flag
        feasible_swap = False

        # SWAP ALGORITHM

        # Iterate until feasibility is reached
        while not feasible_swap: 
            # Generate neighbourhood by swapping customers      
            feasible_swap, old_cost_routes, swapped_routes, route_ids_no_more = self._swap_neighbourhood(all_routes)
        # Initialize the list of tabu moves for the neighbour solution
        tabu_moves = []
        # Update the routes modified by the swap
        all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more, swapped_routes, tabu_moves)
        # Store the identifiers of the routes modified by the swap
        modified_routes_id = []
        for route_swap in swapped_routes:            
            modified_routes_id.append(route_swap.id)
        # Convert to unordered set to avoid duplications
        all_modified_routes = set(modified_routes_id)

        # INSERTION ALGORITHM

        # Generate the neighbourhood by the insertion
        feasible_insertion, route1_ins, route2_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)        
        # Check if inserion has led to a feasible solution
        if feasible_insertion:
            # Update the routes modified by the insertion
            all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more_ins, [route1_ins, route2_ins], tabu_moves)
            # Check if the insertion has eliminated a route
            if route1_ins.load_cust==0:
                # Remove the empty route
                del all_routes[route1_ins.id]
                # Update the flag
                self.eliminated_route = True
                # Set of all the route that have been modified in the neighbour solution
                all_modified_routes = all_modified_routes.union(set([route2_ins.id])).difference(set(route_ids_no_more_ins))  
            else:
                # Set of all the route that have been modified in the neighbour solution
                all_modified_routes = all_modified_routes.union(set([route2_ins.id, route1_ins.id])).difference(set(route_ids_no_more_ins))
            
        # LOCAL SEARCH

        # Initialize the cost of the neighbour solution
        new_cost_routes = 0   
        # Iterate over the modified routes     
        for id_route in all_modified_routes:
            # Apply local search
            best_route = self._local_search(all_routes[id_route])
            # Update the best path for the modified route
            all_routes[id_route] = best_route
            # Update the total cost of the modified routes
            new_cost_routes += best_route.load_min
        # Compute the costs' variation with respect to the current solution due to the new routes
        diff_cost = old_cost_routes - new_cost_routes
        # Compute the cost of the neighbour solution 
        neighbour_cost = self.current_solution.total_cost - diff_cost
        # Compute the costs' variation with respect to the best solution due to the new routes
        diff_cost_best = self.best_cost - neighbour_cost

        # ACCEPTANCE STEP

        # The neighbour solution reduces the cost of the current solution and it does not violate the tabu or it eliminates a route
        if diff_cost >= 0 and not(self.violate_tabu) or self.eliminated_route:
            # Accept the neighbour solution as a new current solution 
            self._accept_solution(all_routes, diff_cost, tabu_moves)
            # Check if the neighbour solution is also a best solution
            if diff_cost_best > 0 or self.eliminated_route:
                # Update the cost of the best solution
                self.best_cost = neighbour_cost
                # Update the routes of the best solution
                self.best_routes = copy.copy(self.current_solution.routes)   
        # Check if the neighbour solution activates the aspiration criterion: it is associated with the best costs found so far or it reduces
        # the number of vehicles, even if it violates the tabu   
        elif diff_cost_best > 0 or self.eliminated_route:
            # The current solution is not updated, so the identifiers of the small routes are the ones stored at the begining
            self.small_routes_ids = copy.copy(current_small_routes_ids)
            # Accept the new best solution
            self._accept_solution(all_routes, diff_cost, tabu_moves, best=True) 
        # Check if the neighbour solution does not violate the tabu and we have not accepted a solution in the last GAP-WORSE iterations                         
        elif not(self.violate_tabu) and self.no_improvement >= constant.GAP_WORSE:
            # Accept a worsening solution as current solution
            self._accept_solution(all_routes, diff_cost, tabu_moves)
        # Refuse the neighbour solution
        else:
            # Increment the number of non improving iterations
            self.no_improvement += 1
            # Restore the small routes' identifiers
            self.small_routes_ids = copy.copy(current_small_routes_ids)
        # Reset flags
        self.violate_tabu = False
        self.eliminated_route = False


    def final_optimization(self):
        '''
        Perform the final optimization over all the routes in the best solution: try all the permutations of all the routes and choose the ones
        associated with the lowest travel costs.

        '''

        # Route of the best solution
        all_routes = self.best_routes
        # Initilialize the total travel and service cost for all the routes
        self.current_solution.total_cost = 0
        # Iterate over the routes
        for id_route, route in all_routes.items():
            # Find the best path to visit the customers on the route
            best_route = self._local_search(route, final=True)
            # Store the best route
            all_routes[id_route] = best_route
            # Update the total cost
            self.current_solution.total_cost += best_route.load_min
        # Update the current solution with the best one
        self.current_solution.routes = all_routes
