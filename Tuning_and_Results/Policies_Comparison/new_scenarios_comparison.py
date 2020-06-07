import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statistics import mean
import pylab

# seeds used in simulation
seeds = [7, 89, 65, 982, 5738, 123, 456, 99, 343, 731, 5, 902, 582, 111, 22, 73, 88, 105, 44, 970, 45, 9, 803, 112, 44]
# number of simulations
num_sim = len(seeds)
# number of thresholds

EP_obj = []
EP_daily_obj = []
EP_vehicles = []
with open('EP_results.txt', 'r') as fpEP:
    lines = fpEP.readlines() 
    for line in lines:
        if line.startswith('Total objective function'):
            EP_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of travel cost'):
            EP_daily_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of empty vehicles'):
            EP_vehicles.append(50-float(line.split(': ')[1]))

DP_obj = []
DP_daily_obj = []
DP_vehicles = []
with open('DP_results.txt', 'r') as fpDP:
    lines = fpDP.readlines() 
    for line in lines:
        if line.startswith('Total objective function'):
            DP_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of travel cost'):
            DP_daily_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of empty vehicles'):
            DP_vehicles.append(50-float(line.split(': ')[1]))

NP_obj = []
NP_daily_obj = []
NP_vehicles = []
with open('NP_results.txt', 'r') as fpNP:
    lines = fpNP.readlines() 
    for line in lines:
        if line.startswith('Total objective function'):
            NP_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of travel cost'):
            NP_daily_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of empty vehicles'):
            NP_vehicles.append(50-float(line.split(': ')[1]))

NP1_obj = []
NP1_daily_obj = []
NP1_vehicles = []
with open('NP1_results.txt', 'r') as fpNP1:
    lines = fpNP1.readlines() 
    for line in lines:
        if line.startswith('Total objective function'):
            NP1_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of travel cost'):
            NP1_daily_obj.append(int(line.split(': ')[1]))
        elif line.startswith('Average of empty vehicles'):
            NP1_vehicles.append(50-float(line.split(': ')[1]))

obj_list = EP_obj+DP_obj+NP1_obj+NP_obj
obj_daily_list = EP_daily_obj+DP_daily_obj+NP1_daily_obj+NP_daily_obj
vehicles_list = EP_vehicles+DP_vehicles+NP1_vehicles+NP_vehicles

counter_obj = 0
df_list = []
df_daily_list = []
df_vehicle_list = []
for obj in obj_list:
    counter_obj += 1
    if counter_obj <= num_sim:
        df_daily_list.append(['EP', seeds[counter_obj-1], obj_daily_list[counter_obj-1]])
        df_list.append(['EP', seeds[counter_obj-1], obj_list[counter_obj-1]])
        df_vehicle_list.append(['EP', seeds[counter_obj-1], vehicles_list[counter_obj-1]])
    elif counter_obj <= 2*num_sim:
        df_daily_list.append(['DP', seeds[counter_obj-num_sim-1], obj_daily_list[counter_obj-1]])
        df_list.append(['DP', seeds[counter_obj-num_sim-1], obj_list[counter_obj-1]])
        df_vehicle_list.append(['DP', seeds[counter_obj-num_sim-1], vehicles_list[counter_obj-1]])
    elif counter_obj <= 3*num_sim:
        df_daily_list.append(['NP_1', seeds[counter_obj-2*num_sim-1], obj_daily_list[counter_obj-1]])
        df_list.append(['NP_1', seeds[counter_obj-2*num_sim-1], obj_list[counter_obj-1]])
        df_vehicle_list.append(['NP_1', seeds[counter_obj-2*num_sim-1], vehicles_list[counter_obj-1]])
    else:
        df_daily_list.append(['NP', seeds[counter_obj-3*num_sim-1], obj_daily_list[counter_obj-1]])
        df_list.append(['NP', seeds[counter_obj-3*num_sim-1], obj_list[counter_obj-1]])
        df_vehicle_list.append(['NP', seeds[counter_obj-3*num_sim-1], vehicles_list[counter_obj-1]])

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

params = {'legend.fontsize': 14,
         'legend.title_fontsize': 14}
pylab.rcParams.update(params)

df_obj.pivot_table(index='seed', columns='policy', values='obj_fun').plot(kind='bar', figsize=(16,7))
plt.xlabel("Simulation's seed", size=15)
plt.ylabel("Objective function (min)", size=15)
plt.ylim(460000, 510000)
plt.tight_layout()
path = "obj_fun_histogram_NS.png"
plt.savefig(path)

df_daily_obj.pivot_table(index='seed', columns='policy', values='obj_fun').plot(kind='bar', figsize=(16,7))
plt.xlabel("Simulation's seed", size=15)
plt.ylabel("Daily Average Cost (min)", size=15)
plt.ylim(5000, 5610)
plt.tight_layout()
path = "obj_fun_daily_histogram_NS.png"
plt.savefig(path)

df_vehicles.pivot_table(index='seed', columns='policy', values='obj_fun').plot(kind='bar', figsize=(16,7))
plt.xlabel("Simulation's seed", size=15)
plt.ylabel("Average number of vehicles daily used", size=15)
plt.ylim(40, 48)
plt.tight_layout()
path = "vehicles_daily_histogram_NS.png"
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