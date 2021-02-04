# CVRPTW stands for Capacitated Vehicle Routing Problem with Time Windows
This code is written in Python3-Gurobi API interface.
In CVRPTW, a fleet of vehicles with a limited capacity leave depot to serve a set of customers and finally come back to the depot. Every customers have a preferred time window of visit. A vehicle can only visit the customers within their respective time window.

#### VRP is a NP-hard problem and hence the computational time increases polynomially even for a small increment in the problem size. 

We can levitate the time windows constraint if only solving the capacitated problem.

Or we can levitate the capacity constraint if only dealing with the time windows considering unlimited vehicle capacity.

Either of those constraints are capable of eliminating the sub-tours.

The CSV file with 400 nodes has (x,y) coordinates of depot and customer nodes, demand at customer node and the profit.

The CSV file with only 10 nodes has the time windows. It has the earliet service start time, latest service start time, and the service duration for all the customers. Travelling time from one node to another is directly proportional to the linear distance between those two nodes.
