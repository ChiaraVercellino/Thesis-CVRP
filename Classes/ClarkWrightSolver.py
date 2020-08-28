from Classes.Customer import Customer
from Classes.Route import Route
from Functions.MergeRoutes import merge_routes
import numpy as np
from scipy.spatial import distance
import random

import constant


class ClarkWrightSolver():
    """Clark and Wright Savings algorithm solver class"""
    def __init__(self, selected_customer, depot):

        random.seed(constant.SEED)
        #self.num_customers = len(selected_customer)
        self.num_customers = len(selected_customer)
        self.num_vehicles = constant.NUM_VEHICLES
        self.num_routes = self.num_customers
        # select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
        clients_coords = selected_customer[['x', 'y']].to_numpy()
        # add at the beginning of the coordinates array the coordinates of depot
        coords = np.vstack ((depot, clients_coords)) 
        self.distance_matrix = np.round(distance.cdist(coords, coords),3)
        self.demand = selected_customer['kg'].to_numpy()
        self.service_time = selected_customer['service_time'].to_numpy()
        # list of customers
        self.customers = {}
        self.routes = {}
        self.route_of_customers = {}
        self.small_routes = []
        
        for k in range(self.num_customers):
            cust = Customer(k+1, self.demand[k], self.service_time[k])
            self.customers[k+1] = cust
            route = Route()
            route.initialize_route(cust, self.distance_matrix[0][k+1])
            self.route_of_customers[k+1] = route.id
            self.routes[route.id] = route

        self.total_cost = 0

    def _compute_savings_matrix(self):
        """Compute Clarke and Wright savings matrix
        It is a matrix containing the saving amount S between i and j
        S is calculated by S = c(0,i) + c(0,j) - c(i,j) (CLARKE; WRIGHT, 1964)
        """
        saving_matrix = np.zeros((self.num_customers,self.num_customers))
        for i in range(self.num_customers):
            for j in range( self.num_customers):
                if j != i:   
                    # saving index of including cell i and cell j in the same route         
                    saving_matrix[i][j] = self.distance_matrix[0][i+1]+self.distance_matrix[0][j+1]-self.distance_matrix[i+1][j+1]
        return saving_matrix


    def solve(self):
        """Solves the CVRP problem using Clarke and Wright Savings methods
        """
        savings_matrix = self._compute_savings_matrix()
        savings_matrix[np.tril_indices_from(savings_matrix, -1)] = 0
        num_elem_tridiag = int((self.num_customers-1)*self.num_customers/2)
        best_savings_indexes = np.unravel_index(np.argsort(savings_matrix.ravel())[-num_elem_tridiag:], savings_matrix.shape)
    
        for i in range(num_elem_tridiag):
            customer1=best_savings_indexes[0][num_elem_tridiag-1-i]
            customer2=best_savings_indexes[1][num_elem_tridiag-1-i]
            route1_idx=self.route_of_customers[customer1+1]
            route2_idx=self.route_of_customers[customer2+1]
            
            route1 = self.routes[route1_idx]
            route2 = self.routes[route2_idx]
            if route1_idx != route2_idx:
                savings = savings_matrix[customer1][customer2]
                feasible_route, new_route = merge_routes(route1, route2, customer1, customer2, savings)
                if feasible_route:
                    for cust_id in new_route.route[1:-1]:
                        self.route_of_customers[cust_id]=new_route.id
                    self.routes[new_route.id]=new_route
                    self.num_routes -= 1
                    del self.routes[route1_idx]
                    del self.routes[route2_idx]
                else:
                    Route.delete_route()
        
        '''
        small_routes = []
        big_routes = []
        for k, v in self.routes.items():
            if v.load_cust <= 2:
                small_routes.append(k)
            else:
                big_routes.append(k)
        
        max_try = self.num_customers-1
        for small_route_id in small_routes:
            small_route = self.routes[small_route_id]
            for cust_id in small_route.route[1:-1]:
                cust = self.customers[cust_id]
                distances  = np.array(self.distance_matrix[cust_id][1:])
                best_indexes = np.argpartition(distances, max_try) 
                i = 1
                found_route = False
                while i < max_try and not(found_route):
                    best_near_cust = best_indexes[i]+1
                    best_route = self.routes[self.route_of_customers[best_near_cust]]
                    if best_route.load_cust+1<=best_route.cap_cust and best_route.load_kg+cust.demand<=best_route.cap_kg:
                        idx_best_near = best_route.route.index(best_near_cust)
                        prec_cust = best_route.route[idx_best_near-1]
                        post_cust = best_route.route[idx_best_near+1]
                        if self.distance_matrix[cust_id][post_cust] < self.distance_matrix[prec_cust][cust_id]:
                            delta_load_min = self.distance_matrix[best_near_cust][post_cust] - self.distance_matrix[best_near_cust][cust_id] - self.distance_matrix[cust_id][post_cust]
                            new_load_min = best_route.load_min - delta_load_min + cust.service_time
                            new_route = best_route.route[:idx_best_near+1]+[cust_id]+best_route.route[idx_best_near+1:]
                        else:
                            delta_load_min = self.distance_matrix[prec_cust][best_near_cust] - self.distance_matrix[prec_cust][cust_id] - self.distance_matrix[cust_id][best_near_cust]
                            new_load_min = best_route.load_min - delta_load_min + cust.service_time
                            new_route = best_route.route[:idx_best_near]+[cust_id]+best_route.route[idx_best_near:]
                        if new_load_min <= best_route.cap_min:
                            best_route.load_min = new_load_min
                            best_route.load_cust += 1
                            best_route.load_kg += cust.demand
                            best_route.route = new_route
                            self.route_of_customers[cust_id] = best_route.id
                            found_route = True
                            small_route.load_cust -= 1
                            if small_route.load_cust == 0:
                                del self.routes[small_route_id]
                                self.num_routes -= 1
                            else:
                                small_route.load_kg -= cust.demand
                                idx_cust = small_route.route.index(cust_id)
                                prec_cust_small = small_route.route[idx_cust-1]
                                post_cust_small = small_route.route[idx_cust+1]
                                delta_small_route = self.distance_matrix[prec_cust_small][cust_id] + self.distance_matrix[cust_id][post_cust_small] - \
                                    self.distance_matrix[prec_cust_small][post_cust_small] + cust.service_time
                                small_route.load_min -= delta_small_route
                                small_route.route.remove(cust_id)
                            
                    i += 1
        
        '''
        if self.num_routes <= self.num_vehicles:
            print('Route before: {}'.format(self.num_routes))
            for k, v in self.routes.items():
                self.total_cost += v.load_min
                feasible_solution = True
                if v.load_cust <= 2:
                    self.small_routes.append(k)
        else:
            feasible_solution = False
        return feasible_solution

    


    def print_solution(self, day, file_path='./Solution/routes.sol'):
        total_load = 0
        num_route = 0
        max_route_distance = 0
        num_empty_vehicles = constant.NUM_VEHICLES-len(self.routes)
        # Save the current day
        with open(file_path, 'a') as fp:            
            fp.write(f'\n DAY: {day.current_day} \n')
        for k, v in self.routes.items():
            route = 'Route for vehicle {}:\n'.format(num_route)
            num_route += 1
            route += ' {} -> '.format(0)
            for cust_id in v.route:
                if cust_id !=0:
                    route += ' {} -> '.format(cust_id)
            route += ' {}\n'.format(0)
            total_load += v.load_kg
            route += 'Travel and service time of the route: {} h\n'.format(round(v.load_min/60,2))
            route += 'Load of the route: {} kg \n'.format(round(v.load_kg,2))
            max_route_distance = max(max_route_distance, v.load_min)
            with open(file_path, 'a') as fp:          
                fp.write(route)
        with open(file_path, 'a') as fp:    
            total_distance = self.total_cost     
            fp.write('Total travel and service time of all routes: {} h\n'.format(round(total_distance/60,2)))
            fp.write('Total load of all routes: {} kg\n'.format(round(total_load, 2)))
            fp.write('Maximum of the route travel time: {} h\n'.format(round(max_route_distance/60,2)))
        return num_empty_vehicles