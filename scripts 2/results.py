"""Exportación genérica a Excel, exclusivamente desde atributos de Gurobi."""
import math

import gurobipy as gp
from gurobipy import GRB

from excel_io import write_xlsx


def attribute(model, name):
    try:
        value = model.getAttr(name)
        if isinstance(value, float) and not math.isfinite(value):
            return str(value)
        return value
    except (gp.GurobiError, AttributeError):
        return None


def export_results(model, path, checks=None):
    tables = {
        'Resumen': [
            ['metric', 'value'],
            ['status_code', model.Status],
            ['optimal_with_solver_tolerances', model.Status == GRB.OPTIMAL],
            ['solution_count', model.SolCount],
            ['runtime_seconds', model.Runtime],
            ['time_limit_seconds', model.Params.TimeLimit],
            ['objective', attribute(model, 'ObjVal') if model.SolCount else None],
            ['best_bound', attribute(model, 'ObjBound')],
            ['mip_gap', attribute(model, 'MIPGap')],
        ],
    }
    if model.SolCount > 0:
        tables['Variables'] = [['variable', 'value', 'domain']]
        tables['Variables'] += [[v.VarName, v.X, v.VType] for v in model.getVars()]
        if checks is not None:
            tables['Validaciones'] = [['check', 'passed']] + [
                [name, bool(passed)] for name, passed in checks.items()]
    # TODO: agregar tablas procesadas e indicadores específicos del proyecto.
    write_xlsx(path, tables)
