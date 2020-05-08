import constant

num_postponed = 0

def select_customers(day, h_capacity, kg_capacity, policy, compatibility, probabilities):
    # percentage for set_up times
    perc = constant.PERCENTAGE
    # calculate average demand and standard deviation (kg)
    avg_kg = day.customer_df['kg'].mean()
    std_kg = day.customer_df['kg'].std()
    # calculate average set_up_times and standard deviation (min)
    avg_set_up = day.customer_df['set_up_time'].mean()
    std_set_up = day.customer_df['set_up_time'].std()
    # approximate the maximum number of deliveries will be allowed with the available capacities
    num_deliveries = min(perc*h_capacity//avg_set_up, kg_capacity//avg_kg)
    # apply the desired policy
    if policy == "EP":
        selected_customers, selected_idx, new_customer_df = _early_policy(day.customer_df, day.current_day,
                                                                          num_deliveries)
    elif policy == "DP":
        selected_customers, selected_idx, new_customer_df = _delayed_policy(day.customer_df, day.current_day,
                                                                            num_deliveries)
    else:
        selected_customers, selected_idx, new_customer_df = _neighbourhood_policy(day.customer_df, day.current_day,
                                                                            num_deliveries, compatibility, probabilities)

    # check if I've respected total capacities
    constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, perc*h_capacity)
    # iterate until the constraint is satisfied
    while not constraints_respected:
        # If capacity is not respected I have to eliminate some customer
        selected_idx, selected_customers, new_customer_df = _remove_client(selected_customers, new_customer_df,
                                                                           day.current_day, selected_idx)
        constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, perc*h_capacity)
        num_deliveries -= 1
    # add labels corresponding to nodes in graph
    selected_customers['customer_label'] = range(1, len(selected_customers)+1)
    # update data frame
    day.customer_df = new_customer_df
    day.selected_customers = selected_customers
    day.selected_indexes = selected_idx
    return day, num_postponed


def remove_client_VRP(day):
    day.selected_indexes, day.selected_customers, day.customer_df = _remove_client(day.selected_customers, day.customer_df,\
     day.current_day, day.selected_indexes)
    return day


# serve all customers as soon as demand happens
def _early_policy(customer_df, this_day, num_deliveries):
    # serve all possible customers, order them by urgency
    customer_df = customer_df.sort_values(by=['last_day', 'yet_postponed'], axis=0, ascending=[True, False],
                                          ignore_index=False)
    selected_customers = customer_df.head(int(num_deliveries))
    selected_indexes = selected_customers.index.tolist()
    # It is possible that some urgent clients are not served: for those ones I increment last_day by one
    customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


# serve only customers whose last available day is the current one
def _delayed_policy(customer_df, this_day, num_deliveries):
    # sort all customer to try and serve the ones whose orders have yet been postponed
    customer_df = customer_df.sort_values(by=['yet_postponed'], axis=0, ascending=[False],
                                          ignore_index=False)
    # select all customers whose last available day is the current one
    selected_indexes = customer_df.index[customer_df['last_day'] == this_day].tolist()
    list_length = len(selected_indexes)
    selected_customers = customer_df[customer_df['last_day'] == this_day].head(int(min(list_length, num_deliveries)))
    # check if all these customers can be served
    if list_length > num_deliveries:
        selected_indexes = selected_indexes[:int(num_deliveries)]
        # It is possible that some urgent clients are not served: for those ones I increment last_day by one
        customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df


# serve customers according to probability of future demands of neighbours
def _neighbourhood_policy(customer_df, this_day, num_deliveries, compatibility, probabilities):
    all_cells = set(customer_df['cell'])
    customer_df = customer_df.apply(lambda line: _index_selection(line, compatibility[line.cell], this_day, all_cells, probabilities), axis=1)
    customer_df = customer_df.sort_values(by=['index'], axis=0, ascending=[False], ignore_index=False)
    selected_customers = customer_df.head(int(num_deliveries))
    selected_indexes = selected_customers.index.tolist()
    # It is possible that some urgent clients are not served: for those ones I increment last_day by one
    customer_df = customer_df.apply(lambda line: _postpone_client(line, this_day, selected_indexes), axis=1)
    return selected_customers, selected_indexes, customer_df

# postpone client which we should have served this day, but we couldn't
def _postpone_client(line, this_day, served_clients=[], single_client=False):
    if single_client:
        boolean = this_day == line.last_day
    else:
        boolean = this_day == line.last_day and line.name not in served_clients
    if boolean:
        global num_postponed
        num_postponed += 1
        line.last_day += 1
        line.yet_postponed = True
    return line


# check if the selected customers are allowed by aggregate capacities
def _check_capacity_constraints(selected_customers_df, kg_capacity, h_capacity):
    tot_kg = selected_customers_df['kg'].sum()
    tot_h = selected_customers_df['set_up_time'].sum()
    kg_constraint = tot_kg <= kg_capacity
    h_constraint = tot_h <= h_capacity
    return kg_constraint and h_constraint


# remove additional clients from selected one and put it again in the queue
def _remove_client(selected_costumers, costumers, this_day, selected_indexes):
    last_client = selected_costumers.tail(1)
    # check if I have to postpone the client
    last_client = last_client.apply(lambda line: _postpone_client(line, this_day, single_client=True), axis=1)
    # update costumer in costumers' dataframe
    costumers.at[selected_indexes[-1], 'last_day'] = last_client.iloc[0]['last_day']   
    costumers.at[selected_indexes[-1], 'yet_postponed'] = last_client.iloc[0]['yet_postponed']
    # update selected customers
    selected_costumers.drop(selected_costumers.tail(1).index, inplace=True)
    del selected_indexes[-1]
    return selected_indexes, selected_costumers, costumers


# calculate index to associate at each customer for selection
def _index_selection(line, compatibility, day, all_cells, probabilities):
    last_day = line.last_day
    # convert into a set the compatible cell of the client
    compatibility = set(compatibility)
    # compute set of compatible cells that are not active this day
    not_present_cell = compatibility.difference(all_cells)
    # compute time distance
    availability = last_day-day
    # cardinality of compatible cells not yet active
    cardinality = len(not_present_cell)
    M = 2
    gamma = 1
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
    
