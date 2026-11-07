from econolab.data_engine.importador import importar_archivo
from econolab.data_engine.diagnostico import diagnosticar_datos
from econolab.data_engine.recomendaciones import generar_recomendaciones
from econolab.data_engine.limpieza import SesionLimpieza
from econolab.data_engine.decisiones import GestorDecisiones


OPERACIONES_DISPONIBLES = {
    "Filas completamente vacías": "eliminar_filas_vacias",
    "Columnas completamente vacías": "eliminar_columnas_vacias",
    "Espacios en nombres de columnas": "normalizar_nombres_columnas",
    "Filas duplicadas": "eliminar_duplicados",
}


class ProcesoPreparacion:

    def __init__(self, ruta):

        self.archivo = importar_archivo(ruta)
        self.sesion = SesionLimpieza(self.archivo["datos"])

        # Inicializar el gestor antes del primer análisis
        self.gestor_decisiones = GestorDecisiones([])

        # Registrar los problemas del análisis anterior
        self._problemas_anteriores = set()

        # Generar el diagnóstico y las recomendaciones iniciales
        self.actualizar_analisis()

    def actualizar_analisis(self):

        self.diagnostico = diagnosticar_datos(
            self.sesion.actual
        )

        self.recomendaciones = generar_recomendaciones(
            self.sesion.actual,
            self.diagnostico,
        )

        problemas_actuales = {
            recomendacion["problema"]
            for recomendacion in self.recomendaciones
        }

        # 1. Marcar como obsoletas las recomendaciones activas
        # cuyos problemas han desaparecido
        for decision in self.gestor_decisiones.obtener_decisiones():

            problema = decision["recomendacion"]["problema"]

            if (
                decision["estado"]
                in ("pendiente", "aceptada", "pospuesta")
                and problema not in problemas_actuales
            ):
                self.gestor_decisiones.marcar_obsoleta(
                    decision["id"]
                )

        # 2. Registrar las recomendaciones actuales
        # El gestor decide si conserva la versión o crea otra
        for recomendacion in self.recomendaciones:

            self.gestor_decisiones.registrar_recomendacion(
                recomendacion
            )

        self._problemas_anteriores = problemas_actuales.copy()

    def obtener_estado(self):

        return {
            "archivo": self.archivo["nombre"],
            "filas": len(self.sesion.actual),
            "columnas": len(self.sesion.actual.columns),
            "datos": self.sesion.actual.copy(deep=True),
            "diagnostico": self.diagnostico,
            "recomendaciones": self.recomendaciones,
        }

    def aplicar_automaticas(self):

        mensajes = []

        # Trabajar sobre una copia de las recomendaciones
        recomendaciones = self.recomendaciones.copy()

        for recomendacion in recomendaciones:

            if not recomendacion["automatico"]:
                continue

            problema = recomendacion["problema"]

            operacion = OPERACIONES_DISPONIBLES.get(
                problema
            )

            if operacion is None:
                continue

            # Crear un punto de restauración
            datos_anteriores = self.sesion.actual.copy(
                deep=True
            )

            historial_anterior = len(
                self.sesion.historial
            )

            registro_anterior = len(
                self.sesion.registro
            )

            # Identificar el metodo de limpieza
            metodo = getattr(self.sesion, operacion)

            try:
                mensaje_operacion = metodo()

            except Exception:

                # Restaurar los datos originales
                self.sesion.actual = datos_anteriores

                # Restaurar el historial
                del self.sesion.historial[
                    historial_anterior:
                ]

                # Restaurar el registro de operaciones
                del self.sesion.registro[
                    registro_anterior:
                ]

                # Propagar el error para que pueda ser detectado
                raise

            # Registrar el resultado de la operacion
            mensajes.append(
                mensaje_operacion
            )

        # Volver a analizar despues de los cambion
        self.actualizar_analisis()

        return mensajes

    def aceptar_recomendacion(self, identificador):

        self.gestor_decisiones.aceptar(
            identificador
        )

    def rechazar_recomendacion(self, identificador):

        self.gestor_decisiones.rechazar(
            identificador
        )

    def posponer_recomendacion(self, identificador):

        self.gestor_decisiones.posponer(
            identificador
        )

    def obtener_decisiones(self):

        return self.gestor_decisiones.obtener_decisiones()

    def ejecutar_recomendaciones_aceptadas(self):

        mensajes = []

        decisiones = self.obtener_decisiones()

        for decision in decisiones:

            if decision["estado"] != "aceptada":
                continue

            identificador = decision["id"]

            problema = decision["recomendacion"]["problema"]

            # Comprobar que la decisión corresponde
            # a la última versión vigente
            version_vigente = (
                self.gestor_decisiones.obtener_version_vigente(
                    problema
                )
            )

            if (
                version_vigente is None
                or version_vigente["id"] != identificador
            ):
                continue

            # Identificar la operación correspondiente
            operacion = OPERACIONES_DISPONIBLES.get(
                problema
            )

            # No marcar como ejecutada una operación
            # que todavía no está implementada
            if operacion is None:

                mensajes.append(
                    f"No existe una operación implementada "
                    f"para: {problema}"
                )

                continue

            # Crear un punto de restauración
            datos_anteriores = self.sesion.actual.copy(
                deep=True
            )

            historial_anterior = len(
                self.sesion.historial
            )

            registro_anterior = len(
                self.sesion.registro
            )

            # Ejecutar la operación con protección ante errores
            metodo = getattr(self.sesion, operacion)

            try:

                mensaje_operacion = metodo()

            except Exception:

                # Restaurar los datos originales
                self.sesion.actual = datos_anteriores

                # Restaurar el historial
                del self.sesion.historial[
                    historial_anterior:
                ]

                # Restaurar el registro de operaciones
                del self.sesion.registro[
                    registro_anterior:
                ]

                # Propagar el error para que pueda ser detectado
                raise

            # Registrar la ejecución únicamente si todo salió bien
            self.gestor_decisiones.marcar_ejecutada(
                identificador
            )

            mensajes.append(
                mensaje_operacion
            )

        # Actualizar el diagnóstico y las recomendaciones
        self.actualizar_analisis()

        return mensajes

    def previsualizar_recomendacion(self, identificador):

        """
        Previsualiza una recomendación concreta mediante su ID.
        No modifica los datos ni ejecuta la operación.
        """

        decision = (
            self.gestor_decisiones.obtener_decision(
                identificador
            )
        )

        # Comprobar el estado de la recomendación
        if decision["estado"] not in (
            "pendiente",
            "aceptada",
        ):

            raise ValueError(
                "Solo se pueden previsualizar recomendaciones "
                "pendientes o aceptadas."
            )

        problema = decision["recomendacion"]["problema"]

        # Identificar la operación
        operacion = OPERACIONES_DISPONIBLES.get(
            problema
        )

        if operacion is None:

            return {
                "valido": False,
                "mensaje": (
                    f"No existe una operación implementada "
                    f"para: {problema}"
                ),
            }

        # Generar la previsualización sin modificar los datos
        return self.sesion.previsualizar_operacion(
            operacion
        )
