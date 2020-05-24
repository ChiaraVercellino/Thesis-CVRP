import matplotlib.pyplot as plt
import numpy as np

# possible value for threshold
thresholds = [0.996, 0.997, 0.998, 0.999, 1.0]
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
NP_obj = [[519779, 523212, 485537, 517822, 499255], [521015, 505100, 501816, 520677, 478564],\
     [485130, 493721, 455426, 480778, 485120], [485120, 516037, 469858, 494154, 485684],\
          [463479, 502554, 517894, 516279, 465354], [449675, 466057, 505088, 483107, 448154],\
               [464829, 454464, 516372, 452206, 517754], [491993, 481349, 520970, 509414, 457015],\
                   [451684, 518712, 492007, 509297, 522922], [465636, 475186, 467220, 519169, 508877]]

best_threshold = [0]*num_thresholds
abs_diff = []

for seed in range(num_sim):
    EP_list = [EP_obj[seed]]*num_thresholds
    DP_list = [DP_obj[seed]]*num_thresholds
    #best_other_policy = min(EP_obj[seed], DP_obj[seed])
    best_other_policy = EP_obj[seed]
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
    plt.legend()
    path = "obj_fun_seed_"+str(seeds[seed])+".png"
    plt.savefig(path)

best_index = best_threshold.index(max(best_threshold))
print(best_threshold)
print(f'Best threshold: {thresholds[best_index]}')
print(f'Absolute differences: {abs_diff}')
print(f'Average absolute improvement: {np.mean(abs_diff)}')