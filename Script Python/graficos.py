import pandas as pd
import os
import matplotlib.pyplot as plt


def cargar_datos(path: str) -> dict[str, pd.DataFrame]:
    print("Leyendo datos del excel")
    file = os.path.join(path)
    datos = pd.read_excel(file, sheet_name=["x", "u", "v", "w", "w_v", "z", "y_0", "y_c", "e"])
    print("Datos cargados con éxito")
    return datos


def create_destinations_graph(dfs: dict[str, pd.DataFrame], path: str, ks: set):
    z = dfs["z"]
    w = dfs["w"]

    
    z_filtered = z[z["k"].isin(ks)]
    zs = z_filtered.groupby(["k"]).sum()
    ws = w.groupby(["p"]).sum()
    # print(ws.columns)
    ws["k"] = "planta " + ws.index.astype(str)
    ws = ws.rename(columns={"w": "z"})
    zs["k"] = zs.index
    zs["k"] = zs["k"].astype(str)

    total_vert = dfs["w_v"][["w_v"]].sum()
    # print(ws)
    
    row = pd.DataFrame({"k": "vertedero", "z": total_vert, "i": pd.NA, "t": pd.NA})
    zs = pd.concat([zs, row])
    zs = pd.concat([zs, ws])
    # print(zs)
    # print(pd.concat([zs, ws]))
    ax = zs.plot(kind="bar", x="k", y="z", 
        title="Cantidad de residuos enviados a los destinos",
        xlabel="Ubicación",
        ylabel="Toneladas de residuos enviadas durante todos los periodos")
    ax.get_legend().remove()
    # print(zs)
    plt.savefig(os.path.join(path, "destinations.png"), dpi=300, bbox_inches="tight")


def create_selled_graphs(dfs: dict[str, pd.DataFrame], path: str):
    v = dfs["v"]
    v_grouped = v.groupby("t").sum()
    ax = v_grouped.plot(kind="bar", use_index=True, y="v", title="Cantidad de residuos consumidos por periodo",
                   xlabel="Periodo", ylabel="Toneladas de residuos vendidas")
    ax.get_legend().remove()
    plt.savefig(os.path.join(path, "amount_consumed.png"), dpi=300, bbox_inches="tight")


def create_plants_vs_time(dfs: dict[str, pd.DataFrame], path: str, ks):
    y_0 = dfs["y_0"]
    y_0_filtered = y_0[y_0["k"].isin(ks)]
    y_0_group = y_0_filtered.groupby(["t", "j"]).sum().reset_index()
    # print(y_0_group)
    ax = y_0_group.pivot(index="t", columns="j", values="y_0").plot(kind="bar", stacked=True,
                title="Plantas construidas por periodo",
                xlabel="Periodo",
                ylabel="Cantidad de plantas construidas")
    ax.legend(title="tipos")
    plt.savefig(os.path.join(path, "constructed_vs_time.png"), dpi=300, bbox_inches="tight")


def save_graphs(dfs: dict[str, pd.DataFrame], path: str) -> None:
    x = dfs["x"]
    plantas_construidas = x[x["x"] == 1]
    ks = set(plantas_construidas["k"])
    print(f"Plantas construidas en {ks}")

    
    total_graficos = 3
    print("Generando graficos")
    create_destinations_graph(dfs, path, ks)
    print(f"1/{total_graficos}")
    create_selled_graphs(dfs, path)
    print(f"2/{total_graficos}")
    create_plants_vs_time(dfs, path, ks)
    print(f"3/{total_graficos}")
    


if __name__ == "__main__":
    dfs = cargar_datos(os.path.join("Análisis de Excels", "variables.xlsx"))
    save_graphs(dfs, "Graficos")