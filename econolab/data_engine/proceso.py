

from econolab.data_engine.importador import importar_archivo
from econolab.data_engine.diagnostico import diagnosticar_datos
from econolab.data_engine.recomendaciones import generar_recomendaciones
from econolab.data_engine.limpieza import SesionLimpieza
from econolab.data_engine.decisiones import GestorDecisiones


OPERACIONES_DISPONIBLES = {
    "Filas completamente vacías": "eliminar_filas_vacias",
    "Columnas completamente vacías": "eliminar_columnas_vacias",
    "Espacios en nombres de columnas": "normalizar_nombres_columnas",
    "Filas duplicadas": "eliminar_duplicados"
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

        # Diagnosticar el estado actual
        self.diagnostico = diagnosticar_datos(
            self.sesion.actual
        )

        # Generar las recomendaciones actuales
        self.recomendaciones = generar_recomendaciones(
            self.sesion.actual,
            self.diagnostico
        )

        # Identificar los problemas que siguen presentes
        problemas_actuales = {
            recomendacion["problema"]
            for recomendacion in self.recomendaciones
        }

        # Marcar como obsoletas las recomendaciones que ya no son relevantes
        for decision in self.gestor_decisiones.obtener_decisiones():

            problema = decision["recomendacion"]["problema"]

            if (
                decision["estado"] in ("pendiente", "aceptada", "pospuesta")
                and problema not in problemas_actuales
            ):
                self.gestor_decisiones.marcar_obsoleta(
                    decision["id"])

        # Detectar únicamente problemas nuevos
        nuevas_recomendaciones = [
            recomendacion
            for recomendacion in self.recomendaciones
            if recomendacion["problema"] not in self._problemas_anteriores
        ]

        # Incorporar las nuevas recomendaciones al gestor
        self.gestor_decisiones.agregar_recomendaciones(
            nuevas_recomendaciones
        )

        # Actualizar los problemas detectados
        self._problemas_anteriores = problemas_actuales

    def obtener_estado(self):

        return {
            "archivo": self.archivo["nombre"],
            "filas": len(self.sesion.actual),
            "columnas": len(self.sesion.actual.columns),
            "datos": self.sesion.actual.copy(deep=True),
            "diagnostico": self.diagnostico,
            "recomendaciones": self.recomendaciones
        }

    def aplicar_automaticas(self):

        mensajes = []

        # Trabajar sobre una copia de las recomendaciones
        recomendaciones = self.recomendaciones.copy()

        for recomendacion in recomendaciones:

            if not recomendacion["automatico"]:
                continue

            problema = recomendacion["problema"]
            operacion = OPERACIONES_DISPONIBLES.get(problema)

            if operacion is None:
                continue

            metodo = getattr(self.sesion, operacion)
            mensaje = metodo()

            mensajes.append(mensaje)

        # Volver a analizar después de los cambios
        self.actualizar_analisis()

        return mensajes

    def aceptar_recomendacion(self, identificador):
        self.gestor_decisiones.aceptar(identificador)

    def rechazar_recomendacion(self, identificador):
        self.gestor_decisiones.rechazar(identificador)

    def posponer_recomendacion(self, identificador):
        self.gestor_decisiones.posponer(identificador)

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

            # Identificar la operación correspondiente
            operacion = OPERACIONES_DISPONIBLES.get(problema)

            # No marcar como ejecutada una operación no implementada
            if operacion is None:
                mensajes.append(
                    f"No existe una operación implementada para: {problema}"
                )
                continue

            # Ejecutar la operación
            metodo = getattr(self.sesion, operacion)
            mensaje = metodo()

            # Registrar la ejecución
            self.gestor_decisiones.marcar_ejecutada(identificador)

            mensajes.append(mensaje)

        # Actualizar el diagnóstico y las recomendaciones
        self.actualizar_analisis()

        return mensajes

    def previsualizar_recomendacion(self, identificador):

        """
        Previsualiza una recomendación concreta mediante su ID.
        No modifica los datos ni ejecuta la operación.
        """

        decision = self.gestor_decisiones.obtener_decision(
            identificador
        )

        # Comprobar el estado de la recomendación
        if decision["estado"] not in ("pendiente", "aceptada"):
            raise ValueError(
                "Solo se pueden previsualizar recomendaciones "
                "pendientes o aceptadas."
            )

        problema = decision["recomendacion"]["problema"]

        # Identificar la operación
        operacion = OPERACIONES_DISPONIBLES.get(problema)

        if operacion is None:
            return {
                "valido": False,
                "mensaje": (
                    f"No existe una operación implementada para: {problema}"
                )
            }

        # Generar la previsualización sin modificar los datos
        return self.sesion.previsualizar_operacion(operacion)
