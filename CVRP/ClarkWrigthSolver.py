from Customer import Customer
from Route import Route
import numpy as np

class ClarkeWrightSolver(BaseSolver):
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
        self.total_cost = 0

        cap_kg=15
        cap_min=3000
        cap_cust=6

        # list of customers
        self.customers = []
        self.routes = []
        self.route_of_customers = {}
        
        for k in range(self.num_customers):
            cust = Customer(k+1, demand[k], service_time[k])
            self.customers.append(cust)
            route = Route(cap_kg, cap_min, cap_cust)
            route.initialize_route(cust, distance_matrix[0][k+1])
            route_of_customers[k+1] = route.id
            self.routes.append(route)

        '''
        selected_customer.apply(lambda line: _initialize_customers(line.kg, line.service_time, line.customer_label, customers))
        '''

    def _compute_savings_matrix(self):
        """Compute Clarke and Wright savings list
        A saving list is a matrix containing the saving amount S between i and j
        S is calculated by S = d(0,i) + d(0,j) - d(i,j) (CLARKE; WRIGHT, 1964)
        """
        saving_matrix = np.zeros((self.num_customers,self.num_customers))
        for i in range(self.num_customers):
            for j in range( self.num_customers):
                if j != i:   
                    # saving index of including cell i and cell j in the same route         
                    saving_matrix[i][j] = self.distance_matrix[0][i+1]+self.distance_matrix[0][j+1]-self.distance_matrix[i+1][j+1]
        return saving_matrix


    def solver(self):
        """Solves the CVRP problem using Clarke and Wright Savings methods

        Parameters:
            data: CVRPData instance
            vehicles: Vehicles number
            timeout: max processing time in seconds

        Returns a solution (ClarkeWrightSolution class))
        """
        savings_matrix = _compute_savings_matrix()

        return 