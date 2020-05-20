import matplotlib.pyplot as plt
import numpy as np

# possible value for threshold
thresholds = [0.996, 0.997, 0.9975, 0.998, 0.9983]
#, 0.9985, 0.999, 1.0
# seeds used in simulation
seeds = [1, 77, 3578, 33, 15, 64, 329, 66, 139, 10]
# number of simulations
num_sim = len(seeds)
# number of thresholds
num_thresholds = len(thresholds)

# cumulative objective function using EP for each seed
EP_obj = [517429, 497563, 475750, 482556, 461897, 447442, 461708, 489475, 451147, 462455]
# cumulative objective function using DP for each seed
DP_obj = [516303, 494319, 475146, 484368, 459823, 446923, 461698, 489369, 449242, 461182]
# cumulative objective function using NP for each seed with different threshold value
#, 513408, 513730, 513418
#, 490410, 491369, 493384
#, 471686, 472489, 474187
#, 480100, 479794, 482450
#, 456883, 456043, 459909
#, 445224, 443127, 443502
#, 458135, 456280, 460016
#, 486923, 487200, 487850
#, 446792, 445151, 447799
#, 459061, 459657, 460023
NP_obj = [[512909, 514526, 514898, 514993, 514445], [492424, 492278, 491543, 490509, 489456],\
     [472510, 473351,472629, 472147, 472340], [480012, 480391, 480429, 478786, 478763],\
          [458549, 458061, 457664, 456616, 457112], [445731, 444817, 445739, 444803, 445507],\
               [461033, 461000, 458270, 458044, 458109], [486993, 485869, 484644, 485977, 487056],\
                   [449247, 449308, 447841, 446485, 446810], [459735, 459375, 460364, 460410, 460744]]

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