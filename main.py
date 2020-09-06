""" 
MAIN

Problem definition:
We consider Capacitated Vehicle Routing Problem (CVRP) with stochastics customers that show up day by day. The set of future customers
is not known a priori, but a spatial distribution is supposed to be known. The position of the depot is fixed and central.
The objective funtion is to minimize the total cost of service up the last day of simulation.
So we want to minimize:
- Total travel time
- Total number of vehicles used
The constraints we are taking into account are:
- Total capacity on each vehicle (kg)
- Maximum number of customer each vehicle can serve in a day
- Total working time of each vehicle: service time + travel time


Summary:
The distribution of customers' arrivals, the policy for customer selection and the number of days for simulation are givem as input
parameters as command line arguments.
The we simulate the arrivals of the customers and select which ones to serve day by day.
Once selected the customers to serve, a CVRP is solved to minimize the travel cost and the total number of vehicles to use.
The simulated customers, the ones selected for CVRP and the best routes found day by day are saved in output files.
Some statistics about the simulation are printed on the standard output.


Main steps of simulation:

1) INITIALIZATION: read command-line arguments, empty pre-existent simulation file, initialize variables used in simulation
2) DATA LOADING: read customers' distribution from input file
Optional) NP & NP_1: costruct variables that are needed only for policy NP and NP_1
3) SIMULATION: each day
    - Customers simulation: simulate new customers and save data related to pending customers in the current day
    - Customers selection: select which customers to serve in the current day.
                          The following selection policies are available:
                          - EP: early policy, each customer is served as soon as he makes a request
                          - DP: delayed policy, each customer is served in the last day of his availability period
                          - NP: neighbourhood policy: to each pending customer is associated a index that takes into account
                                                      the distribution of his neighbours. Customers are then selected by
                                                      decreasing index
                          - NP_1: neighbourhood policy bis: to each pending customer is associated a index that takes into account
                                                            the distribution of his neighbours, the amount of its demand in terms
                                                            of service time and its distance from the depot. Customers are then 
                                                            selected by decreasing index
    - CVRP optimization: find a feasible solution to CVRP problem with the selected customers or a subset of them
    - Save daily routes: append to solution file the new best routes find by CVRP solver
    - Final updates: save the information related to selected customers that lead to a feasible solution of CVRP and
                     delete from pending customers the served ones
    - Objective function: update value of objective function adding up the daily travel time
4) STATISTICS: compute final statistics
    - Total objective funcion: total minutes of travel time along all days of simulation
    - Total number of postponed customers: each time that a customer cannot be served within his last available day it is
      postponed to the following day
    - Average of empty vehicles: mean over the number of vehicles used each day of simulation
    - Average of served customers: mean over the number of customers served each day
    - Average of cycles: there is a cycle over CVRP solver that guarantees the feasibility of the daily solution, each time that the
                         problem is unfeasible a customer is removed from the list of the customers to serve in the current day and 
                         the solution with CVRP solver is tried again and the number of daily cycles is incremented by one.
    - Average of travel cost: mean over the daily travel time 
    - Time for simulation: total time to run simulation (hh:mm:ss)

"""

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
from Functions.CostumerCompatibility import select_compatible_cells
from Classes.ClarkWrightSolver import ClarkWrightSolver
from Classes.TabuSearch import TabuSearch

# import constant variables
import constant


def main():

# ------------------------------------------------ INITIALIZATION -------------------------------------------------------

    tabu_len = 60
    gap_worse = 300
    np.random.seed(constant.SEED)
    # starting time for simulation  
    start = time.time()
    # parse command line arguments:
    # error: there is an erroe in the arguments
    # input_path: path to file containing the distribution of cells
    # n_days: days of simulation
    error, input_path, policy, n_days, solver = check_arguments(sys.argv)
    if error:
        return
    # empty pre-existent files: Solution/routes.sol, Data/selected_customers.txt, Data/simulated_clients.txt
    clean_files()

    # new customers arriving in each day
    new_customers = np.random.randint(low=constant.AVG_CUSTOMERS-constant.GAP_CUSTOMERS,\
        high=constant.AVG_CUSTOMERS+constant.GAP_CUSTOMERS, size=n_days)
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
    # number of while cycles in each day to get a feasible solution for CVRP
    num_cycles = [0]*n_days
    # daily travel cost
    daily_obj = [0]*n_days
    # initialize objective function
    total_obj_fun = 0
    # Initialize flag for simulation
    first_day = True
    # daily tabu serch iterations
    daily_tabu = [0]*n_days

# ------------------------------------------------ DATA LOADING -------------------------------------------------------

    # load distribution and depot position from input file:
    # distribution_df: a pandas dataframe where each row contains information about a cell of the simulated region
    # depot: numpy array with x-coordinate and y-coordinate of the depot
    distribution_df, depot = load_distribution(input_path)

# ------------------------------------------------ NP & NP_1 variables -------------------------------------------------------

    # This variables are empty lists for EP and NP policies
    compatibility_list = []
    compatibility_index = []
    depot_distance = []
    if policy == "NP" or policy == "NP_1":
        # compatibility_list: list with dimension equal to the number of cells, each element of the list is a list of
        #                     neighbours cells that allow percentage savings > rho
        # compatibility_index: symmetric matrix with dimension #cells*#cells, each element (i,j) is the percentage saving
        #                      including cell i and cell j in the same route
        # depot_distance: numpy array with dimension equal to the number of cells, each element is the Euclidean distance
        #                 from depot to the centre of a cell
        compatibility_list, compatibility_index, depot_distance = select_compatible_cells(distribution_df, depot, constant.rho)
    
# ------------------------------------------------- SIMULATION ---------------------------------------------------------

    for day in range(n_days):
        
        # ---------------------------------------- Customers simulation ------------------------------------------------

        # Instantiate a new day
        # new day: object of class Day with attributes
        # current_day -> number of the current day in simulation
        # df_distribution -> distribution_df
        # customer_df -> dataframe of pending customer
        # selected_customers -> dataframe of selected customers
        # selected_indexes -> list of index of selected customers
        if first_day:
            new_day = Day(new_customers[day], first_day, distribution_df)
            first_day = False
        else:
            # append new customers to the ones that were not served in the previous day
            new_day = Day(new_customers[day], previous_df=new_day.customer_df)

        #print(f'Simulated day {new_day.current_day}')

        # save simulated clients' data
        new_day.save_data_costumers()

        # ---------------------------------------- Customers selection ------------------------------------------------

        # select customers accordingly to the desired policy:
        # updated_day: object of class Day with updates regarding attributes customer_df, selected_customers, selected_indexes
        # num_postponed: total number of customers postponed up to the current day
        updated_day, num_postponed = select_customers(new_day, min_capacity, kg_capacity, policy, compatibility_list,\
                distribution_df.probability, compatibility_index, depot_distance)

        # ---------------------------------------- CVRP optimization ---------------------------------------------------
        
        # flag for while cycle
        solution = False
        # iterate until a feasible solution is reached
        while not(solution):
            num_cycles[day] += 1
            # Solve CVRP
            # data: dictionary containig information about
            #      'distance_matrix' -> travel time + service time of selected customers
            #      'num_vehicles' -> number of available vehicles
            #      'depot' -> index of depot
            #      'demands' -> list of demands of selected customers in kg
            #      'vehicle_capacities' -> list of capacities of each vehicle in kg
            # manager: routing index manager
            # routing: routing model
            # solution: solution to CVRP

            if solver == 'ortools':
                data, manager, routing, solution, obj_value = VRP_optimization(updated_day.selected_customers, depot, vehicles, capacity)

            elif solver == 'tabu':                                 
                start_tabu = time.time()
                elapsed_time = 0
                clark_wright_sol = ClarkWrightSolver(updated_day.selected_customers, depot)
                solution = clark_wright_sol.solve()
                if solution:
                    
                    tabu_search = TabuSearch(clark_wright_sol, constant.MAX_TIME, tabu_len, gap_worse)                            
                    ii=0
                    while elapsed_time <= constant.MAX_TIME:
                        ii+=1
                        tabu_search.solve()
                        elapsed_time = time.time()-start_tabu
                    tabu_search.final_optimization()
                    tabu_search_sol = tabu_search.current_solution
                    daily_tabu[day] = ii
                    #tabu_search_sol = clark_wright_sol
                    #print('Iter {}, Worse {}, Tabu {}, Best {}, Small {} -> {}'.format(ii, tabu_search.num_worse, \
                    #    tabu_search.num_tabu, tabu_search.num_best, len(clark_wright_sol.small_routes), \
                    #        len(tabu_search.small_routes_ids)))
                    
                        
                    
                    
            if not(solution):
                # I've selected too many customers so the CVRP became unfeasible, so I remove one client from selected_customers,
                # selected_indexes and I put it again in customer_df to be served in the following days               
                updated_day = remove_client_VRP(updated_day)
        # save number of served customers
        num_served_clients[day] = len(updated_day.selected_customers)
        # save total service time for served customers
        total_time = updated_day.selected_customers.service_time.sum()

        # ---------------------------------------- Save daily routes --------------------------------------------------
        
        # save daily roads in Solution/routes.sol
        if solver == 'ortools':
            num_empty_route[day] = save_routes(updated_day, data, manager, routing, solution)
        elif solver == 'tabu':
            num_empty_route[day] = tabu_search_sol.print_solution(updated_day)
        
        # --------------------------------------- Final updates -------------------------------------------------------
        
        # save selected customer passed to VRP solver in Data/selected_customers.txt
        updated_day.save_selected_costumers()        
        # delete served customer from customer_df
        updated_day.delete_served_customers()        
        # update the day
        new_day = updated_day
        
        # --------------------------------------- Objective function --------------------------------------------------

        # In DP we start serving customers from the 4th day, we need to do a right comparison among the policies, so to
        # study the objective function on the long run I don't consider for statistics a transient period of NUM_DAYS

        # In the objective function I consider only the travel time, not the service one which cannot be optimized
        if solver == 'ortools':
            daily_obj[day] = obj_value-total_time
        elif solver == 'tabu':
            daily_obj[day] = tabu_search_sol.total_cost-total_time

        if new_day.current_day >= constant.NUM_DAYS:
            total_obj_fun += daily_obj[day]

    # ------------------------------------------------ STATISICS -------------------------------------------------------

    #print('Gap Worse {} Tabu Length {}'.format(gap_worse, tabu_len))
    # Print on the standard output some statistics
    print(f'Total objective function: {np.round(total_obj_fun,3)}')
    print(f'Total number of postponed costumers: {num_postponed}')
    print(f'Average of empty vehicles: {np.round(mean(num_empty_route[constant.NUM_DAYS-1:]),3)}')
    print(f'Average of served customers: {np.round(mean(num_served_clients[constant.NUM_DAYS-1:]))}') 
    print(f'Average of cycles: {mean(num_cycles)}') 
    print(f'Average of travel cost: {np.round(mean(daily_obj[constant.NUM_DAYS-1:]))}') 
    #print(f'Average of tabu search iterations: {mean(daily_tabu[constant.NUM_DAYS-1:])}') 
    # ending time for simulation  
    end = time.time()
    str_time = time.strftime("%H:%M:%S", time.gmtime(end-start))
    print('Time for simlation: '+str_time+'\n')

    return


# Call main function
if __name__ == '__main__':
    main()