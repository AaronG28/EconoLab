import pandas as pd

from econolab.data_engine.limpieza import SesionLimpieza


def crear_datos_prueba():
    return pd.DataFrame({
        " País ": ["España", "Francia", None],
        "PIB": [100, 200, None],
        "columna_vacia": [None, None, None]
    })


def test_eliminar_filas_vacias():
    datos = crear_datos_prueba()
    sesion = SesionLimpieza(datos)

    sesion.eliminar_filas_vacias()

    assert len(sesion.actual) == 2


def test_eliminar_columnas_vacias():
    datos = crear_datos_prueba()
    sesion = SesionLimpieza(datos)

    sesion.eliminar_columnas_vacias()

    assert "columna_vacia" not in sesion.actual.columns


def test_normalizar_nombres():
    datos = crear_datos_prueba()
    sesion = SesionLimpieza(datos)

    sesion.normalizar_nombres_columnas()

    assert "País" in sesion.actual.columns


def test_deshacer_recupera_estado_original():
    datos = crear_datos_prueba()
    sesion = SesionLimpieza(datos)

    sesion.eliminar_filas_vacias()
    sesion.eliminar_columnas_vacias()
    sesion.normalizar_nombres_columnas()

    sesion.deshacer()
    sesion.deshacer()
    sesion.deshacer()

    assert sesion.actual.equals(datos)


def test_original_no_se_modifica():
    datos = crear_datos_prueba()
    original = datos.copy(deep=True)

    sesion = SesionLimpieza(datos)

    sesion.eliminar_filas_vacias()
    sesion.eliminar_columnas_vacias()

    assert datos.equals(original)