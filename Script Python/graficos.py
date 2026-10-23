import pandas as pd
import os


def cargar_datos(path: str) -> dict[str, pd.DataFrame]:
    print("Leyendo datos del excel")
    file = os.path.join(path)
    datos = pd.read_excel(file, sheet_name=["x", "u", "v", "w", "w_v"])
    print("Datos cargados con éxito")
    return datos


def save_graphs(dfs: dict[str, pd.DataFrame]) -> None:
    print("Generando graficos")
    x = dfs["x"]
    plantas_construidas = x[x["x"] == 1]
    print(plantas_construidas)
    


if __name__ == "__main__":
    dfs = cargar_datos(os.path.join("Análisis de Excels", "variables.xlsx"))
    save_graphs(dfs)