# To deal with data frame
import pandas as pd
# To deal with numerical operations
import numpy as np
# To sample from a multinomial distribution
from numpy.random import multinomial

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
        # each new day is a new day
        Day.current_day += 1
        # Initialize distribution data frame
        if first_day:
            Day.df_distribution = df_distribution
        # Simulate new customer for the current day
        new_customers = self._simulate_customers(num_customers)
        # Convert dictionary to data frame
        new_customer_df = pd.DataFrame(new_customers)
        # Update all customers' data frame
        if first_day:
            self.customer_df = new_customer_df
        else:
            self.customer_df = previous_df.append(new_customer_df, ignore_index=True)

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
        customers_data = {'x': [], 'y': [], 'm3': [], 'kg': [], 'set_up_time': [], 'last_day': [], 'yet_postponed': []}
        # simulate coordinates for each customer
        selected_cells.apply(lambda line: self._simulate_clients_parameters(line.x, line.length, line.y, line.height,
                                                                            line.demands, customers_data), axis=1)
        return customers_data

    # ------------------------------------------ PUBLIC METHODS -------------------------------------------------------

    # update data frame dropping served customers
    def delete_served_customers(self, indexes_customers):
        # drop customer indexes of selected customer
        self.customer_df = self.customer_df.drop(indexes_customers)

    # ------------------------------------------ STATIC METHODS -------------------------------------------------------

    @staticmethod
    # Simulate the position of num_clients customers using a uniform distribution on the cell
    def _simulate_clients_parameters(x, dx, y, dy, num_clients, custom_data):
        # save all x coordinates
        custom_data['x'] += np.random.uniform(x, x + dx, num_clients).tolist()
        # save all y coordinates
        custom_data['y'] += np.random.uniform(y, y + dy, num_clients).tolist()
        # see whether the demand is for a big or small object
        big = np.random.binomial(n=1, size=num_clients, p=0.5)
        # set time windows in day for each customer
        custom_data['last_day'] += np.random.randint(low=Day.current_day+3, high=Day.current_day+5,
                                                     size=num_clients).tolist()
        # at the beginning no customer has been postponed
        custom_data['yet_postponed'] = False
        for cl in range(num_clients):
            # save demand in m^3
            custom_data['m3'] += np.random.uniform(1+199*big[cl], 3+277*big[cl], 1).tolist()
            # save demand in kg
            custom_data['kg'] += np.random.uniform(1+199*big[cl], 10+590*big[cl], 1).tolist()
            # calculate set up times
            custom_data['set_up_time'] += np.random.uniform(0.15+0.85*big[cl], 1.0+3.5*big[cl], 1).tolist()
        return custom_data


