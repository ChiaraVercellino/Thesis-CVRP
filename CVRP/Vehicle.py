class Vehicle:
    def __init__(self, cap_kg, cap_min, cap_cust):
        '''
        Constructor
        '''
        # kg capacity of vehicle
        self.cap_kg = cap_kg;
        # minutes capacity of vehicle
        self.cap_min = cap_min
        # customers' capacity of vehicle
        self.cap_cust = cap_cust
        # load of vehicle (kg)
        self.load_kg = 0;
        # minutes' load of vehicle
        self.load_min = 0
        # customers' load of vehicle
        self.load_cust = 0
        # the vehicle starts from the depot
        self.current_location = 0;
        # customers on the route of vehicle
        self.route = []


    def add_customer(self, customer, route_length):
        '''
        Add a customer to the route of vehicle
        '''
        self.route.append(customer)
        self.load_kg += customer.demand
        self.load_min = self.load_min + customer.service_time + route_length
        self.load_cust += 1
        self.current_location = customer.id

    def add_depot(self, route_length):
        '''
        Add a customer to the route of vehicle
        '''
        self.load_min += route_length
        self.current_location = 0


    def check_constraints(self, customer, travel_time):
        '''
        Check if capacity constraints are satisfied
        '''
        cust = self.load_cust + 1 <= self.cap_cust
        time = self.load_min + customer.service_time + travel_time <= self.cap_min
        kg = self.load_kg +customer.demand <= self.cap_kg
        constraint = cust and time and kg
        return constraint