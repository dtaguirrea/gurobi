"""Lectura de parámetros desde Excel. Sin esquema ni datos predefinidos."""
from excel_io import read_xlsx


def load_data(path):
    if not path.is_file():
        raise FileNotFoundError(f'Agrega la instancia de entrada: {path}')
    sheets = read_xlsx(path)
    # TODO: convertir las hojas en conjuntos y parámetros del modelo.
    # TODO: validar encabezados, datos faltantes, unidades y claves únicas.
    raise NotImplementedError('Completa load_data() con el esquema de tu instancia.')
