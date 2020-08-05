from itertools import permutations
import random
import copy
import numpy as np
from Route import Route
from ClarkWrigthSolver import ClarkWrightSolver


class TabuSearch():

    def __init__(self, initial_solution):    
        # generate all possible permutation for local search step
        random.seed(793)
        self.perms = {}
        for i in [3,4,5]:
            perms = list(permutations(range(1, i+1))) 
            for p in perms:
                # remove anti-clockwise permutations
                if p[::-1] in perms:
                    perms.remove(p[::-1])
            self.perms[i]=perms
        self.current_solution = initial_solution
        self.tabu_list = {}
        self.tabu_lenght = initial_solution.num_customers
        self.violate_tabu = 0
        self.best_cost = initial_solution.total_cost
        self.best_routes = copy.copy(initial_solution.routes)
        self.best_route_of_customer = copy.copy(initial_solution.route_of_customers)
        self.route_to_eliminate = None
        self.eliminated_route = False


    def solve(self):
        # copy of the routes
        all_routes = copy.copy(self.current_solution.routes)

        feasible_swap = False
        # generate neighbourhood by swapping customers
        while not feasible_swap:
            feasible_swap, old_cost_routes, route1_swap, route2_swap, route_ids_no_more, cust_id1, cust_id2 = self._swap_neighbourhood(all_routes)
        
        # update tabù list
        self._update_tabu_list(route1_swap, cust_id1)
        self._update_tabu_list(route2_swap, cust_id2)
        
        if route1_swap.load_cust == 1:
            self.route_to_eliminate = route1_swap.id
        if route2_swap.load_cust == 1:
            self.route_to_eliminate = route2_swap.id
        # those routes have been modified by swap
        all_routes = self._update_routes(all_routes, route_ids_no_more, route1_swap, route2_swap)
        all_modified_routes = [route1_swap.id, route2_swap.id]

        # generate neighbourhood by inserting a customer in another route
        feasible_insertion = False
        while not feasible_insertion:
            feasible_insertion, route1_ins, route2_ins, cust_id_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)
        

        if feasible_insertion:
            if route1_ins.load_cust == 1:
                self.route_to_eliminate = route1_ins.id
            # those routes have been modified by insertion
            all_routes = self._update_routes(all_routes, route_ids_no_more_ins, route1_ins, route2_ins)
            if self.route_to_eliminate:
                del all_routes[self.route_to_eliminate]
                self.route_to_eliminate = None
                self.eliminated_route = True
                all_modified_routes = set([route1_swap.id, route2_swap.id, route2_ins.id]).difference(set(route_ids_no_more_ins))
            else:
                all_modified_routes = set([route1_swap.id, route2_swap.id, route1_ins.id, route2_ins.id]).difference(set(route_ids_no_more_ins))
            # update tabù list
            self._update_tabu_list(route1_ins, cust_id_ins)
        # calculate cost of new solution
        new_cost_routes = 0        
        for id_route in all_modified_routes:
            best_route = self._local_search(all_routes[id_route])
            all_routes[id_route] = best_route
            new_cost_routes += best_route.load_min
        diff_cost = old_cost_routes - new_cost_routes
        current_cost = self.current_solution.total_cost - diff_cost
        diff_cost_best = self.best_cost - current_cost
        # found a better solution: update solution
        if (diff_cost >= 0 and self.violate_tabu<2) or self.eliminated_route:
            self.eliminated_route = False
            print('old cost {} - current cost {} - best cost {}'.format(self.current_solution.total_cost, current_cost, self.best_cost))
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
            self.current_solution.route_of_customers[cust_id1] = route2_swap.id
            self.current_solution.route_of_customers[cust_id2] = route1_swap.id
            if feasible_insertion:
                self.current_solution.route_of_customers[cust_id_ins] = route2_ins.id
            if diff_cost_best >= 0:
                self.best_cost = current_cost
                self.best_routes = copy.copy(self.current_solution.routes)
                self.best_route_of_customer = copy.copy(self.current_solution.route_of_customers)
        elif diff_cost_best > 0:
            print('best')  
            # mi trova sempre la stessa soluzione    
            self.best_routes = copy.copy(all_routes)
            self.best_cost = current_cost
            self.best_route_of_customer[cust_id1] = route2_swap.id
            self.best_route_of_customer[cust_id2] = route1_swap.id
            if feasible_insertion:
                self.best_route_of_customer[cust_id_ins] = route2_ins.id
        elif self.violate_tabu>=2 and (len(self.tabu_list)>=self.tabu_lenght):
            print('accept worse')
            self.iter_no_improvement = 0
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
            self.current_solution.route_of_customers[cust_id1] = route2_swap.id
            self.current_solution.route_of_customers[cust_id2] = route1_swap.id
            if feasible_insertion:
                self.current_solution.route_of_customers[cust_id_ins] = route2_ins.id
        self.violate_tabu = 0
                

    def final_optimization(self):
        print(self.best_cost)
        self.current_solution.total_cost = self.best_cost
        self.current_solution.routes = self.best_routes
        self.current_solution.route_of_customers = self.best_route_of_customer
        all_routes = self.current_solution.routes
        # find best configuration for all routes
        self.current_solution.total_cost = 0
        for id_route, route in all_routes.items():
            best_route = self._local_search(route)
            all_routes[id_route] = best_route
            self.current_solution.total_cost += route.load_min
        print(self.current_solution.total_cost)

# ------------------------------------------------------ PRIVATE METHODS ----------------------------------------------------------

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

    @staticmethod
    def _update_routes(all_routes, route_ids_no_more, route1, route2):
        del all_routes[route_ids_no_more[0]]
        del all_routes[route_ids_no_more[1]]
        all_routes[route1.id] = route1
        all_routes[route2.id] = route2
        return all_routes

    def _update_tabu_list(self, route, customer):
        if len(self.tabu_list) < self.tabu_lenght:
            self.tabu_list[customer]=set(route.route)
        else:
            element_to_remove = list(self.tabu_list.keys())[0] 
            del self.tabu_list[element_to_remove]

    def _swap_neighbourhood(self, all_routes):
        all_route_ids =all_routes.keys()
        # select 2 random routes and 2 random customer
        route_ids = random.sample(all_route_ids, k=2)
        route_1, cust_id1, prec_cust1, post_cust1, cust_1 = self._initialize_route(all_routes, route_ids[0])
        route_2, cust_id2, prec_cust2, post_cust2, cust_2 = self._initialize_route(all_routes, route_ids[1])
        if cust_id1 in self.tabu_list:
            if self.tabu_list[cust_id1] == set(route_2.route):
                self.violate_tabu += 1
        if cust_id2 in self.tabu_list:
            if self.tabu_list[cust_id2] == set(route_1.route):
                self.violate_tabu += 1
        
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
        # select 2 random routes and 2 random customer 
        route_ids = [0, 0]       
        weight_for_route_big = []
        for route_id, route_obj in all_routes.items():
            weight_for_route_big.append(route_obj.load_min)
        route_ids[0] = random.choices(list(all_route_ids), weights=weight_for_route_big, k=1)
        route_ids[1] = random.sample(all_route_ids, k=1)
        while route_ids[0] == route_ids[1]:
            route_ids[0] = random.choices(list(all_route_ids), weights=weight_for_route_big, k=1)
            route_ids[1] = random.sample(all_route_ids, k=1)
        if self.route_to_eliminate:
            if self.route_to_eliminate == route_ids[1]:
                route_ids[1] = route_ids[0]
                route_ids[0] = self.route_to_eliminate
            else: 
                route_ids[0] = self.route_to_eliminate
        route_ids = sum(route_ids, [])
        route_1, cust_id, prec_cust1, post_cust1, cust = self._initialize_route(all_routes, route_ids[0])
        if self.route_to_eliminate:
            self.route_to_eliminate = route_1.id
        route_2 = self._initialize_route(all_routes, route_ids[1], custumer_on_route=False)

        if cust_id in self.tabu_list:
            if self.tabu_list[cust_id] == set(route_2.route):
                self.violate_tabu += 1
        dist_matrix = self.current_solution.distance_matrix
        # calculate new loads for ruote 1
        new_load_kg1 = route_1.load_kg - cust.demand
        new_load_cust1 = route_1.load_cust -1
        new_load_min1 = route_1.load_min - cust.service_time - dist_matrix[prec_cust1][cust_id] \
        - dist_matrix[cust_id][post_cust1] + dist_matrix[prec_cust1][post_cust1]
        # check if the insertion is feasible
        new_load_kg2 = route_2.load_kg + cust.demand
        cap_kg_constraint2 = new_load_kg2 <= route_2.cap_kg
        new_load_cust2 = route_2.load_cust +1
        cap_cust_constraint = new_load_cust2 <= route_2.cap_cust
        # I try to insert the customer in the best position: look for the nearest customer on route2, I'll put the new customer after it
        distances  = np.array([dist_matrix[cust_id][i] for i in route_2.route])
        best_idx = np.argpartition(distances, 1) 
        prec_cust2 = route_2.route[best_idx[0]]
        post_cust2 = route_2.route[best_idx[0]+1]
        new_load_min2 = route_2.load_min + cust.service_time - dist_matrix[prec_cust2][post_cust2] \
        + dist_matrix[prec_cust2][cust_id] + dist_matrix[cust_id][post_cust2]
        cap_min_constraint2 = new_load_min2 <= route_2.cap_min
        feasible = cap_kg_constraint2 and cap_min_constraint2 and cap_cust_constraint
        # update routes
        route_1.load_kg = new_load_kg1
        route_1.load_min = new_load_min1
        route_1.load_cust -= 1
        route_2.load_kg = new_load_kg2
        route_2.load_min = new_load_min2
        route_2.load_cust += 1
        route_1.route.remove(cust_id)
        route_2.route = route_2.route[:best_idx[0]+1]+[cust_id]+route_2.route[best_idx[0]+1:]
        return feasible, route_1, route_2, cust_id, route_ids

    def _local_search(self, route, final=False):
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
        if route.load_cust >= 3:
            for perm in self.perms[route.load_cust]:
                new_route = [0]+[route.route[i] for i in perm]+[0]
                route_cost = 0
                for i in range(len(new_route)-1):
                    route_cost += self.current_solution.distance_matrix[new_route[i]][new_route[i+1]]
                if route_cost < best_cost:             
                    best_route = new_route
                    best_cost = route_cost
        return best_route, best_cost, service_times_routes
