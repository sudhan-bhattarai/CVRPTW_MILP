import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from gurobipy import *

''' we can also check different vehicle capacities for optimal routes'''
Q = 200  # vehicle capacity
no_of_vehicles = 3  # free to modify
no_of_customers = 15
df = pd.read_csv(r'C:\Users\Administrator\github\VRP\MVRP_400N.txt', sep = " ")
df = df.iloc[0:no_of_customers+1]

Y, X = list(df["Y"]), list(df["X"])
coordinates = np.column_stack((X, Y))

'''
et, lt, st = list(df["Et"]), list(df["Lt"]), list(df["St"])  # needed for time windows
'''

Demand = list(df["Demand"])
n = len(coordinates)
depot, customers = coordinates[0, :], coordinates[1:, :]
M = 100**100  # big number

m = Model("MVRP")
x, y, z = {}, {}, {}  #intialize the decision variables

'''distance matrix (32*32 array)'''
dist_matrix = np.empty([n, n])
for i in range(len(X)):
    for j in range(len(Y)):
        '''variable_1: X[i,j] =(0,1), i,j = Nodes'''
        x[i, j] = m.addVar(vtype=GRB.BINARY, name="x%d,%d" % (i, j))
        dist_matrix[i, j] = np.sqrt((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2)
        if i == j:
            dist_matrix[i, j] = M  ## big 'M'
        continue
m.update()

'''variable_2: y[j] = cumulative demand covered'''
for j in range(n):
    y[j] = m.addVar(vtype=GRB.INTEGER, name="y%d" % (j))   # cumulative demand satisfied variable
    z[j] = m.addVar(vtype=GRB.INTEGER, name="z%d" % (j))   # cumulative time variable
m.update()

'''constraint_1: sum(x[i,j]) = 1, for i = 1,2,...,32'''  # vehicles leaving each customer node
for i in range(n - 1):
    m.addConstr(quicksum(x[(i + 1, j)] for j in range(n)) == 1)
m.update()

''' constraint_2: sum(x[i,j] =1 for j = 1,2,.....,32)'''  # vehicles arriving to each customer node
for j in range(n - 1):
    m.addConstr(quicksum(x[(i, j + 1)] for i in range(n)) == 1)
m.update()

'''constraint_3: sum(x[0,j]) = 5'''  # vehicles leaving depot
m.addConstr(quicksum(x[(0, j)] for j in range(n)) == no_of_vehicles)
m.update()

'''constraint_4: sum(x[i,0]) = 5'''  # vehicles arriving to depot
m.addConstr(quicksum(x[(i, 0)] for i in range(n)) == no_of_vehicles)
m.update()

''' Either of the constraint_5 or the constrain_6 can eliminate sub-tours independently'''

'''constraint_5: capacity of vehicle and also eliminating sub-tours'''
for j in range(n - 1):
    m.addConstr(y[j + 1] <= Q)
    m.addConstr(y[j + 1] >= Demand[j + 1])
    for i in range(n - 1):
        m.addConstr(y[j + 1] >= y[i + 1] + Demand[j + 1] * (x[i + 1, j + 1]) - Q * (1 - (x[i + 1, j + 1])))
m.update()


'''constraint_6: time-windows and also eliminating sub-tours'''
'''
for i in range(n - 1):
    # assumption: service starts at 9:00 AM, 9 == 0 minutes, each hour after 9 is 60 minutes plus previous hours
    m.addConstr(z[i + 1] >= (et[i + 1] - 9) * 60)  # service should start after the earliest service start time
    m.addConstr(z[i + 1] <= (lt[i + 1] - 9) * 60)  # service can't be started after the latest service start time
    for j in range(n - 1):
        # taking the linear distance from one node to other as travelling time in minutes between those nodes
        m.addConstr(z[i + 1] >= z[j + 1] + (st[j + 1] + dist_matrix[j + 1, i + 1]/100) * x[j + 1, i + 1] - M*(1-x[j+1, i+1]))
m.update()
'''

'''objective function'''
m.setObjective(quicksum(quicksum(x[(i, j)]*dist_matrix[(i, j)] for j in range(n)) for i in range(n)),GRB.MINIMIZE)
m.update()

'''optimize'''
m.optimize()

'''retrieve the solution'''
sol_y, sol_x, sol_z = m.getAttr('x', y), m.getAttr('x', x), m.getAttr('x', z)
X, Y, Z = np.empty([n, n]), np.empty([n]), np.empty([n])
for i in range(n):
    Y[i] = sol_y[i]
    Z[i] = sol_z[i]
    for j in range(n):
        X[i, j] = int(sol_x[i, j])
print('\nObjective is:', m.objVal)
print('\nDecision variable X (binary decision of travelling from one node to another):\n', X.astype('int32'))
print('\nDecision variable z:(service start time of every customers in minutes)\n', Z.astype('int32')[1:])
print('\nDecision variable y (cumulative demand collected at every customer node):\n', Y.astype('int32')[1:])


def plot_tours(solution_x):
    tours = [[i, j] for i in range(solution_x.shape[0]) for j in range(solution_x.shape[1]) if solution_x[i, j] ==1]
    for t, tour in enumerate(tours):
        plt.plot(df["X"][tour], df["Y"][tour], color = "black", linewidth=0.5)
    plt.scatter(df["X"][1:], df["Y"][1:], marker = 'x', color = 'g', label = "customers")
    plt.scatter(df["X"][0], df["Y"][0], marker = "o", color = 'b', label = "depot")
    plt.xlabel("X"), plt.ylabel("Y"), plt.title("Tours"), plt.legend(loc = 4)
    plt.show()

plot_tours(X)
