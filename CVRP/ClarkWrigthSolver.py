from Customer import Customer
from Route import Route
from merge_route import merge_routes
import numpy as np


class ClarkeWrightSolver():
    """Clark and Wright Savings algorithm solver class"""
    def __init__(self, distance_matrix, service_time, demand, selected_customer=None, depot=None):
        #self.num_customers = len(selected_customer)
        self.num_customers = 16
        self.num_vehicles = 4
        '''
        # select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
        clients_coords = selected_customer[['x', 'y']].to_numpy()
        # add at the beginning of the coordinates array the coordinates of depot
        coords = np.vstack ((depot, clients_coords)) 
        self.distances = distance.cdist(coords, coords)
        '''
        self.distance_matrix = distance_matrix

        # list of customers
        self.customers = {}
        self.routes = {}
        self.route_of_customers = {}
        
        for k in range(self.num_customers):
            cust = Customer(k+1, demand[k], service_time[k])
            self.customers[k+1] = cust
            route = Route()
            route.initialize_route(cust, distance_matrix[0][k+1])
            self.route_of_customers[k+1] = route.id
            self.routes[route.id] = route

        '''
        selected_customer.apply(lambda line: _initialize_customers(line.kg, line.service_time, line.customer_label, customers))
        '''

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
        best_savings_indexes = np.unravel_index(np.argsort(savings_matrix.ravel())[-4*self.num_customers:], savings_matrix.shape)
    
        for i in range(4*self.num_customers):
            customer1=best_savings_indexes[0][4*self.num_customers-1-i]
            customer2=best_savings_indexes[1][4*self.num_customers-1-i]
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
                    del self.routes[route1_idx]
                    del self.routes[route2_idx]
                else:
                    Route.delete_route()


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
        print('Total distance of all routes: {} km'.format(total_cost-sum([0, 50, 60, 120, 156, 85, 83, 123, 167, 90, 78, 98, 142, 111, 89, 40, 54])))
        print('Total load of all routes: {} kg'.format(total_load)) 
            