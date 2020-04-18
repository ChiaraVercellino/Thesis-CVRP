import os
import subprocess

def main_VRPH(select_clients_df, depot, vehicles, capacity_kg):
    # write input file for VRPH
    file_path = 'inputVRPH.vrp'
    num_nodes = len(select_clients_df)+1
    with open(file_path, 'w') as fp:
        init = f'NAME: input\nDIMENSION: {num_nodes}\nCAPACITY: {capacity_kg}\nEDGE_WEIGHT_FORMAT: FUNCTION\nEDGE_WEIGHT_TYPE: EXACT_2D\nNODE_COORD_SECTION\n'
        fp.write(init)
        fp.write(f'1\t{depot[0]}\t{depot[1]}\n')
        select_clients_df['customer_label'] += 1
        select_clients_df.to_string(fp,columns=['customer_label','x','y'], header=False, index=False)
        fp.write('\nDEMAND_SECTION\n')
        fp.write(f'1\t 0\n')
        select_clients_df.to_string(fp,columns=['customer_label','kg'], header=False, index=False)
        endfile = '\nDEPOT_SECTION\n1\n-1\nEOF'
        fp.write(endfile)
    # Use this if you want to suppress output to stdout from the subprocess
    FNULL = open(os.devnull, 'w')
    args = f'vrp_ej.exe -f {file_path} -j 1 -t 1000 -m 0 -out Solution\outputVRPH.sol -v'  
    subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)