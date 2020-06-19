''' In this file we set all test parameters for simulation, they can be changed directly here without further modifications
in other part of the code'''

# ------------------------------------------------ PARAMETERS FOR ALL POLICIES --------------------------------------------------------------------


# number of days not to consider in objective function
NUM_DAYS = 10
# seed for simulations
SEED = 57
# time limit for CVRP solver (never reached)
TIME_LIMIT = 10

# ------------------------------------------------ parameters for vehicles--------------------------------------------------------------------

# number of available vehicles for CVRP
NUM_VEHICLES = 50
# capacity of a single vehicle in terms of kg
CAPACITY = 1000
# available minutes for a single vehicle (travel time + service time)
TIME = 480
# maximum number of customer served by a single vehicle
CUSTOMER_CAPACITY = 5
# percentage of capacity used for customers' selection
PERCENTAGE = 0.67

# ------------------------------------------------ parameters for customer simulation--------------------------------------------------------------------

# average number of new customers arriving in each day
AVG_CUSTOMERS = 195
# probability for a customer of having a demand that requires a big amount of service time and kg capacity
PROB_BIG = 0.5
# lower bound for small demand in kg
SMALL_KG_MIN = 5
# lower bound for small demand in service time (min)
SMALL_TIME_MIN = 15
# upper bound for small demand in kg
SMALL_KG_MAX = 10
# upper bound for small demand in service time (min)
SMALL_TIME_MAX = 45
# lower bound for increment, w.r.t. small demand lower bound, of big demand in kg
BIG_KG_MIN = 195
# lower bound for increment, w.r.t. small demand lower bound, of big demand in service time (min)
BIG_TIME_MIN = 45
# upper bound for increment, w.r.t. small demand upper bound, of big demand in kg
BIG_KG_MAX = 490
# upper bound for increment, w.r.t. small demand upper bound, of big demand in service time (min)
BIG_TIME_MAX = 135

# ------------------------------------------------ TUNED PARAMETERS POLICY NP--------------------------------------------------------------------

# Threshold for selecting which customers to serve according to index generated by policy NP
threshold = 0.9993
# Threashold to select which cells in the neighbourhood of a specific cell give percentage savings higher than rho
rho = 0.45
# Constant index assigned to clients that are at their last available day to be served
M = 5
# Constant value to add to M for clients that are at their last available day and are yet be postponed
gamma = 1

# ------------------------------------------------ TUNED PARAMETERS POLICY NP_1--------------------------------------------------------------------

# Threashold to select which cells in the neighbourhood of a specific cell give percentage savings higher than rho
#rho = 0.45
# Threshold for selecting which customers to serve according to index generated by policy NP_1
threshold_1 = -0.12


