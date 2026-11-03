
class GestorDecisiones:

    ESTADOS_VALIDOS = {
        "pendiente",
        "aceptada",
        "rechazada",
        "pospuesta",
        "ejecutada"
    }

    def __init__(self, recomendaciones):

        self.decisiones = {}

        for identificador, recomendacion in enumerate(
            recomendaciones, start=1
        ):

            self.decisiones[identificador] = {
                "id": identificador,
                "recomendacion": recomendacion.copy(),
                "estado": "pendiente"
            }

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
