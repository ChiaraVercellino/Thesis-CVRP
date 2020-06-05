#CVRP with stochastic customers over time

The problem is solved in 2 stages:
- Selection of custumers to serve in the current day
- CVRP solved with ORtools library

The *objective function* to minimize is composed by:
- the total travel cost (expressed in terms of minutes to travel)
- the number of vehicles needed to serve customers

The *constraints* concern:
- Total load of each vehicle
- Number of customer for each vehicle
- Total working time of each vehicle (travel time + service time)

Run code with command line arguments:
main.py input_file_path -p policy -d days_simulation

WHERE:
- input_file_path is the file containing density distribution (i.e. grid.txt)
- policy is the desired policy to select which customers to serve
    - EP : early policy
    - DP : delayed policy
    - NP : neighbourhood policy (version 1)
    - NP_1 : neighbourhood policy (version 2)
- days_simulation is the number of day you want to simulate

