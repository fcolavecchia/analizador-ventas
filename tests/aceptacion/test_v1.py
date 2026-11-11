"""Tests de aceptación v1: un CSV. Valores del caso mínimo calculados a mano.

caso_minimo.csv (9 filas, 5 tickets):
    enero:   800000 + 20000 + 20000           = 840000
    febrero: 10000 + 90000 + 500000 + 60000   = 660000
    marzo:   10000 + 40000                    =  50000
    total                                     = 1550000
    ticket promedio = 1550000 / 5 tickets     = 310000   (por fila sería 172222.22)
    unidades: Cable USB 15, Auriculares 4, Mouse 3, Teclado 3, Monitor 2,
              Notebook 1, Webcam 1   (por importe ganaría Notebook)
"""

import hashlib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
DATOS = Path(__file__).resolve().parent / "datos"
CASO_MINIMO = DATOS / "caso_minimo.csv"


def test_facturacion_total(ejecutar):
    resumen, _ = ejecutar(CASO_MINIMO)
    assert resumen["facturacion_total"] == pytest.approx(1_550_000, abs=0.01)


def test_facturacion_mensual(ejecutar):
    _, mensual = ejecutar(CASO_MINIMO)
    assert mensual == pytest.approx({"2026-01": 840_000, "2026-02": 660_000, "2026-03": 50_000})


def test_ticket_promedio_cuenta_tickets_no_filas(ejecutar):
    resumen, _ = ejecutar(CASO_MINIMO)
    assert resumen["cantidad_tickets"] == 5
    assert resumen["ticket_promedio"] == pytest.approx(310_000, abs=0.01)


def test_ranking_por_unidades_con_desempate_alfabetico(ejecutar):
    resumen, _ = ejecutar(CASO_MINIMO)
    assert resumen["top5_productos"] == [
        {"producto": "Cable USB", "unidades": 15},
        {"producto": "Auriculares", "unidades": 4},
        {"producto": "Mouse", "unidades": 3},
        {"producto": "Teclado", "unidades": 3},
        {"producto": "Monitor", "unidades": 2},
    ]


def test_mensual_suma_el_total_en_datos_reales(ejecutar):
    resumen, mensual = ejecutar(RAIZ / "data" / "ventas.csv")
    assert sum(mensual.values()) == pytest.approx(resumen["facturacion_total"], abs=0.01)


def test_no_modifica_la_entrada(ejecutar):
    ventas = RAIZ / "data" / "ventas.csv"
    antes = hashlib.sha256(ventas.read_bytes()).hexdigest()
    ejecutar(ventas)
    assert hashlib.sha256(ventas.read_bytes()).hexdigest() == antes
