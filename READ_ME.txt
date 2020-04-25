Run code with command line arguments:
input_file_path -p policy -d days_simulation

WHERE:
- input_file_path is the file containing density distribution (i.e. grid.txt)
- policy is the desired policy to select which customers to serve
    - EP : early policy
    - DP : delayed policy
- days_simulation is the number of day you want to simulate

OBS:
selected_customers.txt contains the set of customers to serve in each day