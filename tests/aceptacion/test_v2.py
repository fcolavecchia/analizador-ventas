"""Tests de aceptación v2: CSV + JSON online. Valores calculados a mano.

caso_minimo_online.json (3 órdenes, una cancelada):
    W001 enero:   5 * 2000 + 1 * 12000 = 22000
    W002 febrero: CANCELADA, no cuenta (800000)
    W003 marzo:   3 * 40000            = 120000
    total online                       = 142000

caso_minimo.csv + caso_minimo_online.json:
    enero 862000, febrero 660000, marzo 170000, total 1692000
    tickets 5 + 2 = 7, ticket promedio = 1692000 / 7 = 241714.29
    unidades: Cable USB 20, Auriculares 4, Mouse 4, Webcam 4, Teclado 3, Monitor 2, Notebook 1
"""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
DATOS = Path(__file__).resolve().parent / "datos"
CASO_CSV = DATOS / "caso_minimo.csv"
CASO_JSON = DATOS / "caso_minimo_online.json"


def test_solo_json(ejecutar):
    resumen, mensual = ejecutar(CASO_JSON)
    assert resumen["facturacion_total"] == pytest.approx(142_000, abs=0.01)
    assert mensual == pytest.approx({"2026-01": 22_000, "2026-03": 120_000})


def test_canceladas_no_cuentan(ejecutar):
    resumen, _ = ejecutar(CASO_JSON)
    assert resumen["cantidad_tickets"] == 2
    assert "Notebook" not in [p["producto"] for p in resumen["top5_productos"]]


def test_csv_y_json_combinados(ejecutar):
    resumen, mensual = ejecutar(CASO_CSV, CASO_JSON)
    assert resumen["facturacion_total"] == pytest.approx(1_692_000, abs=0.01)
    assert mensual == pytest.approx({"2026-01": 862_000, "2026-02": 660_000, "2026-03": 170_000})
    assert resumen["cantidad_tickets"] == 7
    assert resumen["ticket_promedio"] == pytest.approx(241_714.29, abs=0.01)
    assert resumen["top5_productos"] == [
        {"producto": "Cable USB", "unidades": 20},
        {"producto": "Auriculares", "unidades": 4},
        {"producto": "Mouse", "unidades": 4},
        {"producto": "Webcam", "unidades": 4},
        {"producto": "Teclado", "unidades": 3},
    ]


def test_regresion_combinar_es_sumar_las_fuentes(ejecutar):
    """Agregar el JSON no cambia lo que aporta el CSV: los resultados se suman."""
    csv_, mensual_csv = ejecutar(RAIZ / "data" / "ventas.csv", nombre="csv")
    json_, mensual_json = ejecutar(RAIZ / "data" / "ventas_online.json", nombre="json")
    ambos, mensual_ambos = ejecutar(
        RAIZ / "data" / "ventas.csv", RAIZ / "data" / "ventas_online.json", nombre="ambos"
    )

    assert ambos["facturacion_total"] == pytest.approx(
        csv_["facturacion_total"] + json_["facturacion_total"], abs=0.01
    )
    assert ambos["cantidad_tickets"] == csv_["cantidad_tickets"] + json_["cantidad_tickets"]
    assert set(mensual_ambos) == set(mensual_csv) | set(mensual_json)
    for mes in mensual_ambos:
        esperado = mensual_csv.get(mes, 0) + mensual_json.get(mes, 0)
        assert mensual_ambos[mes] == pytest.approx(esperado, abs=0.01)
