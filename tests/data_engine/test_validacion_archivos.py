import zipfile
import pytest

from econolab.security.validacion_archivos import validar_archivo


def crear_xlsx_valido(ruta):
    """Crea un XLSX mínimo para las pruebas."""

    with zipfile.ZipFile(ruta, "w") as archivo:
        archivo.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types></Types>'
        )

        archivo.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0"?><workbook></workbook>'
        )


def test_aceptar_csv_valido(tmp_path):

    archivo = tmp_path / "datos.csv"
    archivo.write_text(
        "Pais,PIB\nEspaña,100\nFrancia,200\n",
        encoding="utf-8"
    )

    assert validar_archivo(archivo) is True


def test_aceptar_xlsx_valido(tmp_path):

    archivo = tmp_path / "datos.xlsx"
    crear_xlsx_valido(archivo)

    assert validar_archivo(archivo) is True


def test_rechazar_archivo_inexistente(tmp_path):

    archivo = tmp_path / "inexistente.csv"

    with pytest.raises(FileNotFoundError):
        validar_archivo(archivo)


def test_rechazar_extension_no_permitida(tmp_path):

    archivo = tmp_path / "programa.exe"
    archivo.write_bytes(b"contenido")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_archivo_vacio(tmp_path):

    archivo = tmp_path / "datos.csv"
    archivo.write_bytes(b"")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_csv_con_bytes_nulos(tmp_path):

    archivo = tmp_path / "datos.csv"
    archivo.write_bytes(b"Pais,PIB\nEspa\x00na,100")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_csv_con_codificacion_incorrecta(tmp_path):

    archivo = tmp_path / "datos.csv"
    archivo.write_bytes(b"Pais,PIB\nEspa\xf1a,100")

    with pytest.raises(ValueError, match="Codificación no compatible"):
        validar_archivo(archivo)

def test_rechazar_xlsx_que_no_es_zip(tmp_path):

    archivo = tmp_path / "datos.xlsx"
    archivo.write_bytes(b"Esto no es un archivo Excel")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_xlsx_sin_estructura_excel(tmp_path):

    archivo = tmp_path / "datos.xlsx"

    with zipfile.ZipFile(archivo, "w") as contenido:
        contenido.writestr("documento.txt", "contenido")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_xls_con_firma_invalida(tmp_path):

    archivo = tmp_path / "datos.xls"
    archivo.write_bytes(b"Esto no es un XLS")

    with pytest.raises(ValueError):
        validar_archivo(archivo)


def test_rechazar_archivo_superior_al_limite(tmp_path, monkeypatch):

    import econolab.security.validacion_archivos as seguridad

    archivo = tmp_path / "datos.csv"
    archivo.write_text("Pais,PIB\nEspaña,100", encoding="utf-8")

    monkeypatch.setattr(seguridad, "TAMANO_MAXIMO", 5)

    with pytest.raises(ValueError):
        validar_archivo(archivo)

def test_detectar_codificacion_incorrecta_al_final(tmp_path):

    archivo = tmp_path / "codificacion_tardia.csv"

    contenido = b"Pais,PIB\n" + b"A" * 65536 + b"\xff"
    archivo.write_bytes(contenido)

    with pytest.raises(ValueError, match="Codificación no compatible"):
        validar_archivo(archivo)