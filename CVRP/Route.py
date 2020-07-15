class Route:
    num_route = 0
    def __init__(self, cap_kg, cap_min, cap_cust):
        '''
        Constructor
        '''
        self.id = num_route
        num_route += 1
        # kg capacity of vehicle
        self.cap_kg = cap_kg;
        # minutes capacity of vehicle
        self.cap_min = cap_min
        # customers' capacity of vehicle
        self.cap_cust = cap_cust
        # load of vehicle (kg)
        self.load_kg = 0
        # minutes' load of vehicle
        self.load_min = 0
        # customers' load of vehicle
        self.load_cust = 0
        # customers on the route of vehicle
        self.route = [0, 0]
        self.pos_customers_on_route = {}


    def initialize_route(self, customer, depot_distance):
        self.load_kg = customer.demand
        # minutes' load of vehicle
        self.load_min = customer.service_time + 2*depot_distance
        # customers' load of vehicle
        self.load_cust = 1
        # customers on the route of vehicle
        self.route.insert(1, customer.id)
        self.pos_customers_on_route[customer.id] = 1

    def check_constraints(self):
        '''
        Check if capacity constraints are satisfied
        '''
        cust = self.load_cust <= self.cap_cust
        time = self.load_min <= self.cap_min
        kg = self.load_kg <= self.cap_kg
        constraint = cust and time and kg
        return constraint

    @staticmethod
    def merge_routes(route1, route2, customer1, customer2, savings):
        new_route = Route(cap_kg, cap_min, cap_cust)

        new_route.load_kg = route1.load_kg+route2.load_kg
        # minutes' load of vehicle
        new_route.load_min = route1.load_min+route2.load_min - savings
        # customers' load of vehicle
        new_route.load_cust = route1.load_cust+route2.load_cust

        feasible_route = new_route.check_constraints()

        if feasible_route:

            new_route_list = []
            idx_cus1 = route1.pos_customers_on_route[customer1]
            idx_cus2 = route2.pos_customers_on_route[customer2]

            if route1.route[idx_cus1-1]==0:
                if route2.route[idx_cus2-1]==0:
                    new_route_list = route1.route[idx_cus1 :].reverse() + route2.route[idx_cus2 :]
                elif route2.route[idx_cus2+1]==0:
                    new_route_list = route2.route[: idx_cus2] + route1.route[idx_cus1 :]
            elif route1.route[idx_cus1+1]==0:
                if route2.route[idx_cus2-1]==0:
                    new_route_list = route1.route[: idx_cus1] + route2.route[idx_cus2 :]
                elif route2.route[idx_cus2+1]==0:
                    new_route_list = route2.route[: idx_cus2] + route1.route[: idx_cus1].reverse()

            new_route.route = new_route_list

            pos=0
            for cust in new_route_list:
                new_route.pos_customers_on_route[cust]=pos
                pos += 1

        return feasible_route, new_route

        
        