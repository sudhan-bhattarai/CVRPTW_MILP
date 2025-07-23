# Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)

This repository provides a solution to the standard Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). In a CVRPTW, we aim to optimize the routes of a fleet of vehicles serving customers located in different geographic areas. Each customer demands a specific quantity of goods, and the goal is to minimize the total distance traveled while adhering to constraints, such as vehicle capacity and requested time windows for delivery.

For further context and the detailed mathematical model, refer to [`document/problem.pdf`][doc].

---

## Implementation Details

The project is implemented using the Python programming language and the Gurobi optimization solver. All required 
dependencies are listed in [requirements.txt][dependencies]. To set up the environment, install the dependencies using:`pip install -r requirements.txt`. Additionally, a valid Gurobi license is required to run the solver. For licensing details, visit [Gurobi Licensing][gurobi].

---

## Usage
The problem can be solved with `python solve.py` the command-line arguments used for configuration are documented in 
[arguments.json][args].

### Command-Line Options

The script supports the following customizable options:

| Option                               | Description                                                                                  | Default Value               |
|--------------------------------------|----------------------------------------------------------------------------------------------|-----------------------------|
| `-h`, `--help`                       | Show the help message and exit                                                               |                             |
| `--V V`                              | Number of vehicles                                                                           | `4`                         |
| `--v_cap V_CAP`                      | Capacity of vehicles                                                                         | `4`                         |
| `--I I`                              | Number of customers                                                                          | `15`                        |
| `--r R`                              | Number of miles around the depot (radius) of the network                                     | `10`                        |
| `--loc_depot LOC_DEPOT`              | Location (latitude, longitude) of the depot                                                 | `[40.943, -75.501]`         |
| `--delta DELTA`                      | Duration of service (in hours) for each customer                                             | `0.25`                      |
| `--alpha ALPHA`                      | Factor to convert distance to travel time                                                   | `1`                         |
| `--day_start DAY_START`              | Clock time representing the start of a business day                                          | `9`                         |
| `--day_end DAY_END`                  | Clock time representing the end of a business day                                            | `17`                        |
| `--demand_per_customer DEMAND_PER_CUSTOMER` | Number of units of commodities to drop off at each customer                                 | `1`                         |
| `--max_time_window_length MAX_TIME_WINDOW_LENGTH` | Maximum number of hours a time window may last                                                | `4`                         |
| `--travel_time_factor TRAVEL_TIME_FACTOR` | Factor by which travel time relates to `(distance / radius)`                                 | `2`                         |
| `--time_windows {0,1}`               | Activate time-windows constraints (`1`) or not (`0`)                                         | `0`                         |
| `--capacity {0,1}`                   | Activate vehicle capacity constraints (`1`) or not (`0`)                                     | `1`                         |

#### Example Command

To simulate a scenario with five vehicles, each having a capacity of five, and serving 20 customers, use the following command:

`python solve.py --V 5 --I 20 --v_cap 5`

This runs a CVRPTW where:
- **Number of vehicles (`--V`)**: 5  
- **Vehicle capacity (`--v_cap`)**: 5 units each  
- **Number of customers (`--I`)**: 20


## Notes to Ensure Feasibility

- The total fleet capacity, calculated as **V * v\_cap** (number of vehicles multiplied by vehicle capacity), must be sufficient to meet the total customer demand, which is **I * demand\_per\_customer** (number of customers multiplied by demand per customer).
  
- The number of vehicles (**$V$**) must be adequate to service all customers within the specified time window, which is controlled by the `max_time_window_length` parameter. Insufficient vehicles may result in infeasible routes.

- Only one of the options, `time_windows` or `capacity`, can be disabled by setting it to zero. Disabling both (`time_windows=0` and `capacity=0`) will lead to subtours, making the solution infeasible.

## Example: Vehicle Routing Problem (VRP)

The figure below illustrates a VRP scenario with 20 customers placed randomly around the depot. 

![Network of VRP][net_vrp_image]

An optimal solution for this problem, using a fleet of five vehicles (four is enough in the optimal solution), is 
visualized as 
follows:

![Solution for VRP][sol_vrp_image]

---

## Example: Traveling Salesperson Problem (TSP)

The Traveling Salesperson Problem (TSP) represents a special case of the VRP where only one vehicle is used, and its capacity is sufficient to meet the demand of all customers. The objective is to optimize routes by minimizing the total travel distance.

Below is an example with 40 customers:

![Network of TSP][net_tsp_image]

The optimal route, considering only capacity constraints (no time windows), is shown here:

![Solution for TSP][sol_tsp_image]

---
Updated: 07/23/2025

[//]: # (References)
[doc]: document/problem.pdf
[dependencies]: requirements.txt
[gurobi]: https://www.gurobi.com/solutions/licensing/
[net_vrp_image]: output/network_num_vehicle5_num_customers20.PNG
[sol_vrp_image]: output/solution_num_vehicle5_num_customers20.PNG
[net_tsp_image]: output/network_num_vehicle1_num_customers40.PNG
[sol_tsp_image]: output/solution_num_vehicle1_num_customers40.PNG
[arguments.json]: arguments.json
