
from econolab.data_engine.importador import importar_archivo
from econolab.data_engine.diagnostico import diagnosticar_datos
from econolab.data_engine.recomendaciones import generar_recomendaciones
from econolab.data_engine.limpieza import SesionLimpieza
from econolab.data_engine.decisiones import GestorDecisiones


class ProcesoPreparacion:

    def __init__(self, ruta):

        # 1. Importar el archivo
        self.archivo = importar_archivo(ruta)

        # 2. Crear una sesión de limpieza
        self.sesion = SesionLimpieza(
            self.archivo["datos"]
        )

        # 3. Analizar los datos iniciales
        self.actualizar_analisis()

        # 4. Crear un gestor de decisiones
        self.gestor_decisiones = GestorDecisiones(
            self.recomendaciones
        )

    def actualizar_analisis(self):

        # Diagnosticar el estado actual
        self.diagnostico = diagnosticar_datos(
            self.sesion.actual
        )

        # Generar recomendaciones
        self.recomendaciones = generar_recomendaciones(
            self.sesion.actual,
            self.diagnostico
        )

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

        # Trabajamos sobre una copia de las recomendaciones
        recomendaciones = self.recomendaciones.copy()

        for recomendacion in recomendaciones:

            if not recomendacion["automatico"]:
                continue

            problema = recomendacion["problema"]

            if problema == "Filas completamente vacías":

                mensaje = self.sesion.eliminar_filas_vacias()

            elif problema == "Columnas completamente vacías":

                mensaje = self.sesion.eliminar_columnas_vacias()

            elif problema == "Espacios en nombres de columnas":

                mensaje = self.sesion.normalizar_nombres_columnas()

            else:
                continue

            mensajes.append(mensaje)

        # Volver a analizar los datos después de los cambios
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

            if problema == "Filas completamente vacías":
                mensaje = self.sesion.eliminar_filas_vacias()
            elif problema == "Columnas completamente vacías":
                mensaje = self.sesion.eliminar_columnas_vacias()
            elif problema == "Espacios en nombres de columnas":
                mensaje = self.sesion.normalizar_nombres_columnas()
            elif problema == "Filas duplicadas":
                mensaje = self.sesion.eliminar_duplicados()
            else:
                mensajes.append(
                    f"No existe una operacion implemetada para: {problema}"
                )

            # Registrar la operación como ejecutada
            self.gestor_decisiones.marcar_ejecutada(identificador)

            mensajes.append(mensaje)

        # Actaulizar el diagnostico y las recomendaciones
        self.actualizar_analisis()

        return mensajes