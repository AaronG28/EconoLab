from pathlib import Path
import pandas as pd


def importar_archivo(ruta):
    """
    Importa un archivo CSV o Excel sin modificar el archivo original.

    Devuelve un diccionario con los datos importados.
    """

    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encuentra el archivo: {ruta}"
        )

    extension = ruta.suffix.lower()

    if extension == ".csv":
        datos = pd.read_csv(ruta)

    elif extension in [".xlsx", ".xls"]:
        datos = pd.read_excel(ruta)

    else:
        raise ValueError(
            f"Formato no compatible: {extension}"
        )

    return {
        "nombre": ruta.name,
        "ruta": ruta,
        "datos": datos,
        "filas": len(datos),
        "columnas": len(datos.columns)
    }