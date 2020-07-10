from Customer import Customer
from Vehicle import Vehicle
from scipy.spatial import distance
import numpy as np
import sys

class GreedySolver:
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
        self.distances = distance_matrix
        self.total_cost = 0

        cap_kg=15
        cap_min=3000
        cap_cust=6

        # list of customers
        self.customers = []
        
        for k in range(self.num_customers):
            self.customers.append(Customer(k+1, demand[k], service_time[k]))

        '''
        selected_customer.apply(lambda line: _initialize_customers(line.kg, line.service_time, line.customer_label, customers))
        '''

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

        while not self.check_all_customers_on_routes():
            customer_idx = 0
            min_cost = sys.maxsize

            candidate_customer = []
            for i in range (self.num_customers):
                if not(customers[i].is_routed):
                    cost = self.distances[vehicles[vehicle_idx].current_location][i+1]
                    if vehicles[vehicle_idx].check_constraints(customers[i], cost):
                        if cost < min_cost:
                            min_cost = cost
                            customer_idx = i
                            candidate_customer = customers[customer_idx]

            if candidate_customer:
                vehicles[vehicle_idx].add_customer(candidate_customer, min_cost)
                customers[customer_idx].is_routed = True
                self.total_cost += min_cost
            else:
                if vehicle_idx + 1 < self.num_vehicles:
                    if vehicles[vehicle_idx].current_location != 0:
                        cost = self.distances[vehicles[vehicle_idx].current_location][0]
                        vehicles[vehicle_idx].add_depot(cost)
                        self.total_cost += cost
                        vehicle_idx += 1
                else:
                    print('The remaining customers do not fit in vehicles')
                    return self

        cost = self.distances[vehicles[vehicle_idx].current_location][0]
        vehicles[vehicle_idx].add_depot(cost)
        self.total_cost += cost;
        self.vehicles = vehicles
        self.customers = customers
        return self

    def print_solution(self):
        vehicles = self.vehicles
        total_load = 0
        for i in range(self.num_vehicles):
            vehicle = vehicles[i]
            if vehicle.route:
                print('Route for vehicle {}:'.format(i))
                route = ' {} Load ({}) -> '.format(0, 0)
                cum_load = 0
                for j in range(len(vehicle.route)):
                    cum_load += vehicle.route[j].demand
                    customer_idx = vehicle.route[j].id
                    route += ' {} Load ({}) -> '.format(customer_idx, cum_load)
                route += ' {} Load ({})'.format(0, cum_load)
                total_load += cum_load
            print(route)
            print('Total time of the route: {} min'.format(vehicle.load_min))
            print('Total load of the route: {} kg\n'.format(vehicle.load_kg))
        print('Total distance of all routes: {} km'.format(self.total_cost))
        print('Total load of all routes: {} kg'.format(total_load))  

    @staticmethod
    def _initialize_customers(demand, service_time, id, customers):
        custumer = Customer(id, demand, service_time)
        customers.append(custumer)      


def main():
    distance_matrix = [
        [
            0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
            468, 776, 662
        ],
        [
            548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            320, 1084, 514
        ],
        [
            194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            274, 810, 468
        ],
        [
            536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    ]

    service_time = [50, 60, 120, 156, 85, 83, 123, 167, 90, 78, 98, 142, 111, 89, 40, 54]

    demand = [1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]

    greedy_solver = GreedySolver(distance_matrix, service_time, demand)

    greedy_solver.solver()

    greedy_solver.print_solution()


main()