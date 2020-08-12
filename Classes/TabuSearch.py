from itertools import permutations
import random
import copy
import numpy as np
from Classes.Route import Route
from Classes.ClarkWrightSolver import ClarkWrightSolver
import constant


class TabuSearch():

    def __init__(self, initial_solution, max_time, perc_swap, tabu_lenght, num_permutation):    
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
        self.tabu_list = {}
        self.tabu_lenght = tabu_lenght
        self.violate_tabu = True
        self.best_cost = initial_solution.total_cost
        self.best_routes = copy.copy(initial_solution.routes)
        self.best_route_of_customer = copy.copy(initial_solution.route_of_customers)
        self.route_to_eliminate = None
        self.eliminated_route = False
        self.no_improvement = 0
        self.max_time = max_time
        self.previous_time = 0
        self.perc_swap = perc_swap
        self.num_permutation = num_permutation

    def solve(self, elapsed_time):
        # copy of the routes
        all_routes = copy.copy(self.current_solution.routes)
        diff_time = elapsed_time - self.previous_time
        feasible_swap = False
        # generate neighbourhood by swapping customers

        if elapsed_time/self.max_time <= self.perc_swap:            
            num_swap = random.randint(1,2)
            swap_size = random.randint(1,3)
        else:
            num_swap = 1
            swap_size = 1
        while not feasible_swap:
            feasible_swap, old_cost_routes, swapped_routes, route_ids_no_more, cust_ids = self._swap_neighbourhood(all_routes, num_swap, swap_size)

        # those routes have been modified by swap
        all_routes = self._update_routes(all_routes, route_ids_no_more, swapped_routes)

        modified_routes_id = []
        for route_swap in swapped_routes:            
            if route_swap.load_cust <= 2:
                self.route_to_eliminate = route_swap.id
            modified_routes_id.append(route_swap.id)

        all_modified_routes = set(modified_routes_id)

        # generate neighbourhood by inserting a customer in another route
        feasible_insertion, route1_ins, route2_ins, cust_id_ins, route_ids_no_more_ins = self._insert_neighbourhood(all_routes)
            
        if feasible_insertion:
            # those routes have been modified by insertion
            all_routes = self._update_routes(all_routes, route_ids_no_more_ins, [route1_ins,route2_ins])
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
            self.eliminated_route = False
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost, feasible_insertion, route1_ins, route2_ins, cust_id_ins)
            if diff_cost_best >= 0:
                self.best_cost = current_cost
                self.best_routes = copy.copy(self.current_solution.routes)
                self.best_route_of_customer = copy.copy(self.current_solution.route_of_customers)
        elif diff_cost_best > 0:
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost_best, feasible_insertion, route1_ins, route2_ins, cust_id_ins, best=True)
        elif not(self.violate_tabu) and self.no_improvement >= 0.01*self.max_time and elapsed_time<=0.95*self.max_time:
            self._accept_solution(all_routes, swapped_routes, cust_ids, diff_cost, feasible_insertion, route1_ins, route2_ins, cust_id_ins)
        else:
            self.no_improvement += diff_time
        
        self.previous_time = elapsed_time
        self.violate_tabu = True
        self.route_to_eliminate = None
                

    def final_optimization(self):
        self.current_solution.route_of_customers = self.best_route_of_customer
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
    def _update_routes(all_routes, route_ids_no_more, routes_list):
        for i in range(len(routes_list)):
            del all_routes[route_ids_no_more[i]]
            all_routes[routes_list[i].id] = routes_list[i]
        return all_routes


    def _update_tabu_list(self, route, customers):
        for customer in customers:
            if len(self.tabu_list) < self.tabu_lenght:
                self.tabu_list[customer]=set(route.route)
            else:
                element_to_remove = list(self.tabu_list.keys())[0] 
                del self.tabu_list[element_to_remove]


    def _accept_solution(self, all_routes, swapped_routes, swapped_cust, diff_cost, feasible_insertion, route1_ins, route2_ins, cust_id_ins, best=False):
        
        for swap in range(len(swapped_routes)):
            self._update_tabu_list(swapped_routes[swap], swapped_cust[swap])

        self.no_improvement = 0
        if best:
            self.best_routes = copy.copy(all_routes)
            self.best_cost -= diff_cost
            for swap in range(len(swapped_routes)):                
                for cust in swapped_cust[swap]:
                    if swap%2==0:
                        self.best_route_of_customer[cust] = swapped_routes[swap+1].id
                    else:
                        self.best_route_of_customer[cust] = swapped_routes[swap-1].id
        else:
            self.current_solution.routes = copy.copy(all_routes)
            self.current_solution.total_cost -= diff_cost
            for swap in range(len(swapped_routes)):
                for cust in swapped_cust[swap]:
                    if swap%2==0:
                        self.current_solution.route_of_customers[cust] = swapped_routes[swap+1].id
                    else:
                        self.current_solution.route_of_customers[cust] = swapped_routes[swap-1].id

        if feasible_insertion:
            if best:
                self.best_route_of_customer[cust_id_ins] = route2_ins.id
            else:
                self.current_solution.route_of_customers[cust_id_ins] = route2_ins.id                
            self._update_tabu_list(route1_ins, [cust_id_ins])


    def _swap_neighbourhood(self, all_routes, num_swap, swap_size):
        all_route_ids = all_routes.keys()
        # select 2 random routes and 2 random customer
        route_ids = random.sample(all_route_ids, k=2*num_swap)

        swapped_routes = []
        cust_ids = []
        prec_cust_idx = []
        post_cust_idx = []

        for swap in range(2*num_swap):
            route = self._initialize_route(all_routes, route_ids[swap], custumer_on_route = False)
            swapped_routes.append(route)
            if route.load_cust >= swap_size:
                left = random.randint(1,  route.load_cust+1-(swap_size))
                right = left+swap_size
                cust_id = route.route[left:right]
                prec_cust = left-1
                post_cust = right
            else:
                cust_id = random.sample(route.route[1:-1], 1)
                prec_cust = route.route.index(cust_id[0])-1
                post_cust = route.route.index(cust_id[0])+1

            cust_ids.append(cust_id)
            prec_cust_idx.append(prec_cust)
            post_cust_idx.append(post_cust)

        feasible = True
        old_cost_routes = 0
        swap = 0
        while swap<2*num_swap and feasible:
            old_cost_routes += swapped_routes[swap].load_min
            if swap % 2 == 0:
                feasible_swap, swapped_routes[swap] = self._try_swap(swapped_routes[swap+1], swapped_routes[swap], cust_ids[swap+1], \
                    cust_ids[swap], prec_cust_idx[swap], post_cust_idx[swap])                
            else:
                feasible_swap, swapped_routes[swap] = self._try_swap(swapped_routes[swap-1], swapped_routes[swap], cust_ids[swap-1], \
                    cust_ids[swap], prec_cust_idx[swap], post_cust_idx[swap])
            swap += 1
            feasible = feasible and feasible_swap
        return feasible, old_cost_routes, swapped_routes, route_ids, cust_ids
    
    
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

        if cust_id in self.tabu_list:
            self.violate_tabu = self.violate_tabu and (self.tabu_list[cust_id] == set(route_2.route))

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
        return feasible, route_1, route_2, cust_id, route_ids


    def _local_search(self, route, final=False):
        # local search
        new_cost_routes = route.load_min
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
                if total_permutation >= self.num_permutation:
                    all_permutation = random.sample(all_permutation, self.num_permutation)
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


    def _try_swap(self, swapped_route1, swapped_route2, cust_ids1, cust_ids2, left, right):
        
        dist_matrix = self.current_solution.distance_matrix   

        new_load_kg = swapped_route2.load_kg
        new_load_cust = swapped_route2.load_cust + len(cust_ids1) - len(cust_ids2)      
        new_load_min = swapped_route2.load_min
        
        new_load_kg, new_load_min = self._calculate_new_loads(cust_ids1, swapped_route2.route, left, right, new_load_kg, new_load_min)
        new_load_kg, new_load_min = self._calculate_new_loads(cust_ids2, swapped_route2.route, left, right, new_load_kg, new_load_min, factor='minus')
        
        # check if the swap is feasible
        cap_kg_constraint = new_load_kg <= swapped_route2.cap_kg
        cap_min_constraint = new_load_min <= swapped_route2.cap_min
        cap_cust_constraint = new_load_cust <= swapped_route2.load_cust
        feasible_swap = cap_kg_constraint and cap_min_constraint and cap_cust_constraint
        if feasible_swap:
            swapped_route2.load_kg = new_load_kg
            swapped_route2.load_min = new_load_min
            swapped_route2.load_cust = new_load_cust
            swapped_route2.route = swapped_route2.route[0:left+1] + cust_ids1 + swapped_route2.route[right:]
        
        return feasible_swap, swapped_route2


    def _calculate_new_loads(self, cust_ids, route, left, right, new_load_kg, new_route_cost, factor='plus'):
        prec = route[left]
        for cust_id in cust_ids:                 
            customer = self.current_solution.customers[cust_id]
            if cust_id in self.tabu_list:
                self.violate_tabu = self.violate_tabu and (self.tabu_list[cust_id] == set(route))
            if factor == 'plus':
                new_load_kg += customer.demand
                new_route_cost += customer.service_time
                new_route_cost += self.current_solution.distance_matrix[prec][cust_id]
            elif factor == 'minus':
                new_load_kg -= customer.demand
                new_route_cost -= customer.service_time
                new_route_cost -= self.current_solution.distance_matrix[prec][cust_id]
            prec = cust_id
        if factor == 'plus':
            new_route_cost += self.current_solution.distance_matrix[prec][route[right]]
        elif factor == 'minus':
            new_route_cost -= self.current_solution.distance_matrix[prec][route[right]]

        return new_load_kg, new_route_cost