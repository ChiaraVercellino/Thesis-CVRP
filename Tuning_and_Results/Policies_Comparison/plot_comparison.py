import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statistics import mean

# seeds used in simulation
seeds = [1, 77, 3578, 33, 15, 64, 329, 66, 139, 10]
# number of simulations
num_sim = len(seeds)
# number of thresholds

# cumulative objective function using EP for each seed
EP_obj = [486906, 491178, 489381, 492801, 495742, 490375, 486036, 493420, 492239, 491389]
# cumulative objective function using DP for each seed
DP_obj = [487395, 493362, 491733, 493610, 494879, 491976, 490072, 492229, 490692, 490183]
# cumulative objective function using NP_1 for each seed
NP1_obj = [479394, 479781, 480842, 481769, 484233, 484707, 478498, 482324, 478962, 480416]
# cumulative objective function using NP_1 for each seed
NP_obj = [482046, 486360, 484781, 488069, 490448, 487474, 485340, 490591, 487700, 486313]

# daily objective function using EP for each seed
EP_daily_obj = [5350, 5397, 5377, 5415, 5447, 5388, 5341, 5422, 5409, 5399]
# daily objective function using DP for each seed
DP_daily_obj = [5355, 5421, 5403, 5424, 5438, 5406, 5385, 5409, 5392, 5386]
# daily objective function using NP_1 for each seed
NP1_daily_obj = [5268, 5272, 5283, 5294, 5321, 5326, 5258, 5300, 5263, 5272]
# daily objective function using NP_1 for each seed
NP_daily_obj = [5297, 5344, 5327, 5363, 5389, 5356, 5333, 5391, 5359, 5344]

# daily objective function using EP for each seed
EP_vehicles = 50-np.array([5.549450549450549, 4.681318681318682, 4.967032967032967, 4.65934065934066, 4.3076923076923075,\
     4.8791208791208796, 5.131868131868132, 4.835164835164835, 4.802197802197802, 4.758241758241758])
# daily objective function using DP for each seed
DP_vehicles = 50-np.array([5.351648351648351, 4.406593406593407, 4.846153846153846, 4.593406593406593, 4.450549450549451,\
    4.824175824175824, 4.813186813186813, 4.857142857142857, 4.945054945054945, 4.8791208791208796])
# daily objective function using NP_1 for each seed
NP1_vehicles = 50-np.array([6.164835164835165, 5.791208791208791, 5.912087912087912, 5.626373626373627, 5.428571428571429,\
    5.450549450549451, 5.835164835164835, 5.714285714285714, 6.1098901098901095, 5.846153846153846])
# daily objective function using NP_1 for each seed
NP_vehicles = 50-np.array([5.626373626373627, 4.923076923076923, 5.164835164835165, 4.725274725274725, 4.538461538461538,\
    4.846153846153846, 4.868131868131868, 4.714285714285714, 4.923076923076923, 4.9010989010989015])

EP_vehicles = EP_vehicles.tolist()
DP_vehicles = DP_vehicles.tolist()
NP_vehicles = NP_vehicles.tolist()
NP1_vehicles = NP1_vehicles.tolist()

obj_list = EP_obj+DP_obj+NP1_obj+NP_obj
obj_daily_list = EP_daily_obj+DP_daily_obj+NP1_daily_obj+NP_daily_obj
vehicles_list = EP_vehicles+DP_vehicles+NP1_vehicles+NP_vehicles

counter_obj = 0
df_list = []
df_daily_list = []
df_vehicle_list = []
for obj in obj_list:
    counter_obj += 1
    if counter_obj <= 10:
        df_daily_list.append(['EP', seeds[counter_obj-1], obj_daily_list[counter_obj-1]])
        df_list.append(['EP', seeds[counter_obj-1], obj_list[counter_obj-1]])
        df_vehicle_list.append(['EP', seeds[counter_obj-1], vehicles_list[counter_obj-1]])
    elif counter_obj <= 20:
        df_daily_list.append(['DP', seeds[counter_obj-11], obj_daily_list[counter_obj-1]])
        df_list.append(['DP', seeds[counter_obj-11], obj_list[counter_obj-1]])
        df_vehicle_list.append(['DP', seeds[counter_obj-11], vehicles_list[counter_obj-1]])
    elif counter_obj <= 30:
        df_daily_list.append(['NP_1', seeds[counter_obj-21], obj_daily_list[counter_obj-1]])
        df_list.append(['NP_1', seeds[counter_obj-21], obj_list[counter_obj-1]])
        df_vehicle_list.append(['NP_1', seeds[counter_obj-21], vehicles_list[counter_obj-1]])
    else:
        df_daily_list.append(['NP', seeds[counter_obj-31], obj_daily_list[counter_obj-1]])
        df_list.append(['NP', seeds[counter_obj-31], obj_list[counter_obj-1]])
        df_vehicle_list.append(['NP', seeds[counter_obj-31], vehicles_list[counter_obj-1]])

df_obj = pd.DataFrame(df_list, columns=['policy', 'seed', 'obj_fun'])
df_daily_obj = pd.DataFrame(df_daily_list, columns=['policy', 'seed', 'obj_fun'])
df_vehicles = pd.DataFrame(df_vehicle_list, columns=['policy', 'seed', 'obj_fun'])

# absolute differences of the the new policies w.r.t the naive ones
abs_diff_NP = []
abs_diff_NP1 = []
# relative differences of the the new policies w.r.t the naive ones
rel_diff_NP = []
rel_diff_NP1 = []
# absolute daily differences of the the new policies w.r.t the naive ones
abs_diff_daily_NP = []
abs_diff_daily_NP1 = []
# relative daily differences of the the new policies w.r.t the naive ones
rel_diff_daily_NP = []
rel_diff_daily_NP1 = []

df_obj.pivot("seed", "policy", "obj_fun").plot(kind='bar')
plt.xlabel("Simulation's seed")
plt.ylabel("Objective function (min)")
plt.ylim(460000, 510000)
plt.tight_layout()
path = "obj_fun_histogram.png"
plt.savefig(path)

df_daily_obj.pivot("seed", "policy", "obj_fun").plot(kind='bar')
plt.xlabel("Simulation's seed")
plt.ylabel("Daily Average Cost (min)")
plt.ylim(5000, 5610)
plt.tight_layout()
path = "obj_fun_daily_histogram.png"
plt.savefig(path)

df_vehicles.pivot("seed", "policy", "obj_fun").plot(kind='bar')
plt.xlabel("Simulation's seed")
plt.ylabel("Average number of vehicles daily used")
plt.ylim(40, 48)
plt.tight_layout()
path = "vehicles_daily_histogram.png"
plt.savefig(path)

for seed in range(num_sim):

    best_naive_policy = min(EP_obj[seed], DP_obj[seed])
    abs_diff_NP.append(best_naive_policy-NP_obj[seed])
    abs_diff_NP1.append(best_naive_policy-NP1_obj[seed])
    rel_diff_NP.append((best_naive_policy-NP_obj[seed])/best_naive_policy*100)
    rel_diff_NP1.append((best_naive_policy-NP1_obj[seed])/best_naive_policy*100)

    best_daily_naive_policy = min(EP_daily_obj[seed], DP_daily_obj[seed])
    abs_diff_daily_NP.append(best_daily_naive_policy-NP_daily_obj[seed])
    abs_diff_daily_NP1.append(best_daily_naive_policy-NP1_daily_obj[seed])
    rel_diff_daily_NP.append((best_daily_naive_policy-NP_daily_obj[seed])/best_naive_policy*100)
    rel_diff_daily_NP1.append((best_daily_naive_policy-NP1_daily_obj[seed])/best_naive_policy*100)

print(f'Average absolute difference NP policy: {mean(abs_diff_NP)}')
print(f'Average absolute differences NP_1 policy: {mean(abs_diff_NP1)}')
print(f'Average relative differences NP policy: {mean(rel_diff_NP)} %')
print(f'Average relative differences NP_1 policy: {mean(rel_diff_NP1)} %\n')

print(f'Average daily absolute difference NP policy: {mean(abs_diff_daily_NP)}')
print(f'Average daily absolute differences NP_1 policy: {mean(abs_diff_daily_NP1)}')
print(f'Average daily relative differences NP policy: {mean(rel_diff_daily_NP)} %')
print(f'Average daily relative differences NP_1 policy: {mean(rel_diff_daily_NP1)} %')

#print(min(rel_diff_NP1))
#print(max(rel_diff_NP1))