from ClarkWrigthSolver import ClarkWrightSolver
from TabuSearch import TabuSearch
import numpy as np
import time


def main():
    np.random.seed(890)
    num_customer = 195
    distances = np.random.uniform(10,100,int(num_customer*(num_customer+1)/2))
    distance_matrix = np.zeros((num_customer+1,num_customer+1))
    distance_matrix[np.triu_indices(num_customer+1, 1)] = distances
    distance_matrix[np.tril_indices(num_customer+1, -1)] = distance_matrix.T[np.tril_indices(num_customer+1, -1)]
    service_time = np.random.randint(15,80,size=(num_customer,1))
    demand = np.random.randint(100,200,size=(num_customer,1))
    
    
    tabu_divisor = [2, 3, 4, 5, 6]
    perc = [0.1, 0.15, 0.20, 0.25, 0.30, 0.35]
    num_perm = [10, 15, 20, 25, 30, 35, 40]
    initialize_perc = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    
    max_time = 30

    for init_perc in initialize_perc:
        clark_wright_sol = ClarkWrightSolver(distance_matrix, service_time, demand, init_perc)
        clark_wright_sol.solve()
        for tabu_div in tabu_divisor:
            for p in perc:
                for num_p in num_perm:                    
                    start = time.time()
                    tabu_search = TabuSearch(clark_wright_sol, max_time, tabu_div, p, num_p)
                    elapsed_time = 0
                    i=0
                    while elapsed_time <= max_time:
                        i+=1
                        tabu_search.solve(elapsed_time)
                        elapsed_time = time.time()-start
                    tabu_search.final_optimization()
                    tabu_search_sol = tabu_search.current_solution
                    #tabu_search_sol.print_solution()
                    print('Iterations: {}'.format(i))
                    print('Percentage Initializer {}, Divisor Tabu {}, Percentage 2 swap {}, Num Perms {}'. format(init_perc, tabu_div, p, num_p))
                    print('Final cost {}\n'.format(tabu_search_sol.total_cost-sum(service_time)[0]))
    

if __name__ == '__main__':
    main()