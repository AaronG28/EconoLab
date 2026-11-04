from pathlib import Path
import zipfile
import codecs

TAMANO_MAXIMO = 50 * 1024 * 1024  # 50 MB

TAMANO_DESCOMPRIMIDO_MAXIMO = 250 * 1024 * 1024  # 250 MB

TAMANO_ELEMENTO_MAXIMO = 100 * 1024 * 1024  # 100 MB

NUMERO_ELEMENTOS_MAXIMO = 5000

RATIO_COMPRESION_MAXIMO = 100


def validar_archivo(ruta):
    """
    Valida un archivo antes de su importación.

    Formatos admitidos:
    - CSV
    - XLSX
    - XLS
    """

    ruta = Path(ruta)

    # 1. Comprobar que el archivo existe
    if not ruta.exists():
        raise FileNotFoundError(
            "No se encuentra el archivo."
        )

    # 2. Comprobar que es un archivo regular
    if not ruta.is_file():
        raise ValueError(
            "La ruta indicada no corresponde a un archivo."
        )

    # 3. Comprobar la extensión
    extension = ruta.suffix.lower()

    extensiones_permitidas = {
        ".csv",
        ".xlsx",
        ".xls"
    }

    if extension not in extensiones_permitidas:
        raise ValueError(
            f"Formato no permitido: {extension}"
        )

    # 4. Comprobar el tamaño
    tamano = ruta.stat().st_size

    if tamano == 0:
        raise ValueError(
            "El archivo está vacío."
        )

    if tamano > TAMANO_MAXIMO:
        raise ValueError(
            "El archivo supera el tamaño máximo permitido de 50 MB."
        )

    # 5. Validar según el formato
    if extension == ".csv":
        _validar_csv(ruta)

    elif extension == ".xlsx":
        _validar_xlsx(ruta)

    elif extension == ".xls":
        _validar_xls(ruta)

    return True


def _validar_csv(ruta):
    """
    Comprueba que todo el CSV utiliza UTF-8 o UTF-8 con BOM.
    Lee el archivo por bloques para evitar cargarlo entero en memoria.
    """

    decoder = codecs.getincrementaldecoder("utf-8-sig")()

    try:
        with ruta.open("rb") as archivo:
            while bloque := archivo.read(65536):
                texto = decoder.decode(bloque, final=False)

                if "\x00" in texto:
                    raise ValueError(
                        "El archivo contiene bytes nulos y podría ser un archivo binario."
                    )

            texto_final = decoder.decode(b"", final=True)

            if "\x00" in texto_final:
                raise ValueError(
                    "El archivo contiene bytes nulos y podría ser un archivo binario."
                )

    except UnicodeDecodeError as error:
        raise ValueError(
            "Codificación no compatible: EconoLab admite actualmente "
            "archivos CSV en UTF-8. Convierte el archivo a UTF-8 "
            "y vuelve a subirlo."
        ) from error

def _validar_xlsx(ruta):
    """
    Comprueba la estructura básica del contenedor XLSX
    y aplica límites de descompresión.
    """

    if not zipfile.is_zipfile(ruta):
        raise ValueError(
            "El archivo XLSX no es un contenedor ZIP válido."
        )

    try:
        with zipfile.ZipFile(ruta) as archivo:

            elementos = archivo.infolist()

            # Limitar cantidad de elementos
            if len(elementos) > NUMERO_ELEMENTOS_MAXIMO:
                raise ValueError(
                    "El XLSX contiene demasiados elementos internos."
                )

            nombres = {
                elemento.filename
                for elemento in elementos
            }

            # Comprobar estructura básica de Excel
            elementos_requeridos = {
                "[Content_Types].xml",
                "xl/workbook.xml"
            }

            if not elementos_requeridos.issubset(nombres):
                raise ValueError(
                    "El XLSX no contiene la estructura básica de Excel."
                )

            tamano_total = 0

            for elemento in elementos:

                nombre = elemento.filename

                # Evitar rutas internas sospechosas
                partes = Path(nombre).parts

                if (
                    nombre.startswith("/")
                    or "\\" in nombre
                    or ".." in partes
                ):
                    raise ValueError(
                        "El XLSX contiene una ruta interna no permitida."
                    )

                tamano = elemento.file_size
                tamano_comprimido = elemento.compress_size

                # Limitar el tamaño de cada elemento
                if tamano > TAMANO_ELEMENTO_MAXIMO:
                    raise ValueError(
                        "Un elemento interno del XLSX supera el límite permitido."
                    )

                tamano_total += tamano

                # Limitar el tamaño total descomprimido
                if tamano_total > TAMANO_DESCOMPRIMIDO_MAXIMO:
                    raise ValueError(
                        "El XLSX supera el tamaño descomprimido máximo."
                    )

                # Detectar ratios de compresión extremos
                if tamano_comprimido == 0 and tamano > 0:
                    raise ValueError(
                        "El XLSX contiene un elemento con compresión sospechosa."
                    )

                if tamano_comprimido > 0:

                    ratio = tamano / tamano_comprimido

                    if ratio > RATIO_COMPRESION_MAXIMO:
                        raise ValueError(
                            "El XLSX presenta un ratio de compresión excesivo."
                        )

            # Comprobar integridad de los elementos ZIP
            elemento_corrupto = archivo.testzip()

            if elemento_corrupto is not None:
                raise ValueError(
                    "El XLSX contiene un elemento interno corrupto."
                )

    except zipfile.BadZipFile as error:
        raise ValueError(
            "El archivo XLSX está corrupto."
        ) from error


def _validar_xls(ruta):
    """
    Comprueba la firma binaria básica del formato XLS antiguo.
    """

    firma_xls = bytes.fromhex(
        "D0 CF 11 E0 A1 B1 1A E1"
    )

    with ruta.open("rb") as archivo:
        firma = archivo.read(8)

    if firma != firma_xls:
        raise ValueError(
            "El archivo no presenta la firma binaria esperada de XLS."
        )