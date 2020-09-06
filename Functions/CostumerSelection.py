'''
This file contains all the functions that manage the selection of customer for CVRP, given the set of all pending customers in
a specific day.
There are 4 policies to select customer:
- Early Policy (EP): each day we select all pending customers according to the available capacity of the vehicles and
                     assigning a priority to customers based on the last day they are available to be served.
- Delayed Policy (DP): each day we select the customers whose last available day to be served is the current day.
- Neighbourhood Policy (NP): each day we select customers according to a index that expresses the reward of including a customer in
                             the set of selected customer, given the set of pending customer, the presence/absence of other
                             customers in the neighbourhood and the remainings days to serve him.
- Neighbourhood Policy 1 (NP_1): each day we select customers according to a index that expresses the reward of including a 
                                 customer in the set of selected customer, given the set of pending customer, the presence/absence 
                                 of other customers in the neighbourhood, the remainings days to serve him and, his distance from
                                 depot and his service time.
'''


import constant

# global variable: total number of customers that has been post-poned that is the one that couldn't be served within their last
#                  available day.
num_postponed = 0

def select_customers(day, min_capacity, kg_capacity, policy, compatibility, probabilities, compatibility_index, depot_distance):
    '''
    Select the customers for CVRP given the chosen policy, time constraint and capacity contraint.
    INPUTS:
        day: object of class Day containing information about current day in simulation
        min_capacity: aggregate time capacity expressed in minutes
        kg_capacity: aggregate weight capacity expressed in kg
        policy: chosen policy for customers selection ("EP", "DP", "NP", "NP_1")
        compatibility: list of dimension #cells whose elements are lists of convenient cells
        probabilities: dataframe column containig probability of a simulated customer to belong to a cell
        compatibility_index: numpy array of dimension #cells*#cells which contains the saving indexes
        depot_distance: numpy array of dimension #cells+1 containing all distance from depot to each cells (and the depot itself
                        in position 0)
    OUTPUTS:
        day: object of class Day containing information about current day in simulation (updated)
        num_postponed: total number of customers that has been postponed till the current day
    '''
    # percentage for service times: the time constraint will include both service time and travel time so I consider only a
    # percentage of the time capacity to select customers according to their service time.
    perc = constant.PERCENTAGE
    # calculate average demand (kg)
    avg_kg = day.customer_df['kg'].mean()
    # calculate average service_times (min)
    avg_service = day.customer_df['service_time'].mean()
    # approximate the maximum number of deliveries will be allowed with the available capacities
    num_deliveries = min(perc*min_capacity//avg_service, kg_capacity//avg_kg)
    # apply the desired policy
    if policy == "EP":
        selected_customers, selected_idx, new_customer_df = _early_policy(day.customer_df, day.current_day,
                                                                          num_deliveries)
    elif policy == "DP":
        selected_customers, selected_idx, new_customer_df = _delayed_policy(day.customer_df, day.current_day,
                                                                            num_deliveries)
    elif policy == "NP":
        selected_customers, selected_idx, new_customer_df = _neighbourhood_policy(day.customer_df, day.current_day,
                                                                            num_deliveries, compatibility, probabilities)
    elif policy == "NP_1":
        selected_customers, selected_idx, new_customer_df = _neighbourhood_policy_1(day.customer_df, day.current_day,
                                                                            num_deliveries, compatibility, probabilities,
                                                                            compatibility_index, depot_distance)

    # check if I've respected total capacities
    constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, perc*min_capacity)
    # iterate until the constraint is satisfied
    while not constraints_respected:
        # If capacity is not respected I have to eliminate some customer: I remove one customers from the selected ones
        selected_idx, selected_customers, new_customer_df = _remove_client(selected_customers, new_customer_df,
                                                                           day.current_day, selected_idx)
        # check constraints
        constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, perc*min_capacity)
        # reduce the deliveries
        num_deliveries -= 1
    # add labels corresponding to nodes in graph: to have a correspondence with CVRP solutions
    selected_customers['customer_label'] = range(1, len(selected_customers)+1)
    # update dataframe of pending customers
    day.customer_df = new_customer_df
    # create dataframe with selected customers
    day.selected_customers = selected_customers
    # save index of selected customers
    day.selected_indexes = selected_idx
    return day, num_postponed


def remove_client_VRP(day):
    '''
    Remove a costumer from the dataframe of selected customers.
    INPUT:
        day: object of class Day containing information about current day in simulation 
    OUTPUT:
        day: object of class Day containing information about current day in simulation
    '''
    day.selected_indexes, day.selected_customers, day.customer_df = _remove_client(day.selected_customers, day.customer_df,\
     day.current_day, day.selected_indexes)
    return day

# -------------------------------------------------------- PRIVATE METHODS ---------------------------------------------------------------------


def _early_policy(customer_df, this_day, num_deliveries):
    '''
    Early Policy: serve all customers as soon as demand happens. Select customer sorting them by urgency: try to serve at least
    customers whose last available day is near to the current day.
    INPUT:
        customer_df: dataframe containig all information about pending customers
        this_day: integer representing current day in simulation
        num_deliveries: number of deliveries (and customers) to select for CVRP
    OUTPUT:
        selected_customers: dataframe containig all information about selected customers
        selected_indexes: list of index of all selected customers
        customer_df: dataframe containig all information about pending customers (updated)
    '''
    # Order pending customers them by urgency
    customer_df = customer_df.sort_values(by=['last_day', 'yet_postponed'], axis=0, ascending=[True, False],
                                          ignore_index=False)
    # Select all more urgent customers that can be selected
    selected_customers = customer_df.head(int(num_deliveries))
    # Extract the list of selected customers' indexes of the dataframe
    selected_indexes = selected_customers.index.tolist()
    # It is possible that some urgent clients are not served: those ones have to be postponed
    customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


def _delayed_policy(customer_df, this_day, num_deliveries):
    '''
    Delayed Policy: serve only customers whose last available day is the current one.
    INPUT:
        customer_df: dataframe containig all information about pending customers
        this_day: integer representing current day in simulation
        num_deliveries: number of deliveries (and customers) to select for CVRP
    OUTPUT:
        selected_customers: dataframe containig all information about selected customers
        selected_indexes: list of index of all selected customers
        customer_df: dataframe containig all information about pending customers (updated)
    '''
    # sort all customers to try and serve the at least the ones whose orders have yet been postponed
    customer_df = customer_df.sort_values(by=['yet_postponed'], axis=0, ascending=[False],
                                          ignore_index=False)
    # list of indexes of customers whose last available day is the current one
    selected_indexes = customer_df.index[customer_df['last_day'] == this_day].tolist()
    list_length = len(selected_indexes)
    # the number of selected customers must satisfy capacity constraints
    selected_customers = customer_df[customer_df['last_day'] == this_day].head(int(min(list_length, num_deliveries)))
    # check if all these customers can be served
    if list_length > num_deliveries:
        selected_indexes = selected_indexes[:int(num_deliveries)]
        # It is possible that some urgent clients are not served: those ones have to be postponed
        customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


# serve customers according to probability of future demands of neighbours
def _neighbourhood_policy(customer_df, this_day, num_deliveries, compatibility, probabilities):
    '''
    Neighbourhood Policy: each day we select customers according to a index that expresses the reward of including a customer in
    the set of selected customer, given the set of pending customer, the presence/absence of other customers in the neighbourhood
    and the remainings days to serve him..
    INPUT:
        customer_df: dataframe containig all information about pending customers
        this_day: integer representing current day in simulation
        num_deliveries: number of deliveries (and customers) to select for CVRP
        compatibility: list of dimension #cells whose elements are lists of convenient cells
        probabilities: dataframe column containig probabilities of a customer to belong to each cell
    OUTPUT:
        selected_customers: dataframe containig all information about selected customers
        selected_indexes: list of index of all selected customers
        customer_df: dataframe containig all information about pending customers (updated)
    '''
    # create a set containig all the cells of pending customers
    all_cells = set(customer_df['cell']-1)
    # add a column to customer_df containig the index for selection
    customer_df = customer_df.apply(lambda line: _index_selection(line, compatibility[line.cell-1], this_day, all_cells, probabilities), axis=1)
    # sort customer_df according to the index
    customer_df = customer_df.sort_values(by=['index'], axis=0, ascending=[False], ignore_index=False)
    # calculate how many customers have index above a given threshold
    num_convenient_deliveries = len(customer_df[customer_df['index']>=constant.threshold])
    # the number of deliveries must satisfy capacity constraints
    num_deliveries = min(num_deliveries, num_convenient_deliveries)
    # dataframe of selected customers
    selected_customers = customer_df.head(int(num_deliveries))
    # list of indexes fo selected customers
    selected_indexes = selected_customers.index.tolist()
    # It is possible that some urgent clients are not served: those ones has to be postponed
    customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


def _neighbourhood_policy_1(customer_df, this_day, num_deliveries, compatibility, probabilities, compatibility_index, depot_distance):
    '''
    Neighbourhood Policy 1: each day we select customers according to a index that expresses the reward of including a 
    customer in the set of selected customers, given the set of pending customers, the presence/absence of other customers 
    in the neighbourhood, the remainings days to serve him and, his distance from depot and his service time.
    INPUT:
        customer_df: dataframe containig all information about pending customers
        this_day: integer representing current day in simulation
        num_deliveries: number of deliveries (and customers) to select for CVRP
        compatibility: list of dimension #cells whose elements are lists of convenient cells
        probabilities: dataframe column containig probabilities of a customer to belong to each cell
        compatibility_index: numpy array of dimension #cells*#cells which contains the saving indexes
        depot_distance: numpy array of dimension #cells+1 containing all distance from depot to each cells (and the depot itself
                        in position 0)
    OUTPUT:
        selected_customers: dataframe containig all information about selected customers
        selected_indexes: list of index of all selected customers
        customer_df: dataframe containig all information about pending customers (updated)
    '''
    # create a set containig all the cells of pending customers
    all_cells = set(customer_df['cell']-1)
    # add a column to customer_df containig the index for selection
    customer_df = customer_df.apply(lambda line: _index_selection_1(line, compatibility[line.cell-1], this_day, all_cells, probabilities,\
                                                                    compatibility_index, depot_distance), axis=1)
    # sort customer_df according to the index
    customer_df = customer_df.sort_values(by=['index'], axis=0, ascending=[False], ignore_index=False)
    # calculate how many customers have index above a given threshold
    num_convenient_deliveries = len(customer_df[customer_df['index']>=constant.threshold_1])
    # the number of deliveries must satisfy capacity constraints
    num_deliveries = min(num_deliveries, num_convenient_deliveries)
    # dataframe of selected customers
    selected_customers = customer_df.head(int(num_deliveries))
    # list of indexes fo selected customers
    selected_indexes = selected_customers.index.tolist()
    # It is possible that some urgent clients are not served: those ones have to be postponed
    customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


def _postpone_client(line, this_day, served_clients=[], single_client=False):
    '''
    Postpone costumers whose last available day is the current one, but weren't included in selected customers.
    INPUTS:
        line: line of dataframe containig customers, it represent a single customer
        this_day: integer representing current day in simulation
        [served_clients]: list of indexes of customers that were selected to be served
        [single_client]: Boolean flag.
                         True: the customer I'm trying to postpone was among the selected customers
                         False: the customer I'm trying to postpone wasn't among the selected customers
    OUTPUT:
        line: line of dataframe containig customers, it represent a single customer (updated)
    '''
    if single_client:
        boolean = this_day == line.last_day
    else:
        boolean = this_day == line.last_day and line.name not in served_clients
    if boolean:
        global num_postponed
        # increment number of postponed costumers
        num_postponed += 1
        # postpone last available day
        line.last_day += 1
        # this customer has been postponed
        line.yet_postponed = True
    return line


def _check_capacity_constraints(selected_customers_df, kg_capacity, min_capacity):
    '''
    Check if the selected customers satisfy the aggegate capacity constraints.
    INPUTS:
        selected_customers_df: dataframe containg all information about selected customers.
        kg_capacity: total available capacity in kg.
        min_capacity: total available service time in min.
    OUTPUT:
        check: Boolean, if True the constraints are satisfied, if False they aren't.
    '''
    # Total kg of selected customers
    tot_kg = selected_customers_df['kg'].sum()
    # Total minutes of service time of selected customers
    tot_min = selected_customers_df['service_time'].sum()
    # check if kg-capacity constraint is respected
    kg_constraint = tot_kg <= kg_capacity
    # check if min-capacity constraint is respected
    min_constraint = tot_min <= min_capacity
    # check if both constraints are satisfied
    check = kg_constraint and min_constraint
    return check


def _remove_client(selected_costumers, costumers, this_day, selected_indexes):
    '''
    Remove last of selected customers and leave him among the pending ones.
    INPUTS:
        selected_costumers: dataframe constaining the selected customers
        costumers: dataframe of all pending customers
        this_day: integer representing current day in simulation
        selected_indexes: list of indexes of selected customers
    OUTPUTS:
        selected_indexes: list of indexes of selected customers (updated)
        selected_costumers: dataframe constaining the selected customers (updated)
        costumers: dataframe of all pending customers (updated)
    '''
    # last customers among the selected ones
    last_client = selected_costumers.tail(1)
    # check if I have to postpone the client
    last_client = last_client.apply(lambda line: _postpone_client(line, this_day, single_client=True), axis=1)
    # update costumer in costumers' dataframe
    costumers.at[selected_indexes[-1], 'last_day'] = last_client.iloc[0]['last_day']   
    costumers.at[selected_indexes[-1], 'yet_postponed'] = last_client.iloc[0]['yet_postponed']
    # update selected customers dataframe
    selected_costumers.drop(selected_costumers.tail(1).index, inplace=True)
    # remove index of the customer from the list of indexes
    del selected_indexes[-1]
    return selected_indexes, selected_costumers, costumers


def _index_selection(line, compatibility, day, all_cells, probabilities):
    '''
    Calculate index to associate to each customer for selection according to policy NP.
    Reference paper: https://www.sciencedirect.com/science/article/abs/pii/S0305054814000458
    INPUTS:
        line: line of dataframe of pending customers, it represents a costumer
        compatibility: list of dimension #cells whose elements are lists of convenient cells
        day: integer representing current day in simulation
        all_cells: set of all cells from which at least one of the pending customers comes from
        probabilities: dataframe column containig probabilities of a customer to belong to each cell
    OUTPUT:
        line: line of dataframe of pending customers, it represents a costumer (updated)
    '''
    # last available day to serve this costumer
    last_day = line.last_day
    # convert into a set the list of compatible cells
    compatibility = set(compatibility)
    # compute set of compatible cells that have no pending costumer coming from (not active compatible cells)
    not_present_cell = compatibility.difference(all_cells)
    
    # compute time distance
    availability = last_day-day
    # cardinality of not active compatible cells
    cardinality = len(not_present_cell)
    # Compute index
    M =constant.M
    gamma = constant.gamma
    if availability>0:
        if cardinality>0:
            line['index'] = 1/availability*(1+1/cardinality*(cardinality-probabilities[list(not_present_cell)].sum()))
        else:
            line['index'] = M/availability
    else:
        if line.yet_postponed == False:
            line['index'] = M
        else:
            line['index'] = M+gamma
    return line


def _index_selection_1(line, compatibility, day, all_cells, probabilities, compatibility_index, depot_distance):
    '''
    Calculate index to associate to each customer for selection according to policy NP_1.
    This is a modify of previous index that takes into account that costumers near to depot are much easier to serve than the
    ones that are very far from it. Moreover the index takes into accout the actual percentage savings and the expected ones,
    balancing them by travel time and service time of the customer.
    INPUTS:
        line: line of dataframe of pending customers, it represents a costumer
        compatibility: list of dimension #cells whose elements are lists of convenient cells
        day: integer representing current day in simulation
        all_cells: set of all cells from which at least one of the pending customers comes from
        probabilities: dataframe column containig probabilities of a customer to belong to each cell
        compatibility_index: numpy array of dimension #cells*#cells which contains the saving indexes
        depot_distance: numpy array of dimension #cells+1 containing all distances from depot to each cells (and the depot itself
                        in position 0)
    OUTPUT:
        line: line of dataframe of pending customers, it represents a costumer (updated)
    '''
    # average of new costumers
    N = constant.AVG_CUSTOMERS
    # last available day
    last_day = line.last_day
    # convert into a set the list of compatible cells
    compatibility = set(compatibility)
    # compute set of possible future compatible cells
    future_costumers = compatibility.difference(all_cells)
    # compute set of actual compatible cells
    present_costumers = compatibility.difference(future_costumers)
    # compute time distance
    T = last_day-day
    # cell of the considered costumer
    cell = line.cell
    # cumpute savings with present_costumers
    present_savings = compatibility_index[cell-1][list(present_costumers)].sum()
    # compute expected future savings
    exp_future_savings = (1-(1-probabilities[list(future_costumers)])**(T*N)) @ compatibility_index[cell-1][list(future_costumers)]
    # percentage time distance considering both travel and service time
    distance_perc = (depot_distance[cell]+line.service_time)/(max(depot_distance)+constant.BIG_TIME_MAX)
    # Compute the index
    if T>0:
        line['index'] = 1/T*((1-distance_perc)*present_savings-distance_perc*exp_future_savings)
    else:
        line['index'] = constant.M_1
    
    return line
    
