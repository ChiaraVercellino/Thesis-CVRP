import matplotlib.pyplot as plt
import numpy as np

# BEST VALUE: 0.7, 0.9

# possible value for threshold
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
# seeds used in simulation
seeds = [1, 77, 3578, 33, 15, 64, 329, 66, 139, 10]
# number of simulations
num_sim = len(seeds)
# number of thresholds
num_thresholds = len(thresholds)

# cumulative objective function using EP for each seed
EP_obj = [523237, 502685, 480884, 487973, 466868, 452354, 467255, 495075, 455698, 468076]
# cumulative objective function using DP for each seed
DP_obj = [521991, 499340, 480024, 489444, 465454, 451772, 466987, 494589, 454116, 466889]
# cumulative objective function using NP for each seed with different threshold value
NP_obj = [[518696, 522501, 518553, 522798, 488262, 499255, 518808, 525066], [499995, 520045, 497145, 523418, 505051, 478564, 498472, 521496],\
     [481145, 486895, 478532, 486040, 492898, 485120, 480162, 487264], [487868, 520673, 486941, 516643, 471695, 485684, 488100, 521116],\
          [465760, 504215, 463898, 502880, 519697, 465354, 465354, 503615], [451545, 467828, 449988, 466379, 508492, 448154, 448154, 463302],\
               [467709, 457349, 465641, 455061, 516627, 517754, 467135, 456376], [495701, 484400, 493278, 481915, 518145, 457015, 493903, 482323],\
                   [455801, 522669, 451979, 519615, 494529, 522922, 450203, 523662], [466898, 479969, 466219, 476887, 470753, 508877, 466347, 476713]]

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