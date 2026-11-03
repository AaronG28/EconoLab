
import pandas as pd

from econolab.data_engine.proceso import ProcesoPreparacion


def test_proceso_completo(tmp_path):

    # Crear un archivo CSV de prueba
    archivo = tmp_path / "datos.csv"

    datos = pd.DataFrame({
        " Pais ": ["España", "Francia", "Italia", None],
        "PIB": [100, 200, 300, None],
        "columna_vacia": [None, None, None, None]
    })

    datos.to_csv(archivo, index=False)

    # Iniciar el proceso completo
    proceso = ProcesoPreparacion(archivo)

    # Comprobar el diagnóstico inicial
    estado_inicial = proceso.obtener_estado()

    assert estado_inicial["filas"] == 4
    assert estado_inicial["columnas"] == 3
    assert len(estado_inicial["recomendaciones"]) > 0

    # Aplicar las operaciones automáticas
    mensajes = proceso.aplicar_automaticas()

    # Comprobar el resultado
    estado_final = proceso.obtener_estado()

    assert estado_final["filas"] == 3
    assert estado_final["columnas"] == 2
    assert "Pais" in estado_final["datos"].columns
    assert len(mensajes) > 0

    # Comprobar que el archivo original no fue modificado
    assert proceso.sesion.original.equals(
        pd.read_csv(archivo)
    )

def test_previsualizar_recomendacion_no_modifica_datos(tmp_path):

    import pandas as pd

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    resultado = proceso.previsualizar_recomendacion(1)

    # Comprobamos la previsualización
    assert resultado["filas_antes"] == 3
    assert resultado["filas_despues"] == 2

    # Comprobamos que los datos reales no han cambiado
    estado = proceso.obtener_estado()

    assert estado["filas"] == 3

def test_no_previsualizar_recomendacion_rechazada(tmp_path):

    import pytest

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    proceso.rechazar_recomendacion(1)

    with pytest.raises(ValueError):
        proceso.previsualizar_recomendacion(1)

def test_recomendacion_obsoleta_y_nuevo_id(tmp_path):

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    # Aceptar la recomendación inicial
    proceso.aceptar_recomendacion(1)

    # Resolver el problema de los duplicados
    proceso.sesion.eliminar_duplicados()
    proceso.actualizar_analisis()

    # Comprobar que la recomendación anterior es obsoleta
    decision_anterior = proceso.gestor_decisiones.obtener_decision(1)

    assert decision_anterior["estado"] == "obsoleta"

    # Volver a introducir una fila duplicada
    proceso.sesion.actual = pd.concat(
        [proceso.sesion.actual, proceso.sesion.actual.iloc[[0]]],
        ignore_index=True
    )

    proceso.actualizar_analisis()

    # Comprobar que se crea una recomendación nueva
    decisiones = proceso.obtener_decisiones()

    assert len(decisiones) == 2
    assert decisiones[0]["id"] == 1
    assert decisiones[0]["estado"] == "obsoleta"
    assert decisiones[1]["id"] == 2
    assert decisiones[1]["estado"] == "pendiente"