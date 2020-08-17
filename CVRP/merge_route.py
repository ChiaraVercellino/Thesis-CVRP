from Route import Route

def merge_routes(route1, route2, customer1, customer2, savings):
  
    new_route = Route()

    new_route.load_kg = route1.load_kg+route2.load_kg
    # minutes' load of vehicle
    new_route.load_min = route1.load_min+route2.load_min - savings
    # customers' load of vehicle
    new_route.load_cust = route1.load_cust+route2.load_cust

    feasible_route = new_route.check_constraints()

    if feasible_route:
        new_route_list = []
        idx_cus1 = route1.route.index(customer1+1)
        idx_cus2 = route1.route.index(customer2+1)

        if route1.route[idx_cus1-1]==0:
            if route2.route[idx_cus2-1]==0:
                temp = route1.route[idx_cus1 :]
                new_route_list = route1.route[idx_cus1 :][::-1] + route2.route[idx_cus2 :]
            elif route2.route[idx_cus2+1]==0:
                new_route_list = route2.route[: idx_cus2+1] + route1.route[idx_cus1 :]
        elif route1.route[idx_cus1+1]==0:
            if route2.route[idx_cus2-1]==0:
                new_route_list = route1.route[: idx_cus1+1] + route2.route[idx_cus2 :]
            elif route2.route[idx_cus2+1]==0:
                new_route_list = route2.route[: idx_cus2+1] + route1.route[: idx_cus1+1][::-1]

        new_route.route = new_route_list

        if not(new_route_list):
            feasible_route = False

    return feasible_route, new_route

    
    