
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

def test_agregar_recomendaciones_conserva_ids():
    gestor = GestorDecisiones([
        {"problema": "Filas duplicadas"}
    ])

    nuevos_ids = gestor.agregar_recomendaciones([
        {"problema": "Valores ausentes"},
        {"problema": "Columnas vacías"}
    ])

    assert nuevos_ids == [2, 3]

    decisiones = gestor.obtener_decisiones()

    assert len(decisiones) == 3
    assert decisiones[0]["estado"] == "pendiente"
    assert decisiones[1]["recomendacion"]["problema"] == "Valores ausentes"
    assert decisiones[2]["recomendacion"]["problema"] == "Columnas vacías"


def test_agregar_recomendaciones_no_reutiliza_ids():
    gestor = GestorDecisiones([
        {"problema": "Filas duplicadas"}
    ])

    gestor.aceptar(1)

    gestor.agregar_recomendaciones([
        {"problema": "Valores ausentes"}
    ])

    assert gestor.obtener_decision(1)["estado"] == "aceptada"
    assert gestor.obtener_decision(2)["estado"] == "pendiente"

def test_marcar_obsoleta_recomendacion_pendiente():
    gestor = GestorDecisiones([
        {"problema": "Filas duplicadas"}
    ])

    gestor.marcar_obsoleta(1)

    assert gestor.obtener_decision(1)["estado"] == "obsoleta"


def test_marcar_obsoleta_no_permite_decision_rechazada():
    gestor = GestorDecisiones([
        {"problema": "Filas duplicadas"}
    ])

    gestor.rechazar(1)

    with pytest.raises(ValueError):
        gestor.marcar_obsoleta(1)