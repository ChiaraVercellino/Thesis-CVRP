from itertools import permutations
import random
import copy
import numpy as np
from Classes.Route import Route
from Classes.ClarkWrightSolver import ClarkWrightSolver
import constant


class TabuSearch():

    def __init__(self, initial_solution, max_time, tabu_len, perc_worse):    
        random.seed(constant.SEED)
        # generate all possible permutation for local search step
        self.perms = {}
        for i in range(3, constant.CUSTOMER_CAPACITY+1):
            perms = list(permutations(range(1, i+1))) 
            perms.pop(0)
            for p in perms:
                # remove anti-clockwise permutations
                if p[::-1] in perms:
                    perms.remove(p[::-1])
            self.perms[i]=perms            
        self.current_solution = initial_solution
        self.tabu_list = []
        self.tabu_lenght = tabu_len
        self.violate_tabu = False
        self.best_cost = initial_solution.total_cost
        self.best_routes = copy.copy(initial_solution.routes)
        self.route_to_eliminate = None
        self.eliminated_route = False
        self.no_improvement = 0
        self.max_time = max_time
        self.previous_time = 0
        self.accept_worse = False
        self.perc_worse = perc_worse
        self.num_worse = 0
        self.num_tabu = 0
        self.num_best = 0


    def solve(self, elapsed_time):
            
        diff_time = elapsed_time - self.previous_time        
        routing_done = False
        route_of_customers = []
        
        '''
        if self.accept_worse:
            num_unrouted = constant.NUM_UNROUTED
            max_attempt = num_unrouted//2
            num_attempt = 0
            while num_attempt < max_attempt and not(routing_done):
                all_routes_rerouting = copy.copy(self.current_solution.routes)
                route_of_customers = copy.copy(self.current_solution.route_of_customers)
                all_routes_rerouting, unrouted_customers, route_of_customers, diff_cost = self._unrouting(all_routes_rerouting, num_unrouted, route_of_customers)
                routing_done, all_routes_rerouting, route_of_customers, diff_cost = self._re_routing(all_routes_rerouting, unrouted_customers, route_of_customers, diff_cost)
                num_attempt += 1
                num_unrouted -= 1
        
        
        if routing_done:

            all_routes = copy.copy(all_routes_rerouting)
            if len(self.current_solution.routes) > len(all_routes):
                self.eliminated_route = True
        else:
            all_routes = copy.copy(self.current_solution.routes)
            diff_cost = 0
        '''

        all_routes = copy.copy(self.current_solution.routes)
        diff_cost = 0
        feasible_swap = False
        # generate neighbourhood by swapping customers
        while not feasible_swap:       
            feasible_swap, old_cost_routes, swapped_routes, route_ids_no_more, cust_ids = self._swap_neighbourhood(all_routes)
        
        
        # those routes have been modified by swap
        tabu_moves = []
        all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more, swapped_routes, tabu_moves)

        modified_routes_id = []
        for route_swap in swapped_routes:            
            modified_routes_id.append(route_swap.id)
            if route_swap.load_cust <= 2:
                self.route_to_eliminate = route_swap.id

        all_modified_routes = set(modified_routes_id)

        feasible_insertion, route1_ins, route2_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)        
        
        if feasible_insertion:
            # those routes have been modified by insertion
            all_routes, tabu_moves = self._update_routes(all_routes, route_ids_no_more_ins, [route1_ins, route2_ins],tabu_moves=tabu_moves)
            if route1_ins.load_cust==0:
                del all_routes[route1_ins.id]
                self.eliminated_route = True
                all_modified_routes = all_modified_routes.union(set([route2_ins.id])).difference(set(route_ids_no_more_ins))  
                self.route_to_eliminate = None
            else:
                all_modified_routes = all_modified_routes.union(set([route2_ins.id, route1_ins.id])).difference(set(route_ids_no_more_ins))
            if route1_ins.load_cust <= 2:
                self.route_to_eliminate = route1_ins.id
        
        # calculate cost of new solution
        new_cost_routes = 0        
        for id_route in all_modified_routes:
            best_route = self._local_search(all_routes[id_route])
            all_routes[id_route] = best_route
            new_cost_routes += best_route.load_min
        diff_cost = diff_cost + old_cost_routes - new_cost_routes
        current_cost = self.current_solution.total_cost - diff_cost
        diff_cost_best = self.best_cost - current_cost

        if self.violate_tabu:
            self.num_tabu += 1
        # found a better solution: update solution
        if diff_cost >= 0 and not(self.violate_tabu) or self.eliminated_route:            
            self.eliminated_route = False
            self.accept_worse = False
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost, feasible_insertion, route1_ins, route2_ins, \
                routing_done, route_of_customers, tabu_moves)
            if diff_cost_best > 0:
                self.num_best += 1
                self.best_cost = current_cost
                self.best_routes = copy.copy(self.current_solution.routes)   
            
        elif diff_cost_best > 0:
            self.num_best += 1
            self.accept_worse = False
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost_best, feasible_insertion, route1_ins, route2_ins, \
                routing_done, route_of_customers, tabu_moves, best=True) 
                         
        elif not(self.violate_tabu) and self.no_improvement >= self.perc_worse*self.max_time:
            self.accept_worse = True
            self.num_worse += 1
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost, feasible_insertion, route1_ins, route2_ins, \
                routing_done, route_of_customers, tabu_moves)
        
        else:
            self.no_improvement += diff_time
        
        self.previous_time = elapsed_time
        self.violate_tabu = False
        
        
        
                

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


    @staticmethod
    def _update_routes(all_routes, route_ids_no_more, routes_list, tabu_moves):
        for i in range(len(routes_list)):
            tabu_moves.append(all_routes[route_ids_no_more[i]].route)
            del all_routes[route_ids_no_more[i]]
            all_routes[routes_list[i].id] = routes_list[i]
        return all_routes, tabu_moves


    def _update_tabu_list(self, route):
        if route not in self.tabu_list:
            if len(self.tabu_list) < self.tabu_lenght:            
                self.tabu_list.append(route)
            else:
                self.tabu_list.pop(0)
                self.tabu_list.append(route)


    def _accept_solution(self, all_routes, swapped_routes, swapped_cust, diff_cost, feasible_insertion, route1_ins, route2_ins, \
        routing_done, route_of_customers, tabu_moves, best=False):

        self.no_improvement = 0
        if best:
            self.best_routes = copy.copy(all_routes)
            self.best_cost -= diff_cost
        else:
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
            if routing_done:
                self.current_solution.route_of_customers = copy.copy(route_of_customers)
            for cust in swapped_routes[0].route[1:-1]:
                self.current_solution.route_of_customers[cust] = swapped_routes[0].id
            for cust in swapped_routes[1].route[1:-1]:
                self.current_solution.route_of_customers[cust] = swapped_routes[1].id   
        
        for tabu_move in tabu_moves:
            self._update_tabu_list(set(tabu_move))
        

        if feasible_insertion:
            if not best:
                for cust in route1_ins.route[1:-1]:
                    self.current_solution.route_of_customers[cust] = route1_ins.id 
                for cust in route2_ins.route[1:-1]:
                    self.current_solution.route_of_customers[cust] = route2_ins.id       


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
            if set(route_1.route) in self.tabu_list and set(route_2.route) in self.tabu_list:
                self.violate_tabu = True

        return feasible, old_cost_routes, swapped_routes, route_ids, swapped_cust
    
    
    def _insert_neighbourhood(self, all_routes):
        all_route_ids = all_routes.keys()
        # select 2 random routes and 2 random customer
        route_ids = random.sample(all_route_ids, k=2)

        
        if self.route_to_eliminate and self.route_to_eliminate in all_route_ids:
            if self.route_to_eliminate == route_ids[1]:
                route_ids[1] = route_ids[0]
                route_ids[0] = self.route_to_eliminate
            else: 
                route_ids[0] = self.route_to_eliminate
        

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
        route_list = route.route
        for c in route_list[1:-1]:
            service_times_routes += self.current_solution.customers[c].service_time
        best_cost = route.load_min - service_times_routes
        best_route = route_list
        dist_matrix = self.current_solution.distance_matrix
        
        if route.load_cust >= 3:
            all_permutation = copy.copy(self.perms[route.load_cust])
            if not final:
                total_permutation = len(all_permutation)
                if total_permutation >= constant.NUM_PERM:
                    all_permutation = random.sample(all_permutation, constant.NUM_PERM)
            for perm in all_permutation:
                new_route = [0]+[route_list[i] for i in perm]+[0]
                route_cost = 0
                for i in range(len(new_route)-1):
                    route_cost += dist_matrix[new_route[i]][new_route[i+1]]
                    if route_cost>=best_cost:
                        break
                if route_cost < best_cost:             
                    best_route = new_route
                    best_cost = route_cost
        return best_route, best_cost, service_times_routes


    def _unrouting(self, all_routes, num_unrouted, route_of_customers):
        unrouted_customers = random.sample(list(self.current_solution.customers.values()), num_unrouted)
        dist_matrix = self.current_solution.distance_matrix
        delta_cost = 0
        for cust in unrouted_customers:
            route_id = route_of_customers[cust.id]
            new_route = self._initialize_route(all_routes, route_id, custumer_on_route=False)
            cust_idx = new_route.route.index(cust.id) 
            prec_cust = new_route.route[cust_idx-1]     
            post_cust = new_route.route[cust_idx+1]   
            new_route.load_cust -= 1
            new_route.load_kg -= cust.demand     
            delta_load_min = dist_matrix[prec_cust][cust.id] + dist_matrix[cust.id][post_cust] - dist_matrix[prec_cust][post_cust] 
            new_route.load_min = new_route.load_min - delta_load_min - cust.service_time 
            new_route.route.remove(cust.id)
            delta_cost += delta_load_min
            if new_route.load_cust >= 1:
                all_routes[new_route.id] = new_route                    
                for customer in new_route.route[1:-1]:
                    route_of_customers[customer] = new_route.id
            del route_of_customers[cust.id]
            del all_routes[route_id]

        return all_routes, unrouted_customers, route_of_customers, delta_cost

    def _re_routing(self, all_routes, unrouted_customers, route_of_cust, delta_cost):
        dist_matrix = self.current_solution.distance_matrix
        random.shuffle(unrouted_customers)
        max_try = constant.NUM_UNROUTED
        routed_cust = 0
        routing_done = False
        for cust in unrouted_customers:
            distances  = np.array(dist_matrix[cust.id][1:-1])
            best_indexes = np.argpartition(distances, max_try) 
            i = 0
            found_route = False
            while i < max_try and not(found_route):
                best_near_cust = best_indexes[i]+1
                if best_near_cust in route_of_cust.keys():
                    best_near_route = route_of_cust[best_near_cust]
                    best_route = self._initialize_route(all_routes, best_near_route, custumer_on_route=False)
                    if best_route.load_cust+1<=best_route.cap_cust and best_route.load_kg+cust.demand<=best_route.cap_kg:
                        idx_best_near = best_route.route.index(best_near_cust)
                        prec_cust = best_route.route[idx_best_near-1]
                        post_cust = best_route.route[idx_best_near+1]
                        if dist_matrix[cust.id][post_cust] < dist_matrix[prec_cust][cust.id]:
                            delta_load_min = dist_matrix[best_near_cust][post_cust] - dist_matrix[best_near_cust][cust.id] - dist_matrix[cust.id][post_cust]
                            new_load_min = best_route.load_min - delta_load_min + cust.service_time
                            new_route = best_route.route[:idx_best_near+1]+[cust.id]+best_route.route[idx_best_near+1:]
                        else:
                            delta_load_min = dist_matrix[prec_cust][best_near_cust] - dist_matrix[prec_cust][cust.id] - dist_matrix[cust.id][best_near_cust]
                            new_load_min = best_route.load_min - delta_load_min + cust.service_time
                            new_route = best_route.route[:idx_best_near]+[cust.id]+best_route.route[idx_best_near:]
                        if new_load_min <= best_route.cap_min:
                            best_route.load_min = new_load_min
                            best_route.load_cust += 1
                            best_route.load_kg += cust.demand
                            best_route.route = new_route
                            for customer in best_route.route[1:-1]:
                                route_of_cust[customer] = best_route.id
                            found_route = True
                            routed_cust += 1
                            delta_cost += delta_load_min
                            del all_routes[best_near_route]
                            all_routes[best_route.id] = best_route
                            
                i += 1
            if not found_route:
                break
        if routed_cust == len(unrouted_customers):
            routing_done = True
        return routing_done, all_routes, route_of_cust, delta_cost

