
import pandas as pd
import pytest

from econolab.data_engine.importador import importar_archivo


def test_importar_csv(tmp_path):
    archivo = tmp_path / "datos.csv"

    pd.DataFrame({
        "Pais": ["España", "Francia"],
        "PIB": [100, 200]
    }).to_csv(archivo, index=False)

    resultado = importar_archivo(archivo)

    assert resultado["nombre"] == "datos.csv"
    assert resultado["filas"] == 2
    assert resultado["columnas"] == 2


def test_importar_excel(tmp_path):
    archivo = tmp_path / "datos.xlsx"

    pd.DataFrame({
        "Pais": ["España", "Francia"],
        "PIB": [100, 200]
    }).to_excel(archivo, index=False)

    resultado = importar_archivo(archivo)

    assert resultado["nombre"] == "datos.xlsx"
    assert resultado["filas"] == 2
    assert resultado["columnas"] == 2


def test_archivo_inexistente(tmp_path):
    archivo = tmp_path / "inexistente.csv"

    with pytest.raises(FileNotFoundError):
        importar_archivo(archivo)


def test_formato_no_compatible(tmp_path):
    archivo = tmp_path / "datos.txt"
    archivo.write_text("datos de prueba")

    with pytest.raises(ValueError):
        importar_archivo(archivo)
