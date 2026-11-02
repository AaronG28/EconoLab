
import pandas as pd

from econolab.data_engine.diagnostico import diagnosticar_datos


def crear_datos_prueba():
    return pd.DataFrame({
        "Pais": ["España", "España", None],
        "PIB": [100, 100, None],
        "columna_vacia": [None, None, None]
    })


def test_detectar_filas_vacias():
    datos = crear_datos_prueba()

    diagnostico = diagnosticar_datos(datos)

    assert diagnostico["filas_vacias"] == 1


def test_detectar_columnas_vacias():
    datos = crear_datos_prueba()

    diagnostico = diagnosticar_datos(datos)

    assert diagnostico["columnas_vacias"] == 1


def test_detectar_duplicados():
    datos = crear_datos_prueba()

    diagnostico = diagnosticar_datos(datos)

    assert diagnostico["filas_duplicadas"] == 1


def test_contar_valores_ausentes():
    datos = crear_datos_prueba()

    diagnostico = diagnosticar_datos(datos)

    assert diagnostico["detalle_columnas"]["PIB"]["valores_vacios"] == 1


def test_identificar_tipo_dato():
    datos = crear_datos_prueba()

    diagnostico = diagnosticar_datos(datos)

    assert diagnostico["detalle_columnas"]["Pais"]["tipo"] == "str"
