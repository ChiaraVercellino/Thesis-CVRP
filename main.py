# import sys to deal with command line arguments
import sys

# import functions made by me
from InputOutput import load_distribution, save_data_costumers, save_selected_costumers, save_routes, plot_routes
from CostumerSelection import select_customers
from Day import Day
from Vehilcle import Vehicle, inizialize_vehicles
from mainVRP import VRP_optimization


def main():
    # parse command line arguments
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    policy = sys.argv[3]

    # empty pre-existent files
    with open(output_path, 'r+') as fp:
        fp.truncate(0)    
    with open('selected_customers.txt', 'r+') as fp:
        fp.truncate(0)
    with open('routes.txt', 'r+') as fp:
        fp.truncate(0)

# ------------------------------------------------ DATA LOADING -------------------------------------------------------
    # load distribution and depot position from input file
    data_frame, depot = load_distribution(input_path)

# ------------------------------------------------- SIMULATION --------------------------------------------------------
    # new customers arriving  in a day
    new_customers = 400
    # Days used in simulation
    n_days = 3
    first_day = True

    # number of available small vehicles
    small_vehicles = 50
    # dimensions small vehicles (m and kg)
    length_small = 4.20
    width_small = 20.0
    height_small = 23.0
    capacity_small = 10*100
    # number of available big vehicles
    big_vehicles = 0
    # dimensions big vehicles (m and kg)
    length_big = 6.20
    width_big = 12.0
    height_big = 45.0
    capacity_big = 25*100
    # initialize vehicles
    kg_capacity, m3_capacity = inizialize_vehicles(length_small, width_small, height_small, capacity_small, small_vehicles,
                        length_big, width_big, height_big, capacity_big, big_vehicles)
    print(f'Total available capacity: {kg_capacity} kg, {m3_capacity} m^3')
    
    for _ in range(n_days):

        # Instantiate a new day
        if first_day:
            new_day = Day(new_customers, first_day, data_frame)
            first_day = False
        else:
            # append new customers to the ones of previous day
            new_day = Day(new_customers, previous_df=new_day.customer_df)

        # save simulated data
        save_data_costumers(new_day, output_path)

        # ---------------------------------------- Customers selection ------------------------------------------------

        # select customers accordingly to the desired policy
        selected_customers, selected_indexes, updated_day = select_customers(new_day, m3_capacity, kg_capacity, policy)
        # save selected customer to pass to VRP solver
        save_selected_costumers(new_day, selected_customers)
        # delete served customer
        updated_day.delete_served_customers(selected_indexes)
        # update the day
        new_day = updated_day
        
        # ---------------------------------------- VRP optimization ---------------------------------------------------

        data, manager, routing, solution = VRP_optimization(selected_customers, depot, small_vehicles+big_vehicles, capacity_small)

        # ---------------------------------------- Save daily roads----------------------------------------------------
        routes_list = save_routes(new_day, data, manager, routing, solution)
        plot_routes(selected_customers, depot, routes_list, updated_day.current_day)

if __name__ == '__main__':
    main()
