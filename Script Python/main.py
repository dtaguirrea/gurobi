#!/usr/bin/env python3.11
# importamos librerías
from gurobipy import Model, GRB, quicksum
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
