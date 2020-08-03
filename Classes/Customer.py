class Customer:
    # Constructor
    def __init__(self, id, demand, service_time):
        # customer's id
        self.id = id
        # customer's demand
        self.demand = demand
        # customer's service time
        self.service_time = service_time
        # customer is not on a route
        self.is_routed = False