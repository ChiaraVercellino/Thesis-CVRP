from Classes.Customer import Customer
from Classes.Route import Route
from Functions.MergeRoutes import merge_routes
import numpy as np
from scipy.spatial import distance
import constant


class ClarkWrightSolver():
    """Clark and Wright Savings algorithm solver class"""
    def __init__(self, selected_customer, depot):
        #self.num_customers = len(selected_customer)
        self.num_customers = len(selected_customer)
        self.num_vehicles = constant.NUM_VEHICLES
        self.num_routes = self.num_customers
        
        # select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
        clients_coords = selected_customer[['x', 'y']].to_numpy()
        # add at the beginning of the coordinates array the coordinates of depot
        coords = np.vstack ((depot, clients_coords)) 
        self.distance_matrix = distance.cdist(coords, coords)
        self.demand = selected_customer['kg'].to_numpy()
        self.service_time = selected_customer['service_time'].to_numpy()

        # list of customers
        self.customers = {}
        self.routes = {}
        self.route_of_customers = {}
        
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
        best_savings_indexes = np.unravel_index(np.argsort(savings_matrix.ravel())[-2*self.num_vehicles*self.num_customers:], savings_matrix.shape)

        for i in range(2*self.num_vehicles*self.num_customers):
            customer1=best_savings_indexes[0][2*self.num_vehicles*self.num_customers-1-i]
            customer2=best_savings_indexes[1][2*self.num_vehicles*self.num_customers-1-i]
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
            #print('feasible solution found: used {} vehicles'.format(self.num_routes))
            for k, v in self.routes.items():
                self.total_cost += v.load_min
            feasible = True
        else:
            #print('feasible solution not found: used {} vehicles'.format(self.num_routes))
            feasible = False
        return feasible


    def print_solution(self, day, file_path='./Solution/routes.sol'):
        total_load = 0
        num_route = 0
        max_route_distance = 0
        num_empty_vehicles = len(self.routes)
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