# Base Python-Gurobi · E3

Estructura inicial sin modelo, datos ni resultados de ejemplo.

## Archivos por completar

- `Script Python/data_io.py`: lectura del esquema y validación de parámetros.
- `Script Python/model.py`: variables, función objetivo y restricciones.
- `Script Python/validation.py`: chequeos operativos de la solución.
- `Script Python/results.py`: agregar indicadores y tablas del proyecto.
- `Instancias Excel/instancia.xlsx`: agregar la instancia real del grupo.

`main.py` coordina la ejecución y fija `TimeLimit = 1800` segundos.
`excel_io.py` permite leer y escribir tablas XLSX usando biblioteca estándar,
sin dependencias externas adicionales. Lee valores, no evalúa fórmulas de Excel.
`results.py` exporta el estado, objetivo y variables disponibles a Excel.

La base se detiene con un mensaje hasta completar los puntos marcados con `TODO`.
No resuelve un modelo vacío ni produce resultados artificiales.

## Entorno y ejecución

Requiere Python 3.10 o superior y una licencia de Gurobi adecuada al modelo.
Desde la raíz del repositorio, en PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe "Script Python/main.py"
```

Las rutas se resuelven desde la ubicación del proyecto.
Las salidas se guardan en `Análisis de Excels/`.
No subir licencias ni credenciales a GitHub.

<img width="228" height="228" alt="image" src="https://github.com/user-attachments/assets/e58904d9-ced2-4cb2-b4c9-c3fd1a5af69a" />

