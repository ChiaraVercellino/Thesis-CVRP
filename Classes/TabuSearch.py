from itertools import permutations
import random
import copy
import numpy as np
from Classes.Route import Route
from Classes.ClarkWrightSolver import ClarkWrightSolver
import constant


class TabuSearch():

    def __init__(self, initial_solution, max_time):    
        random.seed(constant.SEED)
        # generate all possible permutation for local search step
        self.perms = {}
        for i in range(3, constant.CUSTOMER_CAPACITY+1):
            perms = list(permutations(range(i))) 
            perms.pop(0)
            for p in perms:
                # remove anti-clockwise permutations
                if p[::-1] in perms:
                    perms.remove(p[::-1])
            self.perms[i]=perms            
        self.current_solution = initial_solution
        self.tabu_list = []
        self.violate_tabu = False
        self.best_cost = initial_solution.total_cost
        self.best_routes = copy.copy(initial_solution.routes)
        self.eliminated_route = False
        self.no_improvement = 0
        self.max_time = max_time       
        self.small_routes_ids = initial_solution.small_routes

    def solve(self):                  
         
        current_small_routes_ids = copy.copy(self.small_routes_ids)  
        all_routes = copy.copy(self.current_solution.routes)

        feasible_swap = False
        # generate neighbourhood by swapping customers
        while not feasible_swap:       
            feasible_swap, old_cost_routes, swapped_routes, route_ids_no_more = self._swap_neighbourhood(all_routes)
        
        tabu_moves = []
        all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more, swapped_routes, tabu_moves)

        # these routes have been modified by swap
        modified_routes_id = []
        for route_swap in swapped_routes:            
            modified_routes_id.append(route_swap.id)

        all_modified_routes = set(modified_routes_id)

        feasible_insertion, route1_ins, route2_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)        
        
        if feasible_insertion:
            # those routes have been modified by insertion
            all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more_ins, [route1_ins, route2_ins], tabu_moves)
            if route1_ins.load_cust==0:
                del all_routes[route1_ins.id]
                self.eliminated_route = True
                all_modified_routes = all_modified_routes.union(set([route2_ins.id])).difference(set(route_ids_no_more_ins))  
                self.route_to_eliminate = None
            else:
                all_modified_routes = all_modified_routes.union(set([route2_ins.id, route1_ins.id])).difference(set(route_ids_no_more_ins))
            
        
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
        if diff_cost >= 0 and not(self.violate_tabu) or self.eliminated_route: 
            self._accept_solution(all_routes, diff_cost, tabu_moves)
            if diff_cost_best > 0 or self.eliminated_route:
                self.best_cost = current_cost
                self.best_routes = copy.copy(self.current_solution.routes)   
            
        elif diff_cost_best > 0 or self.eliminated_route:
            self.small_routes_ids = copy.copy(current_small_routes_ids)
            self._accept_solution(all_routes, diff_cost, tabu_moves, best=True)                          
        elif not(self.violate_tabu) and self.no_improvement >= constant.GAP_WORSE:
            self._accept_solution(all_routes, diff_cost, tabu_moves)
        
        else:
            self.no_improvement += 1
            self.small_routes_ids = copy.copy(current_small_routes_ids)
        
        self.violate_tabu = False
        self.eliminated_route = False


    def final_optimization(self):
        all_routes = self.best_routes
        # find best configuration for all routes
        self.current_solution.total_cost = 0
        for id_route, route in all_routes.items():
            best_route = self._local_search(route, final=True)
            all_routes[id_route] = best_route
            self.current_solution.total_cost += best_route.load_min
        self.current_solution.routes = all_routes

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

    
    def _update_routes(self, all_routes, route_ids_no_more, routes_list, tabu_moves):
        for i in range(len(routes_list)):
            tabu_moves.append(all_routes[route_ids_no_more[i]].route)
            del all_routes[route_ids_no_more[i]]
            all_routes[routes_list[i].id] = routes_list[i]            
            if route_ids_no_more[i] in self.small_routes_ids:
                self.small_routes_ids.remove(route_ids_no_more[i])
            if 1 <= routes_list[i].load_cust <= 2:
                self.small_routes_ids.append(routes_list[i].id)
        return all_routes, tabu_moves


    def _update_tabu_list(self, route):
        if route not in self.tabu_list:
            if len(self.tabu_list) < constant.TABU_LENGTH:            
                self.tabu_list.append(route)
            else:
                self.tabu_list.pop(0)
                self.tabu_list.append(route)


    def _accept_solution(self, all_routes, diff_cost, tabu_moves, best=False):
        self.no_improvement = 0
        if best:
            self.best_routes = copy.copy(all_routes)
            self.best_cost -= diff_cost
        else:
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
        
        for tabu_move in tabu_moves:
            self._update_tabu_list(set(tabu_move))           


    def _swap_neighbourhood(self, all_routes):
        all_route_ids = all_routes.keys()
        # select 2 random routes and 2 random customer
        route_ids = random.sample(all_route_ids, k=2)
        route_1, cust_id1, prec_cust1, post_cust1, cust_1 = self._initialize_route(all_routes, route_ids[0])
        route_2, cust_id2, prec_cust2, post_cust2, cust_2 = self._initialize_route(all_routes, route_ids[1])        
        old_cost_routes = route_1.load_min + route_2.load_min
        swapped_routes = [route_1, route_2]
        swapped_cust = [cust_id1, cust_id2]
        
        dist_matrix = self.current_solution.distance_matrix
        # check if the swap is feasible
        route_1.load_kg = route_1.load_kg + cust_2.demand - cust_1.demand
        route_1.load_min = route_1.load_min + cust_2.service_time - cust_1.service_time - dist_matrix[prec_cust1][cust_id1] \
        - dist_matrix[cust_id1][post_cust1] + dist_matrix[prec_cust1][cust_id2] + dist_matrix[cust_id2][post_cust1]
        feasible = route_1.check_constraints()

        route_2.load_kg = route_2.load_kg + cust_1.demand - cust_2.demand
        route_2.load_min = route_2.load_min + cust_1.service_time - cust_2.service_time - dist_matrix[prec_cust2][cust_id2] \
        - dist_matrix[cust_id2][post_cust2] + dist_matrix[prec_cust2][cust_id1] + dist_matrix[cust_id1][post_cust2]
        feasible = feasible and route_2.check_constraints()
        
        if feasible:
            # update routes
            route_1.route[route_1.route.index(cust_id1)] = cust_id2
            route_2.route[route_2.route.index(cust_id2)] = cust_id1
            # check if it violates tabu
            if set(route_1.route) in self.tabu_list or set(route_2.route) in self.tabu_list:
                self.violate_tabu = True

        return feasible, old_cost_routes, swapped_routes, route_ids
    
    
    def _insert_neighbourhood(self, all_routes):
        all_route_ids = all_routes.keys()
        
        # select 2 random routes and 2 random customer
        if self.small_routes_ids:
            #big_route_ids = list(set(all_route_ids).difference(set(self.small_routes_ids)))
            route_id1 = 0
            route_id2 = 0
            while route_id1 == route_id2:
                route_id1 = random.sample(self.small_routes_ids, k=1)[0]
                route_id2 = random.sample(all_route_ids, k=1)[0]
            route_ids = [route_id1, route_id2]   
        else:
            route_ids = random.sample(all_route_ids, k=2)  

        route_1, cust_id, prec_cust1, post_cust1, cust = self._initialize_route(all_routes, route_ids[0])
        route_2 = self._initialize_route(all_routes, route_ids[1], custumer_on_route=False)

        new_load_kg2 = route_2.load_kg + cust.demand
        cap_kg_constraint2 = new_load_kg2 <= route_2.cap_kg
        new_load_cust2 = route_2.load_cust +1
        cap_cust_constraint = new_load_cust2 <= route_2.cap_cust
        feasible = False

        if cap_kg_constraint2 and cap_cust_constraint:
            dist_matrix = self.current_solution.distance_matrix
            # calculate new loads for ruote 1
            new_load_kg1 = route_1.load_kg - cust.demand
            new_load_cust1 = route_1.load_cust -1
            new_load_min1 = route_1.load_min - cust.service_time - dist_matrix[prec_cust1][cust_id] \
            - dist_matrix[cust_id][post_cust1] + dist_matrix[prec_cust1][post_cust1]
            # I try to insert the customer in the best position: look for the nearest customer on route2, I'll put the new customer after it
            distances  = np.array([dist_matrix[cust_id][i] for i in route_2.route])
            best_idx = np.argpartition(distances, 1) 
            prec_cust2 = route_2.route[best_idx[0]]
            post_cust2 = route_2.route[best_idx[0]+1]
            new_load_min2 = route_2.load_min + cust.service_time - dist_matrix[prec_cust2][post_cust2] \
            + dist_matrix[prec_cust2][cust_id] + dist_matrix[cust_id][post_cust2]
            cap_min_constraint2 = new_load_min2 <= route_2.cap_min
            feasible = cap_min_constraint2
            if feasible:
                 # update routes
                route_1.load_kg = new_load_kg1
                route_1.load_min = new_load_min1
                route_1.load_cust -= 1
                route_2.load_kg = new_load_kg2
                route_2.load_min = new_load_min2
                route_2.load_cust += 1
                route_1.route.remove(cust_id)
                route_2.route = route_2.route[:best_idx[0]+1]+[cust_id]+route_2.route[best_idx[0]+1:]
                if set(route_1.route) in self.tabu_list or set(route_2.route) in self.tabu_list:
                    self.violate_tabu = True

        return feasible, route_1, route_2, route_ids


    def _local_search(self, route, final=False):
        # local search
        best_route, best_cost, service_times_routes = self._find_best_permutation(route, final)
        route.route = best_route
        route.load_min = best_cost + service_times_routes
        return route


    def _find_best_permutation(self, route, final):
        service_times_routes = 0
        route_list = route.route[1:-1]
        for c in route_list:
            service_times_routes += self.current_solution.customers[c].service_time
        best_cost = route.load_min - service_times_routes
        best_route = route.route
        dist_matrix = self.current_solution.distance_matrix
        
        if route.load_cust >= 3:
            all_permutation = self.perms[route.load_cust]
            if not final:
                total_permutation = len(all_permutation)
                if total_permutation >= constant.NUM_PERM:
                    all_permutation = random.sample(all_permutation, constant.NUM_PERM)
            for perm in all_permutation:
                new_route = [0]+[route_list[x] for x in perm]+[0]
                route_cost = 0
                for i in range(route.load_cust+1):
                    route_cost += dist_matrix[new_route[i]][new_route[i+1]]
                    if route_cost>=best_cost:
                        break
                if route_cost < best_cost:             
                    best_route = new_route
                    best_cost = route_cost
        return best_route, best_cost, service_times_routes
        
