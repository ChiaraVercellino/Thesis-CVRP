# Multi-Period CVRP with stochastic customers over time

We are addressing to a Multi-Period Capacitated Vehicles Routing Problem (CVRP) with customers' arrivals that are Stochastic over time.

The customers are simulated on a rectangular region 205x215 km<sup>2</sup>, the region is divided into cells of dimensions 5×5 km<sup>2</sup>, the probability of customers belonging to a cell and the cells' coordinates are defined by input file `.Data\grid.txt`. Each day we simulate the number of new customers using a Uniform distribution, whose parameters can be modified in file `constant.py`. Then their positions on the region of interest is performed by a Multinomial distribution, to assign the new customers to a certain cell; finally a Uniform distribution on both dimensions of each cell specify the coordinates of each new customer.

Each day we select the custumers to serve, among the pending ones, and than we solve a CVRP with deterministic information about customers' positions, demands (kg) and service times (min).

So, the proposed algorithms solves the problem in 2 stages:
- Selection of custumers to serve in the current day, in this step we propose four policies for customers' selection
- Solution of deterministic CVRP, in this step both the Google OR-Tools solver and our CW-TS solver could be used

The *objective function* to minimize is composed by:
- the total travel cost (expressed in terms of minutes to travel)
- the number of vehicles needed to serve customers

The *constraints* concern:
- Total load of each vehicle
- Number of customers for each vehicle
- Total working time of each vehicle (travel time + service time)

A more detailed description of the problem can be found in my dissertation: https://github.com/ChiaraVercellino/Thesis-CVRP/blob/master/Images_PDF/Thesis_CVRP.pdf .

## Getting Started

To get you a copy of the project:

```
git clone https://github.com/ChiaraVercellino/Thesis-CVRP.git
```

To run on your local machine:
```
python main.py input_file_path -p policy -d days_simulation -s solver
```

WHERE:
- `input_file_path` is the file containing density distribution
- `policy` is the desired policy to select which customers to serve
    - EP : early policy
    - DP : delayed policy
    - NP : neighbourhood policy (version 1)
    - NP_1 : neighbourhood policy (version 2)
- `days_simulation` is the number of day you want to simulate
- `solver` is the solver that can be used to solve the daily CVRP
    - ortools: use Google OR-Tools solver
    - cwts: use CW-TS solver

### Prerequisites and Installing

To execute the simulator you need Python. Then you have to create a virtual environment `my_env` in your workspace:
```
python -m venv my_env
```
Then you have to activate the virtual environment:
```
.my_env\scripts\activate
```
Finally, you have to install all the packages, contained in the file `requirements.txt`, in your virtual environment:
```
pip install -r C:\WorkSpace\requirements.txt
```
Among all packages in `requirements.txt`, only the `ortools` library needs more care for the installation: it cannot be installed correctly using PyCharm editor, it's suggested to use VSCode with Python extensions and C++ toolset.

For issues about `ortools` installation:
https://developers.google.com/optimization/install


## Running the tests

To run the simulation with the test parameters defined in `constant.py` and the distribution of customers according to `grid.txt`:
- With policy EP and Google OR-Tools solver
```
python main.py grid.txt -p EP -d 100 -s ortools
```
- With policy DP and Google OR-Tools solver
```
python main.py grid.txt -p DP -d 100 -s ortools
```
- With policy NP and Google OR-Tools solver
```
python main.py grid.txt -p NP -d 100 -s ortools
```
- With policy NP_1 and Google OR-Tools solver
```
python main.py grid.txt -p NP_1 -d 100 -s ortools
```
- With policy EP and CW-TS solver
```
python main.py grid.txt -p EP -d 100 -s cwts
```
- With policy DP and CW-TS solver
```
python main.py grid.txt -p DP -d 100 -s cwts
```
- With policy NP and CW-TS solver
```
python main.py grid.txt -p NP -d 100 -s cwts
```
- With policy NP_1 and CW-TS solver
```
python main.py grid.txt -p NP_1 -d 100 -s cwts
```

The following plots show a comparison of the four policies applied to customers' orders datasets, simulated with different seeds: it can be noticed that the best policy, the one that minimizes the costs, to apply is NP_1.
In the same plots we show the further improvement due to the use of CW-TS solver. The application of policy NP_1, combined with the CW-TS solver lead to a costs' reduction of about 3.29%.

![alt text](https://github.com/ChiaraVercellino/Thesis-CVRP/blob/master/Images_PDF/obj_fun_daily_histogram_NS_all.png)
![alt text](https://github.com/ChiaraVercellino/Thesis-CVRP/blob/master/Images_PDF/obj_fun_histogram_NS_all.png)
![alt text](https://github.com/ChiaraVercellino/Thesis-CVRP/blob/master/Images_PDF/vehicles_daily_histogram_NS_all.png)



## Built With

* [Python] https://www.python.org/downloads/
* [VSCode] https://code.visualstudio.com/
* [OR-Tools] https://developers.google.com/optimization

## Licensing and Authors

This code for CVRP simulation is written in Python. It was developed during my Master Thesis at the Politecnico di Torino with the supervisor Paolo Brandimarte.
The author of the code is
* [ChiaraVercellino](https://github.com/ChiaraVercellino) - *chia.vercellino@gmail.com*

## Acknowledgments

* code: [Vehicle Routing Problem](https://developers.google.com/optimization/routing/vrp)
* code: [Limit the number of locations visited by a vehicle in CVRP](https://github.com/google/or-tools/issues/958#issuecomment-470010900)
* paper: [The dynamic multiperiod vehicle routing problem with probabilistic information](https://www.sciencedirect.com/science/article/abs/pii/S0305054814000458)
* master thesis: [A top-down approach for the Dynamic Vehicle Routing Problem](https://webthesis.biblio.polito.it/8629/)














