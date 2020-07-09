from CVRP.Customer import Customer
from CVRP.Vehicle import Vehicle
from scipy.spatial import distance
import numpy as np
import sys

class GreedySolver:
    def __init__(self, selected_customer, depot):
        #self.num_customers = len(selected_customer)
        self.num_customers = 16
        self.num_vehicles = 4
        # select from select_clients_df the columns corresponding to (x,y) coordinates and store them into a numpy array 
        clients_coords = selected_customer[['x', 'y']].to_numpy()
        # add at the beginning of the coordinates array the coordinates of depot
        coords = np.vstack ((depot, clients_coords)) 
        self.distances = distance.cdist(coords, coords)
        self.total_cost = 0

        cap_kg=15
        cap_min=3000
        cap_cust=6

        # list of customers
        self.customers = []
        selected_customer.apply(lambda line: _initialize_customers(line.kg, line.service_time, line.customer_label, customers))

        # list of vehicles
        self.vehicles = [Vehicle(cap_kg, cap_min, cap_cust) for v in range(self.num_vehicles)]


    def check_all_customers_on_routes(self):
        '''
        Check if all customers are on the the routes
        '''
        for customer in self.customers:
            if customer.is_routed == False:
                return False
        return True

    def solver(self):
        vehicles = self.vehicles
        customers = self.customers
        vehicle_idx = 0

        while(check_all_customers_on_routes()):
            customer_idx = 0
            min_cost = sys.maxsize

            # if the list is empty
            if not vehicles[vehicle_idx].route:
                vehicles[vehicle_idx].add_customer(customers[customer_idx], self.distances[0][1])
                customers[customer_idx].is_routed = True
                
    ############################################################################################################################


    @staticmethod
    def _initialize_customers(demand, service_time, id, customers):
        custumer = Customer(id, demand, service_time)
        customers.append(custumer)