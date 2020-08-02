from itertools import permutations
import random
from Route import Route
import copy





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
        feasible = False
        while not feasible:
            feasible, old_cost_routes, route_1, route_2, route_ids, cust_id1, cust_id2 = self._generate_neighbourhood()
        new_cost_routes, route_1, route_2 = self._local_search(route_1, route_2)
        diff_cost = old_cost_routes - new_cost_routes
        # found a better solution: unpdate solution
        if diff_cost >= 0:
            self._update_solution(route_1, route_2, route_ids, diff_cost, cust_id1, cust_id2)


    def _generate_neighbourhood(self):
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

        feasible = cap_kg_constraint1 and cap_kg_constraint2 and cap_min_constraint2 and cap_min_constraint2

        # update routes
        old_cost_routes = route_1.load_min + route_2.load_min
        route_1.load_kg = new_load_kg1
        route_1.load_min = new_load_min1
        route_2.load_kg = new_load_kg2
        route_2.load_min = new_load_min2
        route_1.route[route_1.route.index(cust_id1)] = cust_id2
        route_2.route[route_2.route.index(cust_id2)] = cust_id1
        return feasible, old_cost_routes, route_1, route_2, route_ids, cust_id1, cust_id2
    
    def _local_search(self, route_1, route_2):
        # local search
        new_cost_routes = route_1.load_min + route_2.load_min
        best_route1, best_cost1, service_times_routes1 = self._find_best_permutation(route_1)
        best_route2, best_cost2, service_times_routes2 = self._find_best_permutation(route_2)        
        new_cost_routes = best_cost2 + best_cost1 + service_times_routes1 + service_times_routes2  
        route_1.route = best_route1
        route_2.route = best_route2
        route_1.load_min = best_cost1 + service_times_routes1
        route_2.load_min = best_cost2 + service_times_routes2
        return new_cost_routes, route_1, route_2


    def _update_solution(self, route_1, route_2, route_ids, diff_cost, cust_id1, cust_id2):
        del self.current_solution.routes[route_ids[0]]
        del self.current_solution.routes[route_ids[1]]        
        self.current_solution.route_of_customers[cust_id1] = route_2.id
        self.current_solution.route_of_customers[cust_id2] = route_1.id
        self.current_solution.routes[route_1.id] = route_1
        self.current_solution.routes[route_2.id] = route_2
        self.current_solution.total_cost -= diff_cost


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


    def _initialize_route(self, all_routes, route_id):
        route = Route()
        route.route = copy.copy(all_routes[route_id].route)
        route.load_kg = all_routes[route_id].load_kg
        route.load_min = all_routes[route_id].load_min
        route.load_cust = all_routes[route_id].load_cust
        cust_id = random.sample(route.route[1:-1], 1)[0]
        prec_cust = route.route[route.route.index(cust_id)-1]
        post_cust = route.route[route.route.index(cust_id)+1]
        cust = self.current_solution.customers[cust_id]
        return route, cust_id, prec_cust, post_cust, cust