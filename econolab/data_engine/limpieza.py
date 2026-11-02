class SesionLimpieza:

    def __init__(self, datos):

        # Conservamos una copia de los datos originales
        self.original = datos.copy(deep=True)

        # Trabajamos sobre otra copia
        self.actual = datos.copy(deep=True)

        # Historial de estados anteriores
        self.historial = []

        # Registro de operaciones
        self.registro = []

    def _guardar_estado(self, operacion):

        self.historial.append(self.actual.copy(deep=True))

        self.registro.append({
            "operacion": operacion
        })

    def eliminar_filas_vacias(self):

        cantidad = int(self.actual.isna().all(axis=1).sum())

        if cantidad == 0:
            return "No hay filas vacías."

        self._guardar_estado("Eliminar filas vacías")

        self.actual = self.actual.dropna(how="all").copy()

        return f"Se eliminaron {cantidad} filas vacías."

    def eliminar_columnas_vacias(self):

        cantidad = int(self.actual.isna().all(axis=0).sum())

        if cantidad == 0:
            return "No hay columnas vacías."

        self._guardar_estado("Eliminar columnas vacías")

        self.actual = self.actual.dropna(axis=1, how="all").copy()

        return f"Se eliminaron {cantidad} columnas vacías."

    def normalizar_nombres_columnas(self):

        nuevos_nombres = [
            columna.strip() if isinstance(columna, str) else columna
            for columna in self.actual.columns
        ]

        if nuevos_nombres == list(self.actual.columns):
            return "Los nombres ya están normalizados."

        if len(set(nuevos_nombres)) != len(nuevos_nombres):
            return "No se puede aplicar: produciría nombres duplicados."

        self._guardar_estado("Normalizar nombres de columnas")

        self.actual.columns = nuevos_nombres

        return "Nombres de columnas normalizados."

    def eliminar_duplicados(self):
        cantidad = int(self.actual.duplicated().sum())

        if cantidad == 0:
            return "No hay filas duplicadas."
        self._guardar_estado("Eliminar filas duplicadas")
        self.actual = self.actual.drop_duplicates().copy()

        return f"Se eliminaron {cantidad} filas duplicadas."

    def previsualizar_operacion(self, operacion):

        # Trabajamos sobre una copia temporal
        datos_previos = self.actual.copy(deep=True)

        # Preparamos el resultado sin modificar los datos actuales
        if operacion == "eliminar_filas_vacias":

            datos_nuevos = datos_previos.dropna(how="all").copy()

        elif operacion == "eliminar_columnas_vacias":

            datos_nuevos = datos_previos.dropna(
                axis=1,
                how="all"
            ).copy()

        elif operacion == "normalizar_nombres_columnas":

            nuevos_nombres = [
                columna.strip() if isinstance(columna, str) else columna
                for columna in datos_previos.columns
            ]

            if len(set(nuevos_nombres)) != len(nuevos_nombres):
                return {
                    "valido": False,
                    "mensaje": "La operación produciría nombres duplicados."
                }

            datos_nuevos = datos_previos.copy()
            datos_nuevos.columns = nuevos_nombres

        elif operacion == "eliminar_duplicados":

            datos_nuevos = datos_previos.drop_duplicates().copy()

        else:

            raise ValueError(
                f"Operación no reconocida: {operacion}"
            )

        # Devolvemos información comparativa
        return {
            "valido": True,
            "operacion": operacion,
            "filas_antes": len(datos_previos),
            "filas_despues": len(datos_nuevos),
            "columnas_antes": len(datos_previos.columns),
            "columnas_despues": len(datos_nuevos.columns),
            "datos_antes": datos_previos,
            "datos_despues": datos_nuevos
        }

    def deshacer(self):

        if not self.historial:
            return "No hay operaciones para deshacer."

        self.actual = self.historial.pop()

        operacion = self.registro.pop()

        return f"Operación deshecha: {operacion['operacion']}"

    def mostrar_registro(self):

        return self.registro