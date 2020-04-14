class Vehicle:
    # vehicle counter
    total_vehicles = 0

    def __init__(self, length, width, height, capacity, customer_route=[]):
        Vehicle.total_vehicles += 1
        self.vehicle_id = Vehicle.total_vehicles
        self.volume = length*width*height
        self.capacity = capacity
        self.customer_route = customer_route


# ------------------------------------------- OTHER METHODS ----------------------------------------------------------

# calculate aggregate capacities
def _aggregate_capacities(l_small, w_small, h_small, l_big, w_big, h_big, c_small, c_big, n_small, n_big):
    tot_volume = l_small*w_small*h_small*n_small+l_big*w_big*h_big*n_big
    tot_capacity = c_small*n_small+c_big*n_big
    return tot_capacity, tot_volume

# inizialize vehicles
def inizialize_vehicles(length_small, width_small, height_small, capacity_small, small_vehicles,
                        length_big, width_big, height_big, capacity_big, big_vehicles):
    # list of available vehicles
    vehicles = []
    # Instantiate available vehicles
    for _ in range(small_vehicles):
        vehicles.append(Vehicle(length_small, width_small, height_small, capacity_small))
    for _ in range(big_vehicles):
        vehicles.append(Vehicle(length_big, width_big, height_big, capacity_big))
    # Calculate aggregate values
    kg_capacity, m3_capacity = _aggregate_capacities(length_small, width_small, height_small, length_big,
                                                     width_big, height_big, capacity_small, capacity_big,
                                                     small_vehicles, big_vehicles)
    return kg_capacity, m3_capacity
