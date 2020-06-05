import matplotlib.pyplot as plt
import numpy as np

# possible value for threshold
thresholds = [0.998, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995, 0.9997, 0.9999]
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
NP_obj = [[483025, 481909, 482046, 480993, 482046, 480709, 482058, 480704, 482161],\
     [487029, 486623, 487268, 487082, 486360, 486801, 487931, 487019, 487868],\
     [487814, 486065, 485059, 487383, 484781, 486609, 485697, 488381, 488856],\
          [488239, 489066, 488488, 488658, 488069, 488848, 488403, 489217, 491273],\
          [490724, 492163, 491542, 490201, 490448, 490150, 491005, 491053, 492792],\
               [488195, 487838, 487741, 487365, 487474, 487111, 488291, 487522, 487310],\
               [484841, 485816, 485915, 485455, 485340, 485156, 485317, 487077, 487902],\
                    [489703, 490212, 489466, 490240, 490591, 490833, 491536, 489991, 490834],\
                   [488865, 487572, 487771, 486296, 487700, 488845, 488639, 489184, 488401],\
                        [485307, 485461, 487052, 485839, 486313, 486648, 486728, 487061, 489031]]

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
    min_idx = [idx for idx, val in enumerate(NP_obj[seed]) if val == min_value]
    for index in min_idx:
        best_threshold[index] += 1
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