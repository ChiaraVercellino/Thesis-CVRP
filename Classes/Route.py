'''
This class is used to define the routes' paths for the vehicles that visit customers of the CVRP.

Each object of class Route has the following attributes:
    id: integer number that ideantifies the route
    cap_kg: load-capacity, expressed in kg, of the vehicle traveling along the route
    cap_min: duration-capacity, expressed in min, of the vehicle traveling along the route
    cap_cust: customers-capacity, expressed in number of customers, of the vehicle traveling along the route
    load_kg: total load of goods carried by the vehicle along the route
    load_min: total duration of the route, it takes count of both the travel times and the service times
    load_cust: total number of customers visited along the route
    route: list containing the path of the routes, the path is expressed by integer numbers that refer to the indexes of customers' and the depot 0

These attributes can be managed through the following public methods:
    initialize_route(self, customer, depot_distance)
    check_constraints(self)
    delete_route()

'''

# import constant for fixed parameters
import constant

class Route:
    # Counter for the number of the routes: it is used to maintain unique identifiers for the routes
    num_route = 0

    # ------------------------------------------ CONSTRUCTOR ----------------------------------------------------------

    def __init__(self, cap_kg=constant.CAPACITY, cap_min=constant.TIME, cap_cust=constant.CUSTOMER_CAPACITY):
        '''
        Construction of class Day.
        INPUTS:
            [cap_kg]: load-capacity of the vehicle that travels along the route (kg)
            [cap_min]: duration-capacity of the vehicle that travels along the route (min)
            [cap_cust]: customers-capacity of the vehicle that travels along the route (number of customers)
        '''
        self.id = Route.num_route
        # Increment the routes' counter
        Route.num_route += 1
        # kg capacity of the vehicle
        self.cap_kg = cap_kg;
        # minutes capacity of the vehicle
        self.cap_min = cap_min
        # customers' capacity of the vehicle
        self.cap_cust = cap_cust
        # load of the vehicle (kg)
        self.load_kg = 0
        # minutes' load of the vehicle
        self.load_min = 0
        # customers' load of the vehicle
        self.load_cust = 0
        # customers on the route of vehicle, at the begining only the depot belongs to the path of the route and it is both starting and ending
        # location for the route
        self.route = [0, 0]

    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------

    def initialize_route(self, customer, depot_distance):
        '''
        Route initialization: it adds one customer to the route and updates the loads' attributes and the route path.
        INPUT:
            customer: integer identifier of the customer to be added
            depot_distance: distance between customer's location and the depot, this distance is expressed in km, but, since we consider vehicles
                            that travel at the average speed of 60 km/h, it is also the travel time to go from the depot to the customer's location
                            in minutes
        '''
        # add the load of the customer's demand
        self.load_kg = customer.demand
        # update the time-load considering customer's service time and the distance from the depot. The depot distance is counted twice because the
        # vehicle starts from the depot, visit the customer and then goes back to the depot.
        self.load_min = customer.service_time + 2*depot_distance
        # customers' load of vehicle: only one customer
        self.load_cust = 1
        # insert the customer in the route
        self.route.insert(1, customer.id)

    def check_constraints(self):
        '''
        Check if all the capacity constraints are satisfied:
        - the constraint on the number of customers visited by the vehicle
        - the constraint on the total duration of the vehilcle's work shift
        - the constraint on the maximum load that could be carried by the vehicle

        OUTPUT
            constraint: boolean value, it is True if all the constraints are met, False otherwise
        '''
        # check customers-capacity constraint
        cust = self.load_cust <= self.cap_cust
        # check time-capacity constraint
        time = self.load_min <= self.cap_min
        # check load-capacity constraint
        kg = self.load_kg <= self.cap_kg
        # check if all constraints are met
        constraint = cust and time and kg
        return constraint

    @staticmethod
    def delete_route():
        '''
        Delete the route: the next route will overwrite the preceeding one.
        '''
        # Decrement routes' counter
        Route.num_route -= 1


