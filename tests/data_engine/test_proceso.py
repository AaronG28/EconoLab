
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

    # Comprobar que las recomendaciones resueltas queden obsoletas despues de la limpieza
    decision = proceso.obtener_decisiones()

    assert len(decision) == 3

    assert all(
        decision["estado"] == "obsoleta"
        for decision in decision
    )

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

def test_no_ejecutar_version_aceptada_obsoleta(tmp_path):

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    proceso.aceptar_recomendacion(1)

    proceso.sesion.actual = pd.concat(
        [
            proceso.sesion.actual,
            proceso.sesion.actual.iloc[[0]]
        ],
        ignore_index=True
    )

    proceso.actualizar_analisis()

    decision_anterior = proceso.gestor_decisiones.obtener_decision(1)

    assert decision_anterior["estado"] == "obsoleta"

    proceso.ejecutar_recomendaciones_aceptadas()

    assert len(proceso.sesion.actual) == 4

    decision_nueva = proceso.gestor_decisiones.obtener_decision(2)

    assert decision_nueva["estado"] == "pendiente"


def test_no_ejecutar_recomendacion_aceptada_ya_resuelta(tmp_path):

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    # 1. Aceptar la recomendación de eliminar duplicados
    proceso.aceptar_recomendacion(1)

    # 2. Resolver el problema por otra vía
    proceso.sesion.eliminar_duplicados()

    # 3. Actualizar el análisis
    proceso.actualizar_analisis()

    # 4. Comprobar que la recomendación anterior es obsoleta
    decision = proceso.gestor_decisiones.obtener_decision(1)

    assert decision["estado"] == "obsoleta"

    # 5. Intentar ejecutar las recomendaciones aceptadas
    mensajes = proceso.ejecutar_recomendaciones_aceptadas()

    # 6. Comprobar que no se vuelve a ejecutar la limpieza
    assert mensajes == []
    assert len(proceso.sesion.actual) == 2


def test_recomendacion_aceptada_se_ejecuta_una_sola_vez(tmp_path):

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    archivo = tmp_path / "datos.csv"
    datos.to_csv(archivo, index=False)

    proceso = ProcesoPreparacion(archivo)

    # Aceptar la recomendación de eliminar duplicados
    proceso.aceptar_recomendacion(1)

    # Primera ejecución
    mensajes_primera = proceso.ejecutar_recomendaciones_aceptadas()

    assert len(mensajes_primera) == 1
    assert len(proceso.sesion.actual) == 2

    # La recomendación debe quedar ejecutada
    decision = proceso.gestor_decisiones.obtener_decision(1)

    assert decision["estado"] == "ejecutada"

    # Segunda ejecución: no debe repetir la operación
    mensajes_segunda = proceso.ejecutar_recomendaciones_aceptadas()

    assert mensajes_segunda == []
    assert len(proceso.sesion.actual) == 2
