def generar_recomendaciones(datos, diagnostico):

    recomendaciones = []

    # 1. Filas completamente vacías
    if diagnostico["filas_vacias"] > 0:
        recomendaciones.append({
            "problema": "Filas completamente vacías",
            "cantidad": diagnostico["filas_vacias"],
            "gravedad": "Baja",
            "accion": "Eliminar las filas completamente vacías",
            "automatico": True
        })

    # 2. Columnas completamente vacías
    if diagnostico["columnas_vacias"] > 0:
        recomendaciones.append({
            "problema": "Columnas completamente vacías",
            "cantidad": diagnostico["columnas_vacias"],
            "gravedad": "Baja",
            "accion": "Eliminar las columnas completamente vacías",
            "automatico": True
        })

    # 3. Filas duplicadas
    if diagnostico["filas_duplicadas"] > 0:
        recomendaciones.append({
            "problema": "Filas duplicadas",
            "cantidad": diagnostico["filas_duplicadas"],
            "gravedad": "Media",
            "accion": "Revisar los registros duplicados",
            "automatico": False
        })

    # 4. Espacios en nombres de columnas
    columnas_con_espacios = [
        columna for columna in datos.columns
        if columna != columna.strip()
    ]

    if columnas_con_espacios:
        recomendaciones.append({
            "problema": "Espacios en nombres de columnas",
            "cantidad": len(columnas_con_espacios),
            "gravedad": "Baja",
            "accion": "Eliminar espacios al inicio y al final de los nombres",
            "automatico": True
        })

    # 5. Valores ausentes por variable
    for columna, informacion in diagnostico["detalle_columnas"].items():

        #Ignorar columnas completamente vacias
        if datos[columna].isna().all():
            continue

        # Excluir filas completamente vacías del cálculo
        filas_con_datos = ~datos.isna().all(axis=1)

        valores_ausentes = int(
            datos.loc[filas_con_datos, columna].isna().sum()
        )

        if valores_ausentes > 0:

            recomendaciones.append({
                "problema": f"Valores ausentes en {columna}",
                "cantidad": valores_ausentes,
                "gravedad": "Media",
                "accion": "Revisar los valores ausentes antes de decidir cómo tratarlos",
                "automatico": False
            })


    return recomendaciones