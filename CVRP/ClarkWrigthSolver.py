from Customer import Customer
from Route import Route
from merge_route import merge_routes
import numpy as np
import random


class ClarkWrightSolver():
    """Clark and Wright Savings algorithm solver class"""
    def __init__(self, distance_matrix, service_time, demand):
        #self.num_customers = len(selected_customer)
        self.num_customers = len(service_time)
        self.num_vehicles = 50
        self.num_routes = self.num_customers
        random.seed(501)
        self.distance_matrix = distance_matrix

        # list of customers
        self.customers = {}
        self.routes = {}
        self.route_of_customers = {}

        for k in range(self.num_customers):
            cust = Customer(k+1, demand[k][0], service_time[k][0])
            self.customers[k+1] = cust
            route = Route()
            route.initialize_route(cust, distance_matrix[0][k+1])
            self.route_of_customers[k+1] = route.id
            self.routes[route.id] = route

        self.total_cost = 0
        self.service_time = service_time

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
        best_savings_indexes = np.unravel_index(np.argsort(savings_matrix.ravel())[num_elem_tridiag:], savings_matrix.shape)
        final_random_custumer = int(2*num_elem_tridiag//3)
        permutation = list(range(final_random_custumer,num_elem_tridiag))
        random.shuffle(permutation)
        permutation = list(range(final_random_custumer))+permutation
        for i in permutation:
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
                    for cust_id in new_route.route:
                        self.route_of_customers[cust_id]=new_route.id
                    self.routes[new_route.id]=new_route
                    self.num_routes -= 1
                    del self.routes[route1_idx]
                    del self.routes[route2_idx]
                else:
                    Route.delete_route()
        if self.num_routes <= self.num_vehicles:
            print('feasible solution found: used {} vehicles'.format(self.num_routes))
            for k, v in self.routes.items():
                self.total_cost += v.load_min
        else:
            print('feasible solution not found: used {} vehicles'.format(self.num_routes))


    def print_solution(self):
        total_cost = 0
        total_load = 0
        num_route = 0
        for k, v in self.routes.items():
            print('Route for vehicle {}:'.format(num_route))
            num_route += 1
            route = ' {} Load ({}) -> '.format(0, 0)
            cum_load = 0
            for cust_id in v.route:
                if cust_id !=0:
                    cum_load += self.customers[cust_id].demand
                    route += ' {} Load ({}) -> '.format(cust_id, cum_load)
            route += ' {} Load ({})'.format(0, cum_load)
            total_load += cum_load
            total_cost += v.load_min
            print(route)
            print('Total time of the route: {} min'.format(v.load_min))
            print('Total load of the route: {} kg\n'.format(v.load_kg))
        print('Total distance of all routes: {} km'.format(total_cost-sum(self.service_time)[0]))
        print('Total load of all routes: {} kg'.format(total_load)) 
        