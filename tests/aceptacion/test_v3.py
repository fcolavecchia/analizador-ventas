"""Tests de aceptación v3: facturación por categoría. Valores calculados a mano.

caso_minimo.csv:
    Computación: 800000 + 2 * 250000                  = 1300000   (3 unidades)
    Periféricos: 20000 + 90000 + 10000 + 40000        =  160000   (7 unidades)
    Audio:       4 * 15000                            =   60000   (4 unidades)
    Accesorios:  10 * 2000 + 5 * 2000                 =   30000   (15 unidades)
    suma                                              = 1550000

caso_minimo.csv + caso_minimo_online.json:
    Computación: 1300000 (W002 está cancelada: no suma) = 1300000   (3 unidades)
    Periféricos: 160000 + 12000 (W001) + 120000 (W003) =  292000   (11 unidades)
    Audio:                                                60000   (4 unidades)
    Accesorios:  30000 + 10000 (W001)                 =   40000   (20 unidades)
"""

import csv
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
DATOS = Path(__file__).resolve().parent / "datos"
CASO_CSV = DATOS / "caso_minimo.csv"
CASO_JSON = DATOS / "caso_minimo_online.json"


def leer_categorias(directorio):
    with (directorio / "categorias.csv").open(newline="", encoding="utf-8") as f:
        return [
            (fila["categoria"], float(fila["facturacion"]), int(fila["unidades"]))
            for fila in csv.DictReader(f)
        ]


def test_categorias_solo_csv(ejecutar, tmp_path):
    ejecutar(CASO_CSV)
    assert leer_categorias(tmp_path / "salida") == [
        ("Computación", 1_300_000, 3),
        ("Periféricos", 160_000, 7),
        ("Audio", 60_000, 4),
        ("Accesorios", 30_000, 15),
    ]


def test_categorias_csv_y_json(ejecutar, tmp_path):
    ejecutar(CASO_CSV, CASO_JSON)
    assert leer_categorias(tmp_path / "salida") == [
        ("Computación", 1_300_000, 3),
        ("Periféricos", 292_000, 11),
        ("Audio", 60_000, 4),
        ("Accesorios", 40_000, 20),
    ]


def test_categorias_suman_el_total_en_datos_reales(ejecutar, tmp_path):
    resumen, _ = ejecutar(RAIZ / "data" / "ventas.csv", RAIZ / "data" / "ventas_online.json")
    categorias = leer_categorias(tmp_path / "salida")
    assert sum(f for _, f, _ in categorias) == pytest.approx(resumen["facturacion_total"], abs=0.01)
