# import sys to deal with command line arguments
import sys

# import functions
from Functions.InputOutput import load_distribution, save_routes, clean_files, check_arguments
from Functions.CostumerSelection import select_customers
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
    new_customers = 400
    first_day = True

    # number of available vehicles
    vehicles = 50
    # capacity of each vehicle
    capacity = 10*100
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

        # save simulated clients' data
        new_day.save_data_costumers()

        # ---------------------------------------- Customers selection ------------------------------------------------

        # select customers accordingly to the desired policy
        updated_day = select_customers(new_day, min_capacity, kg_capacity, policy)
        # save selected customer to pass to VRP solver
        updated_day.save_selected_costumers()
        # delete served customer
        updated_day.delete_served_customers()
        # update the day
        new_day = updated_day
        
        # ---------------------------------------- VRP optimization ---------------------------------------------------

        data, manager, routing, solution = VRP_optimization(new_day.selected_customers, depot, vehicles, capacity)

        # ---------------------------------------- Save daily roads----------------------------------------------------
        if solution:
            routes_list = save_routes(new_day, data, manager, routing, solution)

    return


if __name__ == '__main__':
    main()
