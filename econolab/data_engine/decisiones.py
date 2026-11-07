
class GestorDecisiones:

    ESTADOS_VALIDOS = {
        "pendiente",
        "aceptada",
        "rechazada",
        "pospuesta",
        "ejecutada",
        "obsoleta"
    }

    def __init__(self, recomendaciones):
        self.decisiones = {}
        self.siguiente_id = 1

        self.agregar_recomendaciones(recomendaciones)

    def obtener_version_vigente(self, problema):
        """
        Devuelve la última versión de un problema si sigue vigente.

        Si no existe o la última versión está obsoleta,
        devuelve None.
        """

        versiones = [
            decision
            for decision in self.decisiones.values()
            if decision["recomendacion"]["problema"] == problema
        ]

        if not versiones:
            return None

        ultima_version = max(
            versiones,
            key=lambda decision: decision["version"]
        )

        if ultima_version["estado"] == "obsoleta":
            return None

        return ultima_version

    def _recomendaciones_equivalentes(self, anterior, nueva):
        """"
        Comprueba si dos recomendaciones tienen el mismo contenido.
        """
        campos_comparables = (
            "problema",
            "cantidad",
            "gravedad",
            "accion",
            "automatico"
        )

        return all(
            anterior.get(campo) == nueva.get(campo)
            for campo in campos_comparables
        )

    def registrar_recomendacion(self, recomendacion):
        """
        Registra una recomendación nueva o una nueva versión
        de un problema existente.

        Si el contenido cambia, la versión anterior queda obsoleta.
        """

        problema = recomendacion["problema"]

        ultima_version = self.obtener_version_vigente(problema)

        # Si existe una versión vigente y el contenido no cambia,
        # conservamos su ID.
        if ultima_version is not None:

            if self._recomendaciones_equivalentes(
                ultima_version["recomendacion"],
                recomendacion
            ):
                return ultima_version["id"]

            # El contenido ha cambiado.
            # Invalidamos la versión anterior.
            if ultima_version["estado"] in (
                "pendiente",
                "aceptada",
                "pospuesta"
            ):
                self.marcar_obsoleta(ultima_version["id"])

            nueva_version = ultima_version["version"] + 1

        else:
            # Recuperamos la última versión histórica del problema.
            versiones_historicas = [
                decision
                for decision in self.decisiones.values()
                if decision["recomendacion"]["problema"] == problema
            ]

            if versiones_historicas:
                nueva_version = max(
                    decision["version"]
                    for decision in versiones_historicas
                ) + 1
            else:
                nueva_version = 1

        identificador = self.siguiente_id

        self.decisiones[identificador] = {
            "id": identificador,
            "version": nueva_version,
            "recomendacion": recomendacion.copy(),
            "estado": "pendiente"
        }

        self.siguiente_id += 1

        return identificador

    def agregar_recomendaciones(self, recomendaciones):
        """
        Incorpora recomendaciones nuevas sin eliminar las existentes
        las decisiones anteriores ni reutilizar IDs.
        """

        nuevos_ids = []

        for recomendacion in recomendaciones:
            identificador = self.siguiente_id
            self.decisiones[identificador] = {
                "id": identificador,
                "version": 1,
                "recomendacion": recomendacion.copy(),
                "estado": "pendiente"
            }

            nuevos_ids.append(identificador)
            self.siguiente_id += 1

        return nuevos_ids

    def _cambiar_estado(self, identificador, nuevo_estado):

        if identificador not in self.decisiones:
            raise KeyError(
                f"No existe la recomendación con ID {identificador}"
            )

        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError("Estado no válido.")

        self.decisiones[identificador]["estado"] = nuevo_estado

    def aceptar(self, identificador):

        self._cambiar_estado(identificador, "aceptada")

    def rechazar(self, identificador):

        self._cambiar_estado(identificador, "rechazada")

    def posponer(self, identificador):

        self._cambiar_estado(identificador, "pospuesta")

    def obtener_decisiones(self):

        return [
            {
                "id": decision["id"],
                "version": decision["version"],
                "recomendacion": decision["recomendacion"].copy(),
                "estado": decision["estado"]
            }
            for decision in self.decisiones.values()
        ]

    def obtener_decision(self, identificador):
        """
        Devuelve una decision concreta a partir de su ID.
        """
        if identificador not in self.decisiones:
            raise KeyError(
                f"No existe la recomendación con ID {identificador}"
            )

        decision = self.decisiones[identificador]
        return {
            "id": decision["id"],
            "version": decision["version"],
            "recomendacion": decision["recomendacion"].copy(),
            "estado": decision["estado"]
        }

    def marcar_ejecutada(self, identificador):

        if identificador not in self.decisiones:
            raise KeyError(
                f"No existe la recomendación con ID {identificador}"
            )
        if self.decisiones[identificador]["estado"] != "aceptada":
            raise ValueError(
                "Solo se puede marcar como ejecutada una recomendación aceptada."
            )
        self.decisiones[identificador]["estado"] = "ejecutada"

    def marcar_obsoleta(self, identificador):
        """
        Marca como obsoleta una recomendacion que ya no es aplicable.
        """

        if identificador not in self.decisiones:
            raise KeyError(
                f"No existe la recomendación con ID {identificador}"
            )
        estado_actual = self.decisiones[identificador]["estado"]

        if estado_actual not in ("pendiente", "aceptada", "pospuesta"):
            raise ValueError(
                f"Solo se puede marcar como obsoleta una recomendación "
                f"con estado: {estado_actual}"
            )

        self.decisiones[identificador]["estado"] = "obsoleta"
