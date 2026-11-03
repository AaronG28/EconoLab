
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
