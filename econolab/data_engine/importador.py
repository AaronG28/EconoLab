from pathlib import Path
import pandas as pd

from econolab.security.validacion_archivos import validar_archivo


def importar_archivo(ruta):
    """
    Importa un archivo CSV o Excel después de validar
    sus características básicas de seguridad.

    El archivo original no se modifica.
    """

    ruta = Path(ruta)

    # 1. Validar el archivo antes de procesarlo
    validar_archivo(ruta)

    # 2. Determinar el formato
    extension = ruta.suffix.lower()

    # 3. Importar los datos
    if extension == ".csv":
        datos = pd.read_csv(ruta)

    elif extension in [".xlsx", ".xls"]:
        datos = pd.read_excel(ruta)

    # 4. Devolver los datos importados
    return {
        "nombre": ruta.name,
        "ruta": ruta,
        "datos": datos,
        "filas": len(datos),
        "columnas": len(datos.columns)
    }