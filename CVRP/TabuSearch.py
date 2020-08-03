from itertools import permutations
import random
from Route import Route
from ClarkWrigthSolver import ClarkWrightSolver
import copy
import numpy as np




class TabuSearch():

    def __init__(self, initial_solution):    
        # generate all possible permutation for local search step
        random.seed(10)
        self.perms = {}
        for i in [2,3,4,5,6]:
            perms = list(permutations(range(1, i+1))) 
            for p in perms:
                # remove anti-clockwise permutations
                if p[::-1] in perms:
                    perms.remove(p[::-1])
            self.perms[i]=perms
        self.current_solution = initial_solution


    def solve(self):
        feasible_swap = False

        # generate neighbourhood by swapping customers
        while not feasible_swap:
            feasible_swap, old_cost_routes, route1_swap, route2_swap, route_ids_no_more, cust_id1, cust_id2 = self._swap_neighbourhood()
        
        # copy of the updated route
        all_routes = copy.copy(self.current_solution.routes)
        all_routes[route1_swap.id] = route1_swap
        all_routes[route2_swap.id] = route2_swap        
        # those routes have been modified by swap
        del all_routes[route_ids_no_more[0]]
        del all_routes[route_ids_no_more[1]]
        route_1 = route1_swap
        route_2 = route2_swap
        all_modified_routes = [route1_swap.id, route2_swap.id]

        # generate neighbourhood by inserting a customer in another route
        feasible_insertion, route1_ins, route2_ins, cust_id_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)
        if feasible_insertion:
            # those routes have been modified by swap
            del all_routes[route_ids_no_more_ins[0]]
            del all_routes[route_ids_no_more_ins[1]]
            all_routes[route1_ins.id] = route1_ins
            all_routes[route2_ins.id] = route2_ins 
            all_modified_routes = set([route1_swap.id, route2_swap.id, route1_ins.id, route2_ins.id]).difference(set(route_ids_no_more_ins))

        # calculate cost of new solution
        new_cost_routes = 0        
        for id_route in all_modified_routes:
            best_route = self._local_search(all_routes[id_route])
            all_routes[id_route] = best_route
            new_cost_routes += best_route.load_min

        diff_cost = old_cost_routes - new_cost_routes
        # found a better solution: unpdate solution
        if diff_cost >= 0:
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
            self.current_solution.route_of_customers[cust_id1] = route2_swap.id
            self.current_solution.route_of_customers[cust_id2] = route1_swap.id
            if feasible_insertion:
                self.current_solution.route_of_customers[cust_id_ins] = route2_ins.id
                


    def _swap_neighbourhood(self):
        all_routes = self.current_solution.routes
        all_route_ids =all_routes.keys()
        # select 2 random routes and 2 random customer
        route_ids = random.sample(all_route_ids, 2)
        route_1, cust_id1, prec_cust1, post_cust1, cust_1 = self._initialize_route(all_routes, route_ids[0])
        route_2, cust_id2, prec_cust2, post_cust2, cust_2 = self._initialize_route(all_routes, route_ids[1])
        
        dist_matrix = self.current_solution.distance_matrix
        # check if the swap is feasible
        new_load_kg1 = route_1.load_kg + cust_2.demand - cust_1.demand
        cap_kg_constraint1 = new_load_kg1 <= route_1.cap_kg
        new_load_min1 = route_1.load_min + cust_2.service_time - cust_1.service_time - dist_matrix[prec_cust1][cust_id1] \
        - dist_matrix[cust_id1][post_cust1] + dist_matrix[prec_cust1][cust_id2] + dist_matrix[cust_id2][post_cust1]
        cap_min_constraint1 = new_load_min1 <= route_1.cap_min

        new_load_kg2 = route_2.load_kg + cust_1.demand - cust_2.demand
        cap_kg_constraint2 = new_load_kg2 <= route_2.cap_kg
        new_load_min2 = route_2.load_min + cust_1.service_time - cust_2.service_time - dist_matrix[prec_cust2][cust_id2] \
        - dist_matrix[cust_id2][post_cust2] + dist_matrix[prec_cust2][cust_id1] + dist_matrix[cust_id1][post_cust2]
        cap_min_constraint2 = new_load_min2 <= route_2.cap_min

        feasible = cap_kg_constraint1 and cap_kg_constraint2 and cap_min_constraint1 and cap_min_constraint2

        # update routes
        old_cost_routes = route_1.load_min + route_2.load_min
        route_1.load_kg = new_load_kg1
        route_1.load_min = new_load_min1
        route_2.load_kg = new_load_kg2
        route_2.load_min = new_load_min2
        route_1.route[route_1.route.index(cust_id1)] = cust_id2
        route_2.route[route_2.route.index(cust_id2)] = cust_id1
        return feasible, old_cost_routes, route_1, route_2, route_ids, cust_id1, cust_id2
    

    def _insert_neighbourhood(self, all_routes):
        all_route_ids = all_routes.keys()
        # select 2 random routes: try to move customer on first route in the second one
        route_ids = random.sample(all_route_ids, 2)
        route_1, cust_id, prec_cust1, post_cust1, cust = self._initialize_route(all_routes, route_ids[0])
        route_2 = self._initialize_route(all_routes, route_ids[1], custumer_on_route=False)

        dist_matrix = self.current_solution.distance_matrix
        # calculate new loads for ruote 1
        new_load_kg1 = route_1.load_kg - cust.demand
        new_load_min1 = route_1.load_min - cust.service_time - dist_matrix[prec_cust1][cust_id] \
        - dist_matrix[cust_id][post_cust1] + dist_matrix[prec_cust1][post_cust1]
        # check if the insertion is feasible
        new_load_kg2 = route_2.load_kg + cust.demand
        cap_kg_constraint2 = new_load_kg2 <= route_2.cap_kg
        # I try to insert the customer in the best position: look for the nearest customer on route2, I'll put the new customer after it
        distances  = np.array([dist_matrix[cust_id][i] for i in route_2.route[0:-1]])
        best_idx = np.argpartition(distances, 1) 
        prec_cust2 = route_2.route[best_idx[0]]
        post_cust2 = route_2.route[best_idx[0]+1]
        new_load_min2 = route_2.load_min + cust.service_time - dist_matrix[prec_cust2][post_cust2] \
        + dist_matrix[prec_cust2][cust_id] + dist_matrix[cust_id][post_cust2]
        cap_min_constraint2 = new_load_min2 <= route_2.cap_min
        feasible = cap_kg_constraint2 and cap_min_constraint2
        # update routes
        route_1.load_kg = new_load_kg1
        route_1.load_min = new_load_min1
        route_2.load_kg = new_load_kg2
        route_2.load_min = new_load_min2
        route_1.route.remove(cust_id)
        route_2.route = route_2.route[:best_idx[0]]+[cust_id]+route_2.route[best_idx[0]+1:]
        return feasible, route_1, route_2, cust_id, route_ids

    def _local_search(self, route):
        # local search
        new_cost_routes = route.load_min
        best_route, best_cost, service_times_routes = self._find_best_permutation(route)
        route.route = best_route
        route.load_min = best_cost + service_times_routes
        return route

    def _find_best_permutation(self, route):
        service_times_routes = 0
        for c in route.route[1:-1]:
            service_times_routes += self.current_solution.customers[c].service_time
        best_cost = route.load_min - service_times_routes
        best_route = route.route
        for perm in self.perms[route.load_cust]:
            new_route = [0]+[route.route[i] for i in perm]+[0]
            route_cost = 0
            for i in range(len(new_route)-1):
                route_cost += self.current_solution.distance_matrix[new_route[i]][new_route[i+1]]
            if route_cost < best_cost:             
                best_route = new_route
                best_cost = route_cost
        return best_route, best_cost, service_times_routes


    def _initialize_route(self, all_routes, route_id, custumer_on_route=True):
        route = Route()
        route.route = copy.copy(all_routes[route_id].route)
        route.load_kg = all_routes[route_id].load_kg
        route.load_min = all_routes[route_id].load_min
        route.load_cust = all_routes[route_id].load_cust
        if custumer_on_route:
            cust_id = random.sample(route.route[1:-1], 1)[0]
            prec_cust = route.route[route.route.index(cust_id)-1]
            post_cust = route.route[route.route.index(cust_id)+1]
            cust = self.current_solution.customers[cust_id]
            return route, cust_id, prec_cust, post_cust, cust
        else:
            return route
