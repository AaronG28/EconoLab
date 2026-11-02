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

def test_previsualizar_duplicados_no_modifica_datos():

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    sesion = SesionLimpieza(datos)

    resultado = sesion.previsualizar_operacion(
        "eliminar_duplicados"
    )

    assert resultado["filas_antes"] == 3
    assert resultado["filas_despues"] == 2
    assert len(sesion.actual) == 3


def test_previsualizar_no_modifica_historial():

    datos = pd.DataFrame({
        "Pais": ["España", "Francia"],
        "PIB": [100, 200]
    })

    sesion = SesionLimpieza(datos)

    sesion.previsualizar_operacion("eliminar_duplicados")

    assert len(sesion.historial) == 0
    assert len(sesion.registro) == 0


def test_previsualizar_columnas_vacias():

    datos = pd.DataFrame({
        "Pais": ["España", "Francia"],
        "PIB": [100, 200],
        "Vacia": [None, None]
    })

    sesion = SesionLimpieza(datos)

    resultado = sesion.previsualizar_operacion(
        "eliminar_columnas_vacias"
    )

    assert resultado["columnas_antes"] == 3
    assert resultado["columnas_despues"] == 2
    assert len(sesion.actual.columns) == 3


def test_previsualizar_nombres_duplicados():

    datos = pd.DataFrame({
        " Pais": [1, 2],
        "Pais ": [3, 4]
    })

    sesion = SesionLimpieza(datos)

    resultado = sesion.previsualizar_operacion(
        "normalizar_nombres_columnas"
    )

    assert resultado["valido"] is False
    assert list(sesion.actual.columns) == [" Pais", "Pais "]