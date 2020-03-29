import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from gurobipy import*

''' we can also check different vehicle capacities in a loop for optimal routes'''

Q = 62   #vehicle capacity

no_of_vehicles = 2   ## free to modify

df = pd.read_csv("VRPTW.txt",' ')
Y = list(df["Y"])
X = list(df["X"])
et = list(df["Et"])
lt = list(df["Lt"])
st = list(df["St"])
Demand = list(df["Demand"])
Demand[0] = 0
print(df)
et[0] = 0
lt[0] = 0
st[0] = 0
demand = Demand[1:]

coordinates = np.column_stack((X,Y))
n = len(coordinates)
depot = coordinates[0,:]
customers = coordinates[1:,:]
n =len(coordinates)

m = Model("MVRP")
x = {}
y = {}
z = {}

#variable_1: X[i,j] =(0,1), i,j = Nodes
#distance_matrix (32*32 array)
dist_matrix = np.empty([n,n])
for i in range (len(X)):
    for j in range (len(Y)):
        x[i,j] = m.addVar(vtype = GRB.BINARY, name = "x%d,%d" %(i,j))
        dist_matrix[i,j] = np.sqrt((X[i]-X[j])**2 + (Y[i]-Y[j])**2)
        if i==j:
            dist_matrix[i,j] = float('inf')            ## big 'M'
        continue
m.update()

#variable_2: y[j] = cumulative demand covered
for j in range(len(coordinates)):
    y[j] = m.addVar(vtype=GRB.INTEGER, name = "y%d" %(j))            ## cumulative demand satisfied variable
    z[j] = m.addVar(vtype=GRB.INTEGER, name="z%d" % (j))             ## cumulative time variable
m.update()

#constraint_1: sum(x[i,j]) = 1, for i = 1,2,...,32        ## vehicles leaving each customer node
for i in range (len(coordinates)-1):
    m.addConstr(quicksum(x[(i+1,j)] for j in range (len(coordinates))) == 1)
m.update()

#constraint_2: sum(x[i,j] =1 for j = 1,2,.....,32)        ## vehicles arriving to each customer node
for j in range (len(coordinates)-1):
    m.addConstr(quicksum(x[(i,j+1)] for i in range (len(coordinates))) == 1)
m.update()

#constraint_3: sum(x[0,j]) = 5            ## vehicles leaving depot
m.addConstr(quicksum(x[(0,j)] for j in range (len(coordinates))) == no_of_vehicles)
m.update()

#constraint_4: sum(x[i,0]) = 5            ## vehicles arriving to depot
m.addConstr(quicksum(x[(i,0)] for i in range (len(coordinates))) == no_of_vehicles)
m.update()

''' Either of constraint_5 or constrain_6 can eliminate subtours independently'''

#constraint_5: capacity of vehicle and also eliminating subtour
for j in range(len(coordinates)-1):
    m.addConstr(y[j+1]<= Q)
    m.addConstr(y[j+1]>=Demand[j+1])
    for i in range(len(coordinates)-1):
            m.addConstr(y[j+1] >= y[i+1] + Demand[j+1]*(x[i+1,j+1]) - Q*(1-(x[i+1,j+1])))
m.update()

# constraint_6: time windows
for i in range(len(coordinates)-1):
    m.addConstr(z[i+1] >= (et[i+1]-9)*60)   ## service starts at 9:00 AM, 9 == 0 mins, each hour after 9 is 60 mins plus previous hours
    m.addConstr(z[i+1] <= (lt[i+1]-9)*60)
    for j in range(len(coordinates)-1):
        m.addConstr(z[i+1] >= (z[j+1] + st[j+1] + dist_matrix[j+1, i+1])*(x[j+1,i+1]))  ## taking distance from one node to other as travelling time in minutes between those nodes
m.update()

#objective function
m.setObjective(quicksum(quicksum(x[(i,j)]*dist_matrix[(i,j)] for j in range (len(coordinates))) for i in range (len(coordinates))), GRB.MINIMIZE)
m.update()

m.optimize()

solution_y = m.getAttr('x',y)
solution_x = m.getAttr('x', x)
solution_z = m.getAttr('x', z)

# xx = pd.Series(solution_x).reset_index()
# yy = pd.Series(solution_y).reset_index()
# zz = pd.Series(solution_z).reset_index()

print("\n\n\nSingle Depot MVRP:")
print("\nNo of vehicles:",no_of_vehicles)
print("\nNo of Nodes:",n)
print("\nVehicle capacity:",Q)
total_demand = 0
for i in range(len(Demand)):
    total_demand+=Demand[i]
print('\nTotal Demand is:',total_demand)

print('\nObjective (minimum distance covered): %g' % m.objVal)
m.printAttr('x')

#passing variable array into dataframe
from_node=[]
to_node = np.empty([n,n])
collection =[]
for v in m.getVars():
        from_node.append(v.x)

#for i in range(len(from_node)):
#    print('x%d' %i,from_node[i])

for i in range(n):
    collection.append(int(from_node[n*n+i]))
    for j in range (n):
        to_node[i,j] = from_node[n*i+j]

print('\nDistance Matrix (dij):\n',pd.DataFrame(dist_matrix).astype('int64'))
print('\nDecision (Xij):\n',pd.DataFrame(to_node).astype('int64'))
#print('yj\n', pd.DataFrame(collection))

I = []
J = []

for i in range(n):
    for j in range(n):
        if to_node[i,j] > 0.5:
            I.append(i)
            J.append(j)
IJ = np.column_stack((I,J))
XX1 = []
XX2 = []
YY1 = []
YY2 = []
for i in I:
    XX1.append(X[i])
    YY1.append(Y[i])

for j in J:
    XX2.append(X[j])
    YY2.append(Y[j])

plt.subplot(1,2,1)
plt.scatter(X[1:],Y[1:],label = 'Customers', marker = 'o', color = 'blue')
plt.scatter(X[0],Y[0],label = 'Depot', marker = 'x', color = 'green')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.title('Customers')
#plt.legend(loc=4)
plt.subplot(1,2,2)
print("Graph: Green 'x' represent depot and Blue 'o' represent customers")
plt.scatter(X[1:],Y[1:], marker = 'o', color = 'blue')
plt.scatter(X[0],Y[0], marker = 'x', color = 'green')
plt.xlabel('x-coordinate')
plt.title('Multiple Vehicle Routing Problem, MVRP')
plt.plot([XX1,XX2], [YY1, YY2])
plt.show()
