Run code with command line arguments:
input_file_path  output_file_path  policy

WHERE:
- input_file_path is the file containing density distribution (i.e. grid.txt)
- output_file_path is the file containing the dataset of customer in each day (i.e. clients_data.txt)
- policy is the desired policy to select which customers to serve
    - EP : early policy
    - DP : delayed policy

OBS:
selected_customers.txt contains the set of customers to serve in each day