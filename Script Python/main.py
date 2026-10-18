#!/usr/bin/env python3.11
# importamos librerías
from gurobipy import Model, GRB
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

print(x)