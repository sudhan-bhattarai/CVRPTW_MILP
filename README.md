# CVRPTW stands for Capacitated Vehicle Routing Problem with Time Windows
This code is written in Python3-Gurobi API interface.
This is a 'capacitated' multiple vehicle routing problem.
This code also incorporates the 'time windows' constraint.

#### VRP is a NP-hard problem and hence the computational time increases polynomially even for a small increment in the problem size. 

We can levitate the time windows constraint if only solving the capacitated problem.

Or we can levitate the capacity constraint if only dealing with the time windows with unlimited vehicle capacity.

Either of those constraints are capable of eliminating the sub-tours.

The CSV file with 400 nodes has (x,y) coordinates of depot and customer nodes, demand at customer node and profit.

The CSV file with only 10 nodes is to test time windows. It has earliet start time, latest start time, and service duration. Travelling time from one node to another is  directly proportional to the linear distance between those two nodes.
