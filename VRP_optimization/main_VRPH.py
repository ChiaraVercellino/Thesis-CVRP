import os
import subprocess

def main_VRPH(select_clients_df, depot, vehicles, capacity_kg):
    # write input file for VRPH
    file_path = './Solution/inputVRPH.vrp'
    num_nodes = len(select_clients_df)+1
    with open(file_path, 'w') as fp:
        init = f'NAME: input\nDIMENSION: {num_nodes}\nCAPACITY: 5\nEDGE_WEIGHT_FORMAT: FUNCTION\nEDGE_WEIGHT_TYPE: EXACT_2D\nNODE_COORD_SECTION\n'
        #init = f'NAME: input\nDIMENSION: {num_nodes}\nCAPACITY: {capacity_kg}\nEDGE_WEIGHT_FORMAT: FUNCTION\nEDGE_WEIGHT_TYPE: EXACT_2D\nNODE_COORD_SECTION\n'
        fp.write(init)
        fp.write(f'1\t{depot[0]}\t{depot[1]}\n')
        select_clients_df['customer_label'] += 1
        select_clients_df.to_string(fp,columns=['customer_label','x','y'], header=False, index=False)
        fp.write('\nDEMAND_SECTION\n')
        fp.write(f'1\t 0\n')
        select_clients_df['unary_demand'] = [1]*(num_nodes-1)
        select_clients_df.to_string(fp,columns=['customer_label','unary_demand'], header=False, index=False)
        endfile = '\nDEPOT_SECTION\n1\n-1\nEOF'
        fp.write(endfile)
    # Use this if you want to suppress output to stdout from the subprocess
    FNULL = open(os.devnull, 'w')
    args = f'./VRP_optimization/vrp_rtr.exe -f {file_path} -v'
    with open('./Solution/outputVRPH.sol', 'w') as f:
        subprocess.call(args, stdout=f, stderr=FNULL, shell=False)