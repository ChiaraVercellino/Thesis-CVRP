# select which customers to serve:
# MUST select all customer that are at the end of their available days
# SHOULD use a function that takes as input different mode


def select_customers(day, m3_capacity, kg_capacity, policy):
    # maybe later add argument available_time
    # calculate average demand in m^3
    avg_m3 = day.customer_df['m3'].mean()
    # calculate average demand in kg
    avg_kg = day.customer_df['kg'].mean()
    # approximate the maximum number of deliveries will be allowed with the available capacities
    num_deliveries = min(m3_capacity//avg_m3, kg_capacity//avg_kg)

    # apply the desired policy
    if policy == "EP":
        selected_customers, selected_idx, new_customer_df = _early_policy(day.customer_df, day.current_day,
                                                                          num_deliveries)
    elif policy == "DP":
        selected_customers, selected_idx, new_customer_df = _delayed_policy(day.customer_df, day.current_day,
                                                                            num_deliveries)
    else:
        print('Policy not yet implemented')

    # check if I've respected total capacities
    constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, m3_capacity)
    # iterate until the constraint is satisfied
    while not constraints_respected:
        # If capacity is not respected I have to eliminate some customer
        selected_idx, selected_customers, new_customer_df = _remove_client(selected_customers, new_customer_df,
                                                                           day.current_day, selected_idx)
        constraints_respected = _check_capacity_constraints(selected_customers, kg_capacity, m3_capacity)
    # add labels corresponding to nodes in graph
    selected_customers['customer_label'] = range(1, len(selected_customers)+1)
    # update data frame
    day.customer_df = new_customer_df
    return selected_customers, selected_idx, day


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


# postpone client which we should have served this day, but we couldn't
def _postpone_client(line, this_day, served_clients=[], single_client=False):
    if single_client:
        boolean = this_day == line.last_day
    else:
        boolean = this_day == line.last_day and line.name not in served_clients
    if boolean:
        line.last_day += 1
        line.yet_postponed = True
    return line


# check if the selected customers are allowed by aggregate capacities
def _check_capacity_constraints(selected_customers_df, kg_capacity, m3_capacity):
    tot_kg = selected_customers_df['kg'].sum()
    tot_m3 = selected_customers_df['m3'].sum()
    kg_constraint = tot_kg <= kg_capacity
    m3_constraint = tot_m3 <= m3_capacity
    return kg_constraint and m3_constraint


# remove additional clients from selected one and put it again in the queue
def _remove_client(selected_costumers, costumers, this_day, selected_indexes):
    last_client = selected_costumers.tail(1)
    # check if I have to postpone the client
    last_client = last_client.apply(lambda line: _postpone_client(line, this_day, single_client=True), axis=1)
    costumers = costumers.append(last_client)
    selected_costumers.drop(selected_costumers.tail(1).index, inplace=True)
    del selected_indexes[-1]
    return selected_indexes, selected_costumers, costumers

