# CVRP with stochastic customers over time

We are addressing to a Capacitated Vehicles Routing Problem (CVRP) with customers' arriaval that are Stochastic over time.

The customers are simulated on a rectangular region 205x215 km^2, the region is divided in cells of dimensions 5×5 km^2, the probability of customers belonging to a cell and the definitions of cells' coordinates are defined by input file `grid.txt`. Each day we simulate the number of new customers using a Uniform distribution, whose parameters can be modified in file `constant.py`. Then their positions on the region of interest is performed by a Multinomial distribution, to specify the cells they're coming from; finally a Uniform distribution on both dimension of each cell specify the coordinates of each new customers.

Each day we select the custumers to serve, among the pending ones, and than we solve a CVRP with deterministic information about customers' positions, demands (kg) and service time (min) 

So the proposed algorithms solves the problem in 2 stages:
- Selection of custumers to serve in the current day
- CVRP solved with ORtools library

The *objective function* to minimize is composed by:
- the total travel cost (expressed in terms of minutes to travel)
- the number of vehicles needed to serve customers

The *constraints* concern:
- Total load of each vehicle
- Number of customer for each vehicle
- Total working time of each vehicle (travel time + service time)

## Getting Started

To get you a copy of the project:

```
git clone https://github.com/ChiaraVercellino/Tesi-VRP.git
```

To run on your local machine:
```
python main.py input_file_path -p policy -d days_simulation
```

WHERE:
- `input_file_path` is the file containing density distribution
- `policy` is the desired policy to select which customers to serve
    - EP : early policy
    - DP : delayed policy
    - NP : neighbourhood policy (version 1)
    - NP_1 : neighbourhood policy (version 2)
- `days_simulation` is the number of day you want to simulate

### Prerequisites and Installing

To execute the simulator you need to install the following libraries. The following commands will install them in the selected virtual environment. The `ortools` library cannot be installed correctly using PyCharm editor, it's suggested to use VS code with python extension and C++ toolset.

```
pip install ortools
pip install time
pip install statistics
pip install numpy
pip install future
pip install matplotlib
pip install pandas
```

For issues about 'ortools' installation:
https://developers.google.com/optimization/install


## Running the tests

To run the simulation with the test parameters defined in `constant.py` and the distribution of customers according to `grid.txt`:
- With policy EP
```
python main.py grid.txt -p EP -d 100
```
- With policy DP
```
python main.py grid.txt -p DP -d 100
```
- With policy NP
```
python main.py grid.txt -p NP -d 100
```
- With policy NP_1
```
python main.py grid.txt -p NP_1 -d 100
```

## Built With

* [Python] https://www.python.org/downloads/
* [VSCode] https://code.visualstudio.com/
* [OrTools] https://developers.google.com/optimization

## Licensing and Authors

This code for CVRP simulation is written in Python.
The author of the code is
* [ChiaraVercellino](https://github.com/ChiaraVercellino) - *chia.vercellino@gmail.com*
It was mostly developed during Master Thesis at the Politecnico di Torino with supervisor Paolo Brandimarte.

## Acknowledgments

* code: [Vehicle Routing Problem](https://developers.google.com/optimization/routing/vrp)
* code: [Limit the number of locations visited by a vehicle in CVRP](https://github.com/google/or-tools/issues/958#issuecomment-470010900)
* paper: [The dynamic multiperiod vehicle routing problem with probabilistic information](https://www.sciencedirect.com/science/article/abs/pii/S0305054814000458)
* master thesis: [A top-down approach for the Dynamic Vehicle Routing Problem](https://webthesis.biblio.polito.it/8629/)














