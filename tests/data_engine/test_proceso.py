
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
