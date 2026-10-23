import pandas as pd
import os
import matplotlib.pyplot as plt


def cargar_datos(path: str) -> dict[str, pd.DataFrame]:
    print("Leyendo datos del excel")
    file = os.path.join(path)
    datos = pd.read_excel(file, sheet_name=["x", "u", "v", "w", "w_v", "z"])
    print("Datos cargados con éxito")
    return datos


def save_graphs(dfs: dict[str, pd.DataFrame]) -> None:
    print("Generando graficos")
    x = dfs["x"]
    plantas_construidas = x[x["x"] == 1]
    ks = set(plantas_construidas["k"])
    z = dfs["z"]
    filtered = z[z["k"].isin(ks)]
    total_vert = dfs["w_v"][["w_v"]].sum()
    
    zs = filtered.groupby(["k"]).sum()
    print(zs.columns.values)
    zs.plot(kind="bar", use_index=True, y="z")
    plt.savefig("grafico.png", dpi=300, bbox_inches="tight")
    
    # print(filtered)
    


if __name__ == "__main__":
    dfs = cargar_datos(os.path.join("Análisis de Excels", "variables.xlsx"))
    save_graphs(dfs)