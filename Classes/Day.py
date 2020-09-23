'''
This class is used to manage information about customers day by day.

In particular each object of class Day has the following attributes:
    current_day: integer representing current day in simulation
    df_distribution: dataframe containing information about cells and distribution of customers over them
    customer_df: dataframe of pending customers
    selected_customers: dataframe of customers selected for CVRP
    selected_indexes: list of indexes of selected customers for CVRP

These attributes can be managed through the following public methods:
    delete_served_customers(self)
    save_data_costumers(self, file_path='./Data/simulated_clients.txt')
    save_selected_costumers(self, file_path='./Data/selected_customers.txt')

In dataframes customer_df and selected_customers each row represents a customer, the columns are the following:
    'x': x-coordinate of the customer in the region
    'y': y-coordinate of the customer in the region
    'kg': demand of the customer in kg
    'service_time': time to serve the customer in min
    'last_day': last available day to serve the customer
    'yet_postponed': flag that is set to False by default and will become True if the customer is postponed
    'cell': cell to which the customer belong
    'index': index used in policy NP or NP_1

'''


# To deal with data frame
import pandas as pd
# To deal with numerical operations
import numpy as np
# To sample from a multinomial distribution
from numpy.random import multinomial

# import constant for fixed parameters
import constant

# deactivate chained warning
pd.options.mode.chained_assignment = None


class Day:    
    # class variable, to count number of day for simulation
    current_day = 0
    # the data frame of distribution is common to all days
    df_distribution = pd.DataFrame()

    # ------------------------------------------ CONSTRUCTOR ----------------------------------------------------------

    def __init__(self, num_customers, first_day=False, df_distribution=[], previous_df=[]):
        '''
        Construction of class Day.
        INPUTS:
            num_customers: number of new customers that show up this day
            [first_day]: flag that specify if this object of class Day is the first of simulation.
                         True if it is the first day of simulation
                         False if it is not the first day of simulation
            [df_distribution]: dataframe containing information about cells and distribution of customers over them
            [previous_df]: dataframe of pending customers of previous day
        '''
        
        if first_day:
            # Initialize cell's distribution dataframe
            Day.df_distribution = df_distribution            
            # Set seed for random generator (replicability)
            np.random.seed(constant.SEED)
            # Initialize counter of days in simulation
            Day.current_day = 0
        # each new day is a new day
        Day.current_day += 1
        # Simulate new customer for the current day
        new_customers = self._simulate_customers(num_customers)
        # Convert dictionary to data frame
        new_customer_df = pd.DataFrame(new_customers)
        # Update all customers' data frame
        if first_day:
            self.customer_df = new_customer_df
        else:
            self.customer_df = previous_df.append(new_customer_df, ignore_index=True)
        # initialize selected_customers dataframe
        self.selected_customers = pd.DataFrame()
        # initialize selected_indexes list
        self.selected_indexes = []

    # ------------------------------------------ PRIVATE METHODS ------------------------------------------------------

    
    def _simulate_customers(self, n_customers):
        '''
        Simulate new costumers, starting from probability distribution of cells.
        INPUT:
            n_customers: number of customers to simulate
        OUTPUT:
            customers_data: dictionary containing for each simulated customer
                            'x' x-coordinate in the region
                            'y' y-coordinate in the region
                            'kg' demand of the customer in kg
                            'service_time' time to serve the customer in min
                            'last_day' last available day to serve the customer
                            'yet_postponed' flag that is set to False and will become True if the customer is postponed
                            'cell' cell to which the customer belong
                            'index' index used in policy NP or NP_1
        '''
        # extract probabilities for each cell
        probs = self.df_distribution['probability']
        # simulate a multinomial distribution on the cells
        demands_cell = multinomial(n_customers, probs)
        # copy the interested rows in data frame
        selected_cells = self.df_distribution[demands_cell > 0]
        # add a column corresponding to the number of costumers to simulate for each cell
        selected_cells['demands'] = demands_cell[demands_cell > 0]
        # initialize empty dictionary
        customers_data = {'x': [], 'y': [], 'kg': [], 'service_time': [], 'last_day': [], 'yet_postponed': [], 'cell': [], 'index': []}
        # simulate customers
        selected_cells.apply(lambda line: self._simulate_clients_parameters(line.cell_name, line.x, line.length, line.y, line.height,
                                                                            line.demands, customers_data), axis=1)
        return customers_data

    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------

    
    def delete_served_customers(self):
        '''
        Update data frame dropping served customers: the list selected_index contains the indexes of selected customers in
        customer_df, those costumers has been served, solving CVRP, so they are no longer pending ones.
        '''
        # drop customer indexes of selected customer
        self.customer_df = self.customer_df.drop(self.selected_indexes)

    
    def save_data_costumers(self, file_path='./Data/simulated_clients.txt'):
        '''
        Save data for simulated customers.
        INPUT:
            [file_path]: path to file in which the dataframe customer_df will be saved
        '''
        # append new data to the previous ones
        with open(file_path, 'a') as fp:
            fp.write(f'\n DAY: {self.current_day} \n')
            # write all data frame in the file
            fp.write(self.customer_df.to_string(header=True, index=True))

    
    def save_selected_costumers(self, file_path='./Data/selected_customers.txt'):
        '''
        Save customers that have been selected for CVRP, the ones that have been served.
        INPUT:
            [file_path]: path to file in which the dataframe selected_customers will be saved
        '''
        # append new data to the previous ones
        with open(file_path, 'a') as fp:
            fp.write(f'\n DAY: {self.current_day} \n')
            # write all data frame in the file
            fp.write(self.selected_customers.to_string(header=True, index=True))

    # ------------------------------------------ STATIC METHODS -------------------------------------------------------

    @staticmethod
    def _simulate_clients_parameters(cell_name, x, dx, y, dy, num_clients, custom_data):
        '''
        Simulate the position, the demand, the availability to be served and the service time for new customers.
        INPUTS:
            cell_name: cell id of the customers to simulate
            x: x-coordinate of top left bound of the cell
            dx: lenght of the cell
            y: y-coordinate of lower bound of the cell
            dy: height of the cell
            num_clients: number of customers belonging to the selected cell to simulate
            custom_data: dictionary containing all information about customers
        OUTPUT:
            custom_data: dictionary containing all information about customers (updated)
        '''

        # cast to int
        num_clients = np.int_(num_clients)
        # save the cell id
        custom_data['cell'] += [np.int(cell_name)]*num_clients
        # initialize index
        custom_data['index'] += [0]*num_clients
        # save all x coordinates
        custom_data['x'] += np.random.uniform(x, x + dx, num_clients).tolist()
        # save all y coordinates
        custom_data['y'] += np.random.uniform(y, y + dy, num_clients).tolist()
        # see whether the demand is for a big or small object
        big = np.random.binomial(n=1, size=num_clients, p=constant.PROB_BIG)
        # set last available day for each customer
        custom_data['last_day'] += np.random.randint(low=Day.current_day+constant.MIN_DAY, high=Day.current_day+constant.MAX_DAY,
                                                    size=num_clients).tolist()
        # at the beginning no customer has been postponed
        custom_data['yet_postponed'] = False
        for cl in range(num_clients):
            # save demand in kg
            custom_data['kg'] += np.random.randint(low=constant.SMALL_KG_MIN+constant.BIG_KG_MIN*big[cl],\
                 high=constant.SMALL_KG_MAX+constant.BIG_KG_MAX*big[cl],size=1).tolist()
            # save service times
            custom_data['service_time'] += np.random.randint(low=constant.SMALL_TIME_MIN+constant.BIG_TIME_MIN*big[cl],\
                 high=constant.SMALL_TIME_MAX+constant.BIG_TIME_MAX*big[cl],size=1).tolist()
        return custom_data


