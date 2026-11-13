"""Tests de aceptación v4: categorías sucias, catálogo y revisión. Valores calculados a mano.

caso_oeste.csv con catalogo_minimo.csv (Cable USB, Mouse y Teclado están en el catálogo):
    Mouse         "perifericos"   → catálogo: Periféricos       2 * 12000 =  24000
    Micrófono USB "AUDIO "        → normalizada: Audio          1 * 40000 =  40000
    Hub USB-C     ""              → Sin clasificar              1 * 25000 =  25000
    Soporte p/m.  "Varios"        → Sin clasificar              2 * 15000 =  30000
    Cable USB     "Accesorios PC" → catálogo: Accesorios        3 *  2500 =   7500
    Disco SSD 1TB "computacion"   → normalizada: Computación    1 * 90000 =  90000
    Teclado       "Audio"         → catálogo (gana): Periféricos 1 * 30000 =  30000
    total 246500; 4 tickets; abril 89000, mayo 157500

    Computación 90000 (1) · Sin clasificar 55000 (3) · Periféricos 54000 (3) · Audio 40000 (1) · Accesorios 7500 (3)

Sin catálogo: Cable USB pasa a Sin clasificar y Teclado queda en Audio:
    Computación 90000 (1) · Audio 70000 (2) · Sin clasificar 62500 (6) · Periféricos 24000 (2)
"""

import csv
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
DATOS = Path(__file__).resolve().parent / "datos"
CASO_OESTE = DATOS / "caso_oeste.csv"
CATALOGO_MINIMO = DATOS / "catalogo_minimo.csv"
CATALOGO_REAL = RAIZ / "data" / "catalogo_categorias.csv"


def leer_csv(ruta):
    with ruta.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def leer_categorias(directorio):
    return [
        (fila["categoria"], float(fila["facturacion"]), int(fila["unidades"]))
        for fila in leer_csv(directorio / "categorias.csv")
    ]


def leer_revision(directorio):
    return [(fila["producto"], fila["categoria_original"]) for fila in leer_csv(directorio / "revision.csv")]


def test_categorias_con_catalogo(ejecutar, tmp_path):
    ejecutar(CASO_OESTE, "--catalogo", CATALOGO_MINIMO)
    assert leer_categorias(tmp_path / "salida") == [
        ("Computación", 90_000, 1),
        ("Sin clasificar", 55_000, 3),
        ("Periféricos", 54_000, 3),
        ("Audio", 40_000, 1),
        ("Accesorios", 7_500, 3),
    ]
    assert leer_revision(tmp_path / "salida") == [
        ("Hub USB-C", ""),
        ("Soporte para monitor", "Varios"),
    ]


def test_categorias_sin_catalogo(ejecutar, tmp_path):
    ejecutar(CASO_OESTE)
    assert leer_categorias(tmp_path / "salida") == [
        ("Computación", 90_000, 1),
        ("Audio", 70_000, 2),
        ("Sin clasificar", 62_500, 6),
        ("Periféricos", 24_000, 2),
    ]
    assert leer_revision(tmp_path / "salida") == [
        ("Cable USB", "Accesorios PC"),
        ("Hub USB-C", ""),
        ("Soporte para monitor", "Varios"),
    ]


def test_las_categorias_no_cambian_los_totales(ejecutar):
    resumen, mensual = ejecutar(CASO_OESTE, "--catalogo", CATALOGO_MINIMO)
    assert resumen["facturacion_total"] == pytest.approx(246_500, abs=0.01)
    assert resumen["cantidad_tickets"] == 4
    assert mensual == pytest.approx({"2026-04": 89_000, "2026-05": 157_500})


def test_revision_vacia_tiene_encabezado(ejecutar, tmp_path):
    ejecutar(DATOS / "caso_minimo.csv")
    assert (tmp_path / "salida" / "revision.csv").read_text(encoding="utf-8").strip() == (
        "producto,categoria_original"
    )


def test_regresion_el_catalogo_real_no_cambia_las_fuentes_anteriores(ejecutar, tmp_path):
    fuentes = [RAIZ / "data" / "ventas.csv", RAIZ / "data" / "ventas_online.json"]
    sin = ejecutar(*fuentes, nombre="sin")
    con = ejecutar(*fuentes, "--catalogo", CATALOGO_REAL, nombre="con")
    assert con == sin
    assert leer_categorias(tmp_path / "con") == leer_categorias(tmp_path / "sin")
    assert leer_revision(tmp_path / "con") == []


def test_catalogo_con_categoria_invalida_es_un_error(tmp_path):
    catalogo = tmp_path / "catalogo.csv"
    catalogo.write_text("producto,categoria\nMouse,Gaming\n", encoding="utf-8")
    proceso = subprocess.run(
        [sys.executable, "-m", "ventas", str(CASO_OESTE), "--catalogo", str(catalogo),
         "--salida", str(tmp_path / "salida")],
        cwd=RAIZ,
        capture_output=True,
        text=True,
    )
    assert proceso.returncode != 0
    assert "Gaming" in proceso.stderr
