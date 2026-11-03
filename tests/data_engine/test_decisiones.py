
import pytest
from econolab.data_engine.decisiones import GestorDecisiones


@pytest.fixture
def gestor():

    recomendaciones = [
        {
            "problema": "Filas duplicadas",
            "cantidad": 5,
            "gravedad": "Media",
            "accion": "Revisar registros duplicados",
            "automatico": False
        },
        {
            "problema": "Valores ausentes en PIB",
            "cantidad": 3,
            "gravedad": "Media",
            "accion": "Revisar valores ausentes",
            "automatico": False
        }
    ]

    return GestorDecisiones(recomendaciones)


def test_recomendaciones_inician_pendientes(gestor):

    decisiones = gestor.obtener_decisiones()

    assert len(decisiones) == 2
    assert all(
        decision["estado"] == "pendiente"
        for decision in decisiones
    )


def test_aceptar_recomendacion(gestor):

    gestor.aceptar(1)

    decisiones = gestor.obtener_decisiones()

    assert decisiones[0]["estado"] == "aceptada"


def test_rechazar_recomendacion(gestor):

    gestor.rechazar(1)

    decisiones = gestor.obtener_decisiones()

    assert decisiones[0]["estado"] == "rechazada"


def test_posponer_recomendacion(gestor):

    gestor.posponer(1)

    decisiones = gestor.obtener_decisiones()

    assert decisiones[0]["estado"] == "pospuesta"


def test_revisar_recomendacion_pospuesta(gestor):

    gestor.posponer(1)
    gestor.aceptar(1)

    decisiones = gestor.obtener_decisiones()

    assert decisiones[0]["estado"] == "aceptada"


def test_identificador_inexistente(gestor):

    with pytest.raises(KeyError):
        gestor.aceptar(99)

def test_obtener_decision_por_id():
    recomendaciones = [
        {"problema": "Filas duplicadas"}
    ]

    gestor = GestorDecisiones(recomendaciones)

    decision = gestor.obtener_decision(1)

    assert decision["id"] == 1
    assert decision["recomendacion"]["problema"] == "Filas duplicadas"
    assert decision["estado"] == "pendiente"


def test_obtener_decision_id_inexistente():
    gestor = GestorDecisiones([])

    with pytest.raises(KeyError):
        gestor.obtener_decision(99)


def test_obtener_decision_no_modifica_estado_interno():
    gestor = GestorDecisiones([
        {"problema": "Filas duplicadas"}
    ])

    decision = gestor.obtener_decision(1)
    decision["estado"] = "ejecutada"

    assert gestor.obtener_decision(1)["estado"] == "pendiente"