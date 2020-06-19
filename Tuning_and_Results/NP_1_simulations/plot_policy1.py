import matplotlib.pyplot as plt
import numpy as np

# possible value for threshold
thresholds = [-0.12, -0.11, -0.1, -0.09, -0.08, -0.07, -0.05]
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
NP_obj = [[479394, 479013, 478501, 478173, 478166, 477652, 478295],\
     [479781, 479934, 481324, 480758, 480931, 480493, 481742],\
     [480842, 480842, 480808, 480808, 481001, 481132, 481132],\
          [481769, 482016, 482108, 482111, 482022, 482069, 482158],\
          [484233, 484381, 484381, 484381, 484260, 484429, 484373],\
               [484707, 484707, 484707, 483943, 483943, 483915, 483915],\
               [478498, 478498, 479420, 479420, 479420, 479985, 480192],\
                    [482324, 484091, 482681, 482681, 483704, 483704, 482977],\
                   [478962, 478626, 478774, 478637, 478834, 478913, 478994],\
                        [480416, 479854, 479815, 479769, 479381, 479369, 479416]]

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