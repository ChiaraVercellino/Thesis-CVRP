import matplotlib.pyplot as plt
import numpy as np

# BEST THRESHOLD = 0.93

# possible value for threshold
thresholds = [0.993, 0.995, 0.997, 0.999]
# seeds used in simulation
seeds = [1, 77, 3578, 33, 15, 64, 329, 66, 139, 10]
# number of simulations
num_sim = len(seeds)
# number of thresholds
num_thresholds = len(thresholds)

# cumulative objective function using EP for each seed
EP_obj = [486906, 491178, 489381, 492801, 495742, 490375, 486036, 493420, 492239, 491389]
# cumulative objective function using DP for each seed
DP_obj = [487395, 493362, 491733, 493610, 494879, 491976, 490072, 492229, 490692, 490183]
# cumulative objective function using NP for each seed with different threshold value
NP_obj = [[485136, 485260, 484014, 481909], [490148, 489743, 487896, 486623],\
     [489085, 488900, 488388, 486065], [489971, 490695, 488961, 489066],\
          [492580, 493102, 492915, 492163], [489254, 490082, 489577, 487838],\
               [486843, 486680, 486039, 485816], [491544, 491709, 490698, 490212],\
                   [491086, 490474, 490004, 487572], [485875, 486361, 485884, 485461]]

best_threshold = [0]*num_thresholds
worse_result = [0]*num_thresholds
abs_diff = []

for seed in range(num_sim):
    EP_list = [EP_obj[seed]]*num_thresholds
    DP_list = [DP_obj[seed]]*num_thresholds
    best_other_policy = min(EP_obj[seed], DP_obj[seed])
    #best_other_policy = EP_obj[seed]
    plt.figure()
    plt.xlabel("Threshold")
    plt.ylabel("Objective function")
    plt.title(f'Objective function for seed {seeds[seed]}')
    plt.plot(thresholds, NP_obj[seed], label = 'Policy: NP')
    plt.plot(thresholds, EP_list , label = 'Policy: EP')
    plt.plot(thresholds, DP_list, label = 'Policy: DP')
    min_value = min(NP_obj[seed])
    min_index = NP_obj[seed].index(min_value)
    best_threshold[min_index] += 1
    abs_diff.append(best_other_policy-min_value)
    worse_idx = [idx for idx, val in enumerate(NP_obj[seed]) if val >= best_other_policy]
    for index in worse_idx:
        worse_result[index] += 1
    plt.legend()
    path = "obj_fun_seed_"+str(seeds[seed])+".png"
    plt.savefig(path)

best_index = best_threshold.index(max(best_threshold))
print('Number of times each threshold brings to best result')
print(best_threshold)
print('Number of times each threshold brings a result is worse than other policies')
print(worse_result)
print(f'Best threshold: {thresholds[best_index]}')
print(f'Absolute differences: {abs_diff}')
print(f'Average absolute improvement: {np.mean(abs_diff)}')