
import pandas as pd

from econolab.data_engine.proceso import ProcesoPreparacion


def crear_archivo_prueba(tmp_path):

    archivo = tmp_path / "datos.csv"

    datos = pd.DataFrame({
        "Pais": ["España", "Francia", "España"],
        "PIB": [100, 200, 100]
    })

    datos.to_csv(archivo, index=False)

    return archivo


def test_ejecutar_recomendacion_aceptada(tmp_path):

    archivo = crear_archivo_prueba(tmp_path)

    proceso = ProcesoPreparacion(archivo)

    proceso.aceptar_recomendacion(1)

    proceso.ejecutar_recomendaciones_aceptadas()

    estado = proceso.obtener_estado()

    assert estado["filas"] == 2


def test_no_ejecutar_recomendacion_rechazada(tmp_path):

    archivo = crear_archivo_prueba(tmp_path)

    proceso = ProcesoPreparacion(archivo)

    proceso.rechazar_recomendacion(1)

    proceso.ejecutar_recomendaciones_aceptadas()

    estado = proceso.obtener_estado()

    assert estado["filas"] == 3


def test_no_ejecutar_recomendacion_pendiente(tmp_path):

    archivo = crear_archivo_prueba(tmp_path)

    proceso = ProcesoPreparacion(archivo)

    proceso.ejecutar_recomendaciones_aceptadas()

    estado = proceso.obtener_estado()

    assert estado["filas"] == 3


def test_no_ejecutar_dos_veces(tmp_path):

    archivo = crear_archivo_prueba(tmp_path)

    proceso = ProcesoPreparacion(archivo)

    proceso.aceptar_recomendacion(1)

    proceso.ejecutar_recomendaciones_aceptadas()

    proceso.ejecutar_recomendaciones_aceptadas()

    estado = proceso.obtener_estado()

    assert estado["filas"] == 2
