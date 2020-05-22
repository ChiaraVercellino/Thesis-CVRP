# import sys to deal with command line arguments
import sys
# import to calculate average
from statistics import mean
# import to calculate time for simulation
import time
# import to set random seed
import numpy as np

# import functions
from Functions.InputOutput import load_distribution, save_routes, clean_files, check_arguments
from Functions.CostumerSelection import select_customers, remove_client_VRP
from Classes.Day import Day
from VRP_optimization.mainVRP import VRP_optimization
from VRP_optimization.main_VRPH import main_VRPH
from VRP_optimization.main_VRPortools import main_VRPortools
from Functions.CostumerCompatibility import select_compatible_cells

# import constant variables
import constant

np.random.seed(constant.SEED)

def main():
    # starting time for simulation  
    start = time.time()
    # parse command line arguments
    error, input_path, policy, n_days = check_arguments(sys.argv)
    if error:
        return
    # empty pre-existent files
    clean_files()

# ------------------------------------------------ DATA LOADING -------------------------------------------------------
    # load distribution and depot position from input file
    distribution_df, depot = load_distribution(input_path)
    compatibility_list = []
    # parameter to tune rho < 0.5 otherwise empty lists
    if policy == "NP":
        compatibility_list = select_compatible_cells(distribution_df, depot, constant.rho)
    
# ------------------------------------------------- SIMULATION --------------------------------------------------------
    # new customers arriving  in a day
    new_customers = np.random.randint(low=constant.AVG_CUSTOMERS-20, high=constant.AVG_CUSTOMERS+20, size=1)
    # number of available vehicles
    vehicles = constant.NUM_VEHICLES
    # capacity of each vehicle
    capacity = constant.CAPACITY
    # total available capacity (kg)
    kg_capacity = vehicles*capacity
    # total available time (min)
    min_capacity = constant.TIME*vehicles

    # initialize vector for couting empty vehicles in each day 
    num_empty_route = [0]*n_days
    # initialize vector for couting served clients in each day 
    num_served_clients = [0]*n_days
    # number of while cycles in each day
    num_cycles = [0]*n_days
    # initialize objective function
    total_obj_fun = 0
    first_day = True

    for day in range(n_days):
        
        # Instantiate a new day
        if first_day:
            new_day = Day(new_customers, first_day, distribution_df)
            first_day = False
        else:
            # append new customers to the ones of previous day
            new_day = Day(new_customers, previous_df=new_day.customer_df)

        print(f'Simulated day {new_day.current_day}')
        # save simulated clients' data
        new_day.save_data_costumers()
        # ---------------------------------------- Customers selection ------------------------------------------------

        # select customers accordingly to the desired policy
        updated_day, num_postponed = select_customers(new_day, min_capacity, kg_capacity, policy, compatibility_list,\
                distribution_df.probability)

        # ---------------------------------------- VRP optimization ---------------------------------------------------
        solution = False
        # iterate until a feasible solution is reached
        while not(solution):
            num_cycles[day] += 1
            data, manager, routing, solution = VRP_optimization(updated_day.selected_customers, depot, vehicles, capacity)
            if not(solution):                
                updated_day = remove_client_VRP(updated_day)
        # save number of served clients
        num_served_clients[day] = len(updated_day.selected_customers)
        # save total set-up time for served customers
        total_time = updated_day.selected_customers.set_up_time.sum()

        # ---------------------------------------- Save daily roads ---------------------------------------------------

        # save daily roads
        routes_list, num_empty_route[day] = save_routes(new_day, data, manager, routing, solution)

        # --------------------------------------- Final updates -------------------------------------------------------
        
        # save selected customer passed to VRP solver
        updated_day.save_selected_costumers()        
        # delete served customer
        updated_day.delete_served_customers()        
        # update the day
        new_day = updated_day

        # --------------------------------------- Objective function --------------------------------------------------
        # In DP we start serving customers from the 4th day, we need to do a right comparison among the policies
        if new_day.current_day > constant.NUM_DAYS:
            total_obj_fun += solution.ObjectiveValue()-total_time

    print(f'Total objective function: {total_obj_fun}')
    print(f'Total number of postponed costumers: {num_postponed}')
    print(f'Average of empty vehicles: {mean(num_empty_route[9:])}')
    print(f'Average of served customers: {mean(num_served_clients[9:])}') 
    print(f'Average of cycles: {mean(num_cycles)}') 
    # ending time for simulation  
    end = time.time()
    str_time = time.strftime("%H:%M:%S", time.gmtime(end-start))
    print('Time for simlation: '+str_time)

    return


if __name__ == '__main__':
    main()
