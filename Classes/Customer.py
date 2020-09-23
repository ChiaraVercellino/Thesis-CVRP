'''
This class is used to represent customers's demands.

Each object of class Customer has the following attributes:
    id: integer number that idenitifies the customer's order
    demand: the amount of good requested by the customer, it is expressed in kg
    service_time: the estimated time to perform the service for the customer
'''

class Customer:
    def __init__(self, id, demand, service_time):
        '''
        Construction of class Customer.
        INPUTS:
            id: number of new customers that show up this day
            demand: customer's demand (kg)
            service_time: customer's service time (min)
        '''
        # customer's id
        self.id = id
        # customer's demand
        self.demand = demand
        # customer's service time
        self.service_time = service_time