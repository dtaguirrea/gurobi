"""Punto de entrada. Completar model.py y validation.py antes de resolver."""
import sys
from pathlib import Path
from zipfile import BadZipFile

import gurobipy as gp
from gurobipy import GRB

from data_io import load_data
from model import build_model
from results import export_results
from validation import validate_solution

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / 'Instancias Excel' / 'instancia.xlsx'
OUTPUT_DIR = ROOT / 'Análisis de Excels'


def main():
    try:
        data = load_data(INPUT_FILE)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with gp.Env() as env:
            with gp.Model('optimization_model', env=env) as model:
                model.Params.TimeLimit = 1800
                model.Params.Seed = 0
                model.Params.LogFile = str(OUTPUT_DIR / 'gurobi.log')

                variables = build_model(model, data)
                model.write(str(OUTPUT_DIR / 'modelo.lp'))
                model.optimize()

                checks = None
                if model.SolCount > 0:
                    checks = validate_solution(data, variables)
                    model.write(str(OUTPUT_DIR / 'solucion.sol'))

                export_results(model, OUTPUT_DIR / 'resultados.xlsx', checks)
                print(f'Estado Gurobi: {model.Status}')
                print(f'Resultados: {OUTPUT_DIR / "resultados.xlsx"}')
                if model.SolCount:
                    print(f'Valor objetivo: {model.ObjVal}')
                return 0 if model.SolCount and checks and all(checks.values()) else 2
    except (OSError, ValueError, BadZipFile, NotImplementedError, gp.GurobiError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
