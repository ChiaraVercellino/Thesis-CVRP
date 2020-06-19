# To deal with data frame
import pandas as pd
# To deal with numerical operations
import numpy as np
# To sample from a multinomial distribution
from numpy.random import multinomial

# import constant for seed of pseudo-random generator
import constant

# deactivate chained warning
pd.options.mode.chained_assignment = None

# Define class to get for each day the informations about custumer
class Day:    
    # class variable, to count number of day for simulation
    current_day = 0
    # the data frame of distribution is common to all days
    df_distribution = pd.DataFrame()

    # ------------------------------------------ CONSTRUCTOR ----------------------------------------------------------

    def __init__(self, num_customers, first_day=False, df_distribution=[], previous_df=[]):
        # Initialize distribution data frame
        if first_day:
            Day.df_distribution = df_distribution            
            # To set seed for random generator (replicability)
            np.random.seed(constant.SEED)
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
        self.selected_customers = pd.DataFrame()
        self.selected_indexes = []

    # ------------------------------------------ PRIVATE METHODS ------------------------------------------------------

    # Simulate n_customers clients, starting from probability distribution in df, consider this as a private function
    def _simulate_customers(self, n_customers):
        # extract probabilities for each cell
        probs = self.df_distribution['probability']
        # simulate a multinomial distribution on the cells
        demands_cell = multinomial(n_customers, probs)
        # copy the interested rows in data frame
        selected_cells = self.df_distribution[demands_cell > 0]
        # add a column corresponding to the number of client to simulate for each cell
        selected_cells['demands'] = demands_cell[demands_cell > 0]
        # initialize empty coordinates
        customers_data = {'x': [], 'y': [], 'kg': [], 'set_up_time': [], 'last_day': [], 'yet_postponed': [], 'cell': [], 'index': []}
        # simulate coordinates for each customer
        selected_cells.apply(lambda line: self._simulate_clients_parameters(line.cell_name, line.x, line.length, line.y, line.height,
                                                                            line.demands, customers_data), axis=1)
        return customers_data

    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------

    # Update data frame dropping served customers
    def delete_served_customers(self):
        # drop customer indexes of selected customer
        self.customer_df = self.customer_df.drop(self.selected_indexes)

    # Save the simulated data of each customer
    def save_data_costumers(self, file_path='./Data/simulated_clients.txt'):
        # append new data to the previous ones
        with open(file_path, 'a') as fp:
            fp.write(f'\n DAY: {self.current_day} \n')
            # write all data frame to in a file
            fp.write(self.customer_df.to_string(header=True, index=True))

    # Save selected customers customer
    def save_selected_costumers(self, file_path='./Data/selected_customers.txt'):
        # append new data to the previous ones
        with open(file_path, 'a') as fp:
            fp.write(f'\n DAY: {self.current_day} \n')
            # write all data frame to in a file
            fp.write(self.selected_customers.to_string(header=True, index=True))

    # ------------------------------------------ STATIC METHODS -------------------------------------------------------

    @staticmethod
    # Simulate the position of num_clients customers using a uniform distribution on the cell
    def _simulate_clients_parameters(cell_name, x, dx, y, dy, num_clients, custom_data):
        num_clients = np.int_(num_clients)
        # save the cell
        custom_data['cell'] += [np.int(cell_name)]*num_clients
        # initialize index
        custom_data['index'] += [0]*num_clients
        # save all x coordinates
        custom_data['x'] += np.random.uniform(x, x + dx, num_clients).tolist()
        # save all y coordinates
        custom_data['y'] += np.random.uniform(y, y + dy, num_clients).tolist()
        # see whether the demand is for a big or small object
        big = np.random.binomial(n=1, size=num_clients, p=constant.PROB_BIG)
        # set time windows in day for each customer
        custom_data['last_day'] += np.random.randint(low=Day.current_day+3, high=Day.current_day+5,size=num_clients).tolist()
        # at the beginning no customer has been postponed
        custom_data['yet_postponed'] = False
        for cl in range(num_clients):
            # save demand in kg
            custom_data['kg'] += np.random.randint(low=constant.SMALL_KG_MIN+constant.BIG_KG_MIN*big[cl],\
                 high=constant.SMALL_KG_MAX+constant.BIG_KG_MAX*big[cl],size=1).tolist()
            # calculate set up times
            custom_data['set_up_time'] += np.random.randint(low=constant.SMALL_TIME_MIN+constant.BIG_TIME_MIN*big[cl],\
                 high=constant.SMALL_TIME_MAX+constant.BIG_TIME_MAX*big[cl],size=1).tolist()
        return custom_data


