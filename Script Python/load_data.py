#!/usr/bin/env python3.11

import pandas as pd
import os

# Funcion para iterar sobre una lista de columnas
def iter_over_rows(columns: list[str], df:pd.DataFrame):
    return df[columns].itertuples(index=False, name=None)

# Cargamos el excel
file = os.path.join("Instancias Excel", "datos-opti-E3.xlsx")
datos = pd.read_excel(file, sheet_name=None)

# Cargamos parámetros por cada hoja
## Generales (c_a, k_i, beta, g_r, g_k)
c_a= datos["generales"].loc[0, "c_a"]
k_i= datos["generales"].loc[0, "k_i"]
beta= datos["generales"].loc[0, "beta"]
g_r= datos["generales"].loc[0, "g_r"]
g_k= datos["generales"].loc[0, "g_k"]

d_c = {}
# los que dependen de p
if datos["p"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja p")
for p_local, d_c_local in iter_over_rows(["p", "d_c"], datos["p"]):
    d_c[p_local] = d_c_local

# Los que dependen de i, t
d = {}
if datos["it"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja it")
for i, t, d_local in iter_over_rows(["I", "t", "d"], datos["it"]):
    d[i, t] = d_local


# Los que dependen de k
m = {}
if datos["k"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja k")
for k, m_local in iter_over_rows(["k", "m"], datos["k"]):
    m[k] = m_local

# Los que dependen de i, p
c_r = {}
if datos["ip"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja ip")
for i, p, c_r_local in iter_over_rows(["I", "p", "c_r"], datos["ip"]):
    c_r[i, p] = c_r_local

# Los que dependen de i
c_v = {}
if datos["i"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja i")
for i, c_v_local in iter_over_rows(["I", "c_v"], datos["i"]):
    c_v[i] = c_v_local

# Los que dependen de i, k
c_t = {}
if datos["ik"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja ik")
for i, k, c_t_local in iter_over_rows(["I", "k", "c_t"], datos["ik"]):
    c_t[i, k] = c_t_local

# Los que dependen de j
c_p = {}
c_o = {}
t_c = {}
sigma = {}
tau = {}
if datos["j"].isnull().values.any():
    raise ValueError("Hay valores nulos en la hoja j")
for i, c_p_local, c_o_local, t_c_local, sigma_local, tau_local in iter_over_rows(["I", "c_p", "c_o", "t_c", "sigma", "tau"], datos["j"]):
    c_p[i] = c_p_local
    c_o[i] = c_o_local
    t_c[i] = t_c_local
    sigma[i] = sigma_local
    tau[i] = tau_local

# Definimos conjuntos
F = list(range(1, len(c_p)+1))
P = list(range(1, len(d_c)+1))
I = list(range(1, len(c_v)+1))
U = list(range(1, len(m)+1))
T = list(range(1, len(d)//len(I)+1))
print("T=", len(T))
T2 = list(range(0, len(T)+1))

# Realizamos validaciones

if len(c_t) != len(I)*len(U):
    raise ValueError(f"La hoja ik no tiene valores adecuados, cantidad de columnas={len(c_t)}",
                     f"I= {len(I)} U={len(U)}")