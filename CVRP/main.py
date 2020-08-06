from ClarkWrigthSolver import ClarkWrightSolver
from TabuSearch import TabuSearch
import numpy as np



def main():
    np.random.seed(789)
    num_customer = 200
    distances = np.random.uniform(10,100,int(num_customer*(num_customer+1)/2))
    distance_matrix = np.zeros((num_customer+1,num_customer+1))
    distance_matrix[np.triu_indices(num_customer+1, 1)] = distances
    distance_matrix[np.tril_indices(num_customer+1, -1)] = distance_matrix.T[np.tril_indices(num_customer+1, -1)]
    service_time = np.random.randint(15,80,size=(num_customer,1))
    demand = np.random.randint(100,200,size=(num_customer,1))

    clark_wright_sol = ClarkWrightSolver(distance_matrix, service_time, demand)
    clark_wright_sol.solve()
    tabu_search = TabuSearch(clark_wright_sol)
    for i in range(100000):
        tabu_search.solve()
    tabu_search.final_optimization()
    tabu_search_sol = tabu_search.current_solution
    tabu_search_sol.print_solution()
    
if __name__ == '__main__':
    main()