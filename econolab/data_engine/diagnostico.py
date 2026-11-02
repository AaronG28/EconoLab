import pandas as pd


def diagnosticar_datos(datos):

    diagnostico = {
        "filas": len(datos),
        "numero_columnas": len(datos.columns),
        "filas_vacias": int(datos.isna().all(axis=1).sum()),
        "columnas_vacias": int(datos.isna().all(axis=0).sum()),
        "filas_duplicadas": int(datos.duplicated().sum()),
        "detalle_columnas": {}
    }

    for columna in datos.columns:

        diagnostico["detalle_columnas"][columna] = {
            "tipo": str(datos[columna].dtype),
            "valores_vacios": int(datos[columna].isna().sum()),
            "valores_unicos": int(datos[columna].nunique())
        }

    return diagnostico