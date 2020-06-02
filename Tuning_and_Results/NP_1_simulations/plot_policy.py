import matplotlib.pyplot as plt
import numpy as np

# possible value for threshold
thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
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
NP_obj = [[480094, 481269, 481073, 482547, 483579, 484304, 485782, 486302, 486570, 486395, 486711], [485604, 486225, 487018, 488108, 488874, 489313, 490173, 490500, 490236, 491227, 491025],\
     [482738, 482506, 483631, 484069, 487340, 487519, 488283, 489531, 489651, 490140, 490220], [484168, 484964, 485750, 486314, 487009, 488920, 489603, 490478, 491089, 490928, 491558],\
          [487013, 487290, 489601, 491150, 491317, 492256, 492475, 492645, 492916, 494041, 494057], [487105, 487292, 489030, 488983, 490036, 490582, 490910, 490354, 491192, 491184, 491816],\
               [483794, 485793, 486153, 486985, 487874, 488618, 489028, 489165, 489580, 490189, 490384], [485122, 486232, 487125, 488556, 489241, 489282, 491694, 490860, 491087, 491281, 492101],\
                   [481858, 481820, 482942, 484447, 485049, 485748, 486308, 486350, 487100, 487015, 487770], [483789, 483775, 485394, 486038, 486869, 487669, 487705, 488664, 488644, 489222, 489550]]

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