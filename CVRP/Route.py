class Route:
    num_route = 0
    def __init__(self, cap_kg=16, cap_min=3000, cap_cust=5):
        '''
        Constructor
        '''
        self.id = Route.num_route
        Route.num_route += 1
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
    def delete_route():
        Route.num_route -= 1


