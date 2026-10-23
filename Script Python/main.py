#!/usr/bin/env python3.11
# importamos librerías
from gurobipy import Model, GRB, quicksum
import pandas as pd
import sys
from graficos import save_graphs
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
def alpha_1(t: int) -> float:
    return quicksum(g_k * v[k, t] for k in U)

def alpha_2(t:int ) -> float:
    return - quicksum((c_p[j] + m[k]) * y_0[j, k, t] for k in U for j in F)

def alpha_3(t:int ) -> float:
    return - quicksum(c_o[j] * e[j, k, t] for j in F for k in U)

def alpha_4(t:int ) -> float:
    return - quicksum(c_t[i, k] * z[i, k, t] for k in U for i in I)

def alpha_5(t:int ) -> float:
    return - quicksum(c_v[i] * w_v[i, t] for i in I)

def alpha_6(t:int ) -> float:
    return - quicksum(c_r[i, p] * w[i, p, t] for i in I for p in P)

def alpha_7(t:int ) -> float:
    return - quicksum(c_a * u[k, t] for k in U)

def alpha(t: int) -> float:
    return alpha_1(t) + alpha_2(t) + alpha_3(t) + alpha_4(t) + alpha_5(t) + alpha_6(t) + alpha_7(t)

# TEMPORAL
"""
func_obj = -(quicksum(x[j, k]+y_0[j, k, t]+y_c[j, k, t]+e[j, k, t] for j in F for k in U for t in T) + 
                    quicksum(u[k, t] + v[k, t] for k in U for t in T) + quicksum(z[i, k, t] for i in I for k in U for t in T) + quicksum(w[i, p, t] for i in I for p in P for t in T) + quicksum(w_v[i, t] for i in I for t in T))
"""
func_obj = quicksum(alpha(t)/((1+k_i)**t) for t in T)
model.setObjective(func_obj, GRB.MAXIMIZE)

# Constantes para evitar que gurobi se coma todos los recursos
model.Params.NumericFocus = 1
model.Params.DualReductions = 0
model.Params.SoftMemLimit = 10.0  # GB
model.Params.Threads = 4
model.Params.NodeFileStart = 0.5
# Aplicamos las restricciones
model.update()
# Optimizamos
model.optimize()

# Validamos la solución
if model.Status == GRB.OPTIMAL:
    print("Se ganó:", model.ObjVal)

elif model.Status == GRB.TIME_LIMIT:
    if model.SolCount > 0:
        print("Límite de tiempo. Mejor solución:", model.ObjVal)
    else:
        print("Límite de tiempo sin solución factible.")

elif model.Status == GRB.INFEASIBLE:
    print("El modelo es infactible.")
    model.computeIIS()
    model.write("modelo_infactible.ilp")
    print("IIS guardado en modelo_infactible.ilp")

elif model.Status == GRB.UNBOUNDED:
    print("El modelo es no acotado.")

elif model.Status == GRB.INF_OR_UNBD:
    print("El modelo es infactible o no acotado.")

else:
    print("Estado Gurobi:", model.Status)


# Guardamos los resultados en dataframes
x_df = pd.DataFrame(
    [
        {"j": j, "k": k, "x": x[j, k].X}
        for j in F
        for k in U
    ]
)
y_0_df = pd.DataFrame(
    [
        {"j": j, "k": k, "t": t, "y_0": y_0[j, k, t].X}
        for j in F
        for k in U
        for t in T
    ]
)
y_c_df = pd.DataFrame(
    [
        {"j": j, "k": k, "t": t, "y_c": y_c[j, k, t].X}
        for j in F
        for k in U
        for t in T
    ]
)
e_df = pd.DataFrame(
    [
        {"j": j, "k": k, "t": t, "e": e[j, k, t].X}
        for j in F
        for k in U
        for t in T
    ]
)
u_df = pd.DataFrame(
    [
        {"k": k, "t": t, "u": u[k, t].X}
        for k in U
        for t in T2
    ]
)
v_df = pd.DataFrame(
    [
        {"k": k, "t": t, "v": v[k, t].X}
        for k in U
        for t in T
    ]
)
z_df = pd.DataFrame(
    [
        {"i": i, "k": k, "t": t, "z": z[i, k, t].X}
        for i in I
        for k in U
        for t in T
    ]
)
w_df = pd.DataFrame(
    [
        {"i": i, "p": p, "t": t, "w": w[i, p, t].X}
        for i in I
        for p in P
        for t in T
    ]
)
w_v_df = pd.DataFrame(
    [
        {"i": i, "t": t, "w_v": w_v[i, t].X}
        for i in I
        for t in T
    ]
)

# Los escribimos en el excel

with pd.ExcelWriter(os.path.join("Análisis de Excels", "variables.xlsx")) as writer:
    x_df.to_excel(writer, sheet_name="x", index=False)
    y_0_df.to_excel(writer, sheet_name="y_0", index=False)
    y_c_df.to_excel(writer, sheet_name="y_c", index=False)
    e_df.to_excel(writer, sheet_name="e", index=False)
    u_df.to_excel(writer, sheet_name="u", index=False)
    v_df.to_excel(writer, sheet_name="v", index=False)
    z_df.to_excel(writer, sheet_name="z", index=False)
    w_df.to_excel(writer, sheet_name="w", index=False)
    w_v_df.to_excel(writer, sheet_name="w_v", index=False)

# Generamos los gráficos
save_graphs({"x": x_df, 
             "y_0": y_0_df, 
             "y_c": y_c_df, 
             "e": e_df, 
             "u": u_df, 
             "v": v_df, 
             "z": z_df, 
             "w": w_df, 
             "w_v": w_v_df})

with open("variables.txt", "w") as f:
    print("\n".join(map(lambda i: f"{i.VarName}: {i.X}",model.getVars())), file=f)