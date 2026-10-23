import pandas as pd
import os
import matplotlib.pyplot as plt


def cargar_datos(path: str) -> dict[str, pd.DataFrame]:
    print("Leyendo datos del excel")
    file = os.path.join(path)
    datos = pd.read_excel(file, sheet_name=["x", "u", "v", "w", "w_v", "z"])
    print("Datos cargados con éxito")
    return datos


def create_destinations_graph(dfs: dict[str, pd.DataFrame], path: str):
    x = dfs["x"]
    z = dfs["z"]
    w = dfs["w"]
    
    plantas_construidas = x[x["x"] == 1]
    ks = set(plantas_construidas["k"])
    
    z_filtered = z[z["k"].isin(ks)]
    zs = z_filtered.groupby(["k"]).sum()
    ws = w.groupby(["p"]).sum()
    # print(ws.columns)
    ws["k"] = ws.index
    ws = ws.rename(columns={"w": "z"})
    zs["k"] = zs.index
    zs["k"] = zs["k"].astype(str)

    total_vert = dfs["w_v"][["w_v"]].sum()
    print(ws)
    
    row = pd.DataFrame({"k": "vertedero", "z": total_vert, "i": pd.NA, "t": pd.NA})
    zs = pd.concat([zs, row])
    zs = pd.concat([zs, ws])
    # print(zs)
    # print(pd.concat([zs, ws]))
    zs.plot(kind="bar", x="k", y="z", 
            title="Cantidad de residuos enviados a los destinos",
            xlabel="Ubicación",
            ylabel="Toneladas de residuos enviadas durante todos los periodos")
    print(zs)
    plt.savefig(os.path.join(path, "destinations.png"), dpi=300, bbox_inches="tight")


def save_graphs(dfs: dict[str, pd.DataFrame], path: str) -> None:
    total_graficos = 1
    print("Generando graficos")
    create_destinations_graph(dfs, path)
    print(f"1/{total_graficos}")
    


if __name__ == "__main__":
    dfs = cargar_datos(os.path.join("Análisis de Excels", "variables.xlsx"))
    save_graphs(dfs, "Graficos")