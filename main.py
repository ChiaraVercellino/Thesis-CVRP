# import sys to deal with command line arguments
import sys

# import functions
from Functions.InputOutput import load_distribution, save_routes, clean_files, check_arguments
from Functions.CostumerSelection import select_customers, remove_client_VRP
from Classes.Day import Day
from VRP_optimization.mainVRP import VRP_optimization
from VRP_optimization.main_VRPH import main_VRPH
from VRP_optimization.main_VRPortools import main_VRPortools


def main():
    # parse command line arguments
    error, input_path, policy, n_days = check_arguments(sys.argv)
    if error:
        return
    # empty pre-existent files
    clean_files()

# ------------------------------------------------ DATA LOADING -------------------------------------------------------
    # load distribution and depot position from input file
    data_frame, depot = load_distribution(input_path)

# ------------------------------------------------- SIMULATION --------------------------------------------------------
    # new customers arriving  in a day
    new_customers = 180
    total_obj_fun = 0
    first_day = True

    # number of available vehicles
    vehicles = 50
    # capacity of each vehicle
    capacity = 1000
    # total available capacity (kg)
    kg_capacity = vehicles*capacity
    # total available time (min)
    min_capacity = 8*60*vehicles
    #print(f'Total available capacity: {kg_capacity} kg, {min_capacity} min')    
    

    for _ in range(n_days):
        
        # Instantiate a new day
        if first_day:
            new_day = Day(new_customers, first_day, data_frame)
            first_day = False
        else:
            # append new customers to the ones of previous day
            new_day = Day(new_customers, previous_df=new_day.customer_df)

        print(f'Simulated day {new_day.current_day}')
        # save simulated clients' data
        new_day.save_data_costumers()
        # ---------------------------------------- Customers selection ------------------------------------------------

        # select customers accordingly to the desired policy
        updated_day, num_postponed = select_customers(new_day, min_capacity, kg_capacity, policy)

        # ---------------------------------------- VRP optimization ---------------------------------------------------
        solution = False
        # iterate until a feasible solution is reached
        while not(solution):
            data, manager, routing, solution = VRP_optimization(updated_day.selected_customers, depot, vehicles, capacity)
            if not(solution):                
                updated_day = remove_client_VRP(updated_day)

        # ---------------------------------------- Save daily roads ---------------------------------------------------

        # save daily roads
        routes_list = save_routes(new_day, data, manager, routing, solution)

        # --------------------------------------- Final updates -------------------------------------------------------
        
        # save selected customer passed to VRP solver
        updated_day.save_selected_costumers()        
        # delete served customer
        updated_day.delete_served_customers()        
        # update the day
        new_day = updated_day

        # --------------------------------------- Objective function --------------------------------------------------
        # In DP we start serving customers from the 4th day, we need to do a right comparison among the policies
        total_obj_fun += solution.ObjectiveValue()

    print(f'Total objective function: {total_obj_fun}')
    print(f'Total number of postponed costumers: {num_postponed}')

    return


if __name__ == '__main__':
    main()
