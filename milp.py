import itertools
import gurobipy as gb
import numpy as np
from _utils import extract_routes


bi = gb.GRB.BINARY
ct = gb.GRB.CONTINUOUS
M = 1e10  # A big number (theoretically, infinity)


class ConstructModel(gb.Model):
    def __init__(self, data):
        super().__init__()  # Initialize Gurobi Model
        self._routes = []
        self._dt = data
        self._n = self._dt.args['I'] + 1  # Number of nodes (including depot)
        self._add_vars()
        self._add_constraints()
        self._add_objective()
        model_path = 'output/model_num_vehicle{}_num_customers{}.lp'.format(
            self._dt.args['V'], self._dt.args['I']
        )
        self.write(model_path)
        print(f'Model created at: {model_path}')

    def _add_vars(self):
        self._var = {
            # Binary variables for arcs (i, j) activations
            'x': self.addVars(self._n, self._n, vtype=bi, name='x'),
        }
        if self._dt.args['time_windows'] == 1:
            # Auxiliary variables for actual servie time
            self._var['s'] = self.addVars(self._n, vtype=ct, name='s')
        if self._dt.args['capacity'] == 1:
            # Auxiliary variables for cumulative demand satisfaction
            self._var['z'] = self.addVars(self._n, vtype=ct, name='z')
        self.update()

    def _add_constraints(self):
        # Number of vehicles leaving the depot (at most the entire fleet)
        self.addConstr(
            gb.quicksum(self._var['x'][0, j] for j in range(1, self._n))
            <= self._dt.args['V'],
            name='depot_exit'
        )
        # Number of vehicles coming back to the depot (same number that leaves)
        self.addConstr(
            gb.quicksum(self._var['x'][j, 0] for j in range(1, self._n)) ==
            gb.quicksum(self._var['x'][0, j] for j in range(1, self._n)),
            name='depot_return'
        )
        # Every customer must be satisfied
        for i in range(self._n):
            if i == 0:
                continue  # the case for depot is already defined above
            self.addConstr(
                gb.quicksum(self._var['x'][i, j] for j in range(self._n)) == 1,
                name=f'demand_satisfaction_1{i}'
            )
            self.addConstr(
                gb.quicksum(self._var['x'][j, i] for j in range(self._n)) == 1,
                name=f'demand_satisfaction_2_{i}'
            )
        if self._dt.args['capacity'] == 1:
            # Total demand satisfied by a vehicle cannot exceed vehicle capacity
            for i in range(1, self._n):
                for j in range(1, self._n):
                    self.addConstr(
                        self._var['z'][j] >=
                        self._var['z'][i]
                        + self._dt.demand[i - 1] * self._var['x'][i, j]
                        - M * (1 - self._var['x'][i, j]),
                        name=f'demand_flow_balance{i}_{j}'
                    ) # self._dt.demand[j - 1] because depot is not included
            # Vehicle capacity constraint
            self.addConstrs((
                self._var['z'][i] <= self._dt.args['v_cap'] for i in range(self._n)
            ))
        if self._dt.args['time_windows'] == 1:
            for i in range(1, self._n):
                for j in range(1, self._n):
                    self.addConstr(
                        self._var['s'][j] >=
                        self._var['s'][i]
                        + self._dt.travel_time_matrix[i - 1, j - 1] *
                        self._var['x'][i, j]
                        + self._dt.args['delta']
                        - M * (1 - self._var['x'][i, j]),
                        name=f'service_time_balance{i}_{j}'
                    )
            # Service cannot start before the earliest-start-time
            self.addConstrs((
                self._var['s'][i] >= self._dt.e_t[i - 1] for i in range(1, self._n)
            ))
            # Service cannot start after the latest-start-time
            self.addConstrs((
                self._var['s'][i] <= self._dt.l_t[i - 1] for i in range(1, self._n)
            ))
            self.addConstr(self._var['s'][0] == self._dt.args['day_start'],
                           name='day_start_time')
        self.update()

    def _add_objective(self):
        sense = gb.GRB.MINIMIZE
        self.setObjective(
            gb.quicksum(
                self._dt.dist_matrix[i, j] * self._var['x'][i, j]
                for i, j in itertools.product(range(self._n), range(self._n))
            ),
            sense=sense
        )
        self.update()

    def _gel_sol(self):
        assert self.status == gb.GRB.OPTIMAL, "Model is not optimal"
        x_sol = np.zeros((self._n, self._n))
        for i, j in self._var['x'].keys():
            x_sol[i, j] = round(self._var['x'][i, j].x)
        self._sol = {'x': x_sol.astype(int)}

        if self._dt.args['capacity'] == 1:
            z_sol = np.zeros(self._n)
            for i in self._var['z'].keys():
                z_sol[i] = self._var['z'][i].x
            self._sol['z'] = z_sol.astype(int)

        if self._dt.args['time_windows'] == 1:
            s_sol = np.zeros(self._n)
            for i in self._var['s'].keys():
                s_sol[i] = self._var['s'][i].x
            self._sol['s'] = s_sol.astype(int)

    def solve(self):
        self.optimize()
        self._gel_sol()
        self._routes = extract_routes(self._sol['x'])
        print('\n', '-'*5, 'The Solution', '-'*5, '\n')
        for i, r in enumerate(self._routes):
            print(f'The route vehicle {i} follows is {r}')
        if self._dt.args['time_windows'] == 1:
            print('The service-time solution is:\n', self._sol['s'])
        if self._dt.args['capacity'] == 1:
            print('The vehicle-capacity solution:\n', self._sol['z'])