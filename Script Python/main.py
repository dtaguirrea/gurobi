#!/usr/bin/env python3.11
# importamos librerías
from gurobipy import Model, GRB, quicksum
import sys
# Cargamos datos
from load_data import *

# Creamos el modelo
model = Model()
model.setParam('TimeLimit', 1800)

# Variables
x = model.addVars(F, U, vtype=GRB.BINARY, name="x_jk")
y_0 = model.addVars(F, U, T, vtype=GRB.BINARY, name="y0_jkt")
y_c = model.addVars(F, U, T, vtype=GRB.BINARY, name="yc_jkt")
e = model.addVars(F, U, T, vtype=GRB.BINARY, name="e_jkt")
u = model.addVars(U, T2, vtype=GRB.CONTINUOUS, name="u_kt")
v = model.addVars(U, T, vtype=GRB.CONTINUOUS, name="v_kt")
z = model.addVars(I, U, T, vtype=GRB.CONTINUOUS, name="z_ikt")
w = model.addVars(I, P, T, vtype=GRB.CONTINUOUS, name="w_ipt")
w_v = model.addVars(I, T, vtype=GRB.CONTINUOUS, name="wv_it")

# Restricciones
## Las restricciones están en el orden especificado en el informe
model.addConstrs((quicksum(x[j, k] for j in F) <= 1 for k in U), name="R1")
model.addConstrs((quicksum(y_0[j, k, t] for t in T) == x[j, k] for j in F for k in U), name="R2")
model.addConstrs((quicksum(y_c[j, k, t] for j in F for k in U) <= beta for t in T), name="R3")
model.addConstrs((y_c[j, k, t] == quicksum(y_0[j, k, t1] for t1 in range(max(1, t-t_c[j]+1), t)
                                           ) for j in F for k in U for t in T), name="R4")
model.addConstrs((y_0[j, k, t] == 0 for j in F for k in U for t in range(T[-1]-t_c[j]+1, T[-1])), name="R5")
model.addConstrs((e[j, k, t] == quicksum(y_0[j, k, t3] for t3 in range(1, t-t_c[j])
                                         ) for j in F for k in U for t in T), name="R6")
model.addConstrs((u[k, t] <= quicksum(sigma[j]*e[j, k, t] for j in F) for t in T for k in U), name="R7")
model.addConstrs((u[k, 0] == 0 for k in U), name="R8")
model.addConstrs((u[k, t-1]+ quicksum(z[i, k, t] for i in I)== v[k, t]+u[k, t] for k in U for t in T), name="R9")
model.addConstrs((v[k, t] <= quicksum(tau[j]*e[j, k, t] for j in F) for k in U for t in T), name="R10")
model.addConstrs((d[i, t] == quicksum(w[i, p, t] for p in P)+quicksum(z[i, k, t]for k in U)
                   + w_v[i, t] for t in T for i in I), name="R11")
model.addConstrs((quicksum(w[i, p, t] for i in I) <= d_c[p] for p in P for t in T), name="R12")
## No es necesario establecer la no-negatividad de las variables, por convención
## Ver https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/variables.html
# Se actualiza el modelo
model.update()

# Funcion objetivo
# TEMPORAL
func_obj = -(quicksum(x[j, k]+y_0[j, k, t]+y_c[j, k, t]+e[j, k, t] for j in F for k in U for t in T) + 
                    quicksum(u[k, t] + v[k, t] for k in U for t in T) + quicksum(z[i, k, t] for i in I for k in U for t in T) + quicksum(w[i, p, t] for i in I for p in P for t in T) + quicksum(w_v[i, t] for i in I for t in T))
model.setObjective(func_obj, GRB.MAXIMIZE)

# Resolvemos el modelo
model.optimize()
print("Se gano", model.ObjVal)
