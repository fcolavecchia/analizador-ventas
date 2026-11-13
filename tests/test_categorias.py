from datetime import date
from decimal import Decimal

import pytest

from ventas.categorias import (
    SIN_CLASIFICAR,
    cargar_catalogo,
    categoria_valida,
    resolver_categorias,
)
from ventas.modelos import Venta


def venta(producto, categoria):
    return Venta("T1", date(2026, 1, 1), producto, categoria, 1, Decimal("10"), "Centro")


@pytest.mark.parametrize(
    "texto, esperada",
    [(" perifericos", "Periféricos"), ("AUDIO ", "Audio"), ("computacion", "Computación"),
     ("Varios", None), ("", None)],
)
def test_categoria_valida_ignora_mayusculas_tildes_y_espacios(texto, esperada):
    assert categoria_valida(texto) == esperada


def test_el_catalogo_gana_sobre_la_linea():
    ventas, revisar = resolver_categorias([venta("Teclado", "Audio")], {"Teclado": "Periféricos"})
    assert ventas[0].categoria == "Periféricos" and revisar == []


def test_sin_catalogo_ni_categoria_valida_queda_sin_clasificar():
    ventas, revisar = resolver_categorias([venta("Hub", ""), venta("Hub", ""), venta("Soporte", "Varios")])
    assert [v.categoria for v in ventas] == [SIN_CLASIFICAR] * 3
    assert revisar == [("Hub", ""), ("Soporte", "Varios")]


def test_catalogo_con_categoria_invalida_o_repetido(tmp_path):
    ruta = tmp_path / "c.csv"
    ruta.write_text("producto,categoria\nMouse,Gaming\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Gaming"):
        cargar_catalogo(ruta)
    ruta.write_text("producto,categoria\nMouse,Periféricos\nMouse,Audio\n", encoding="utf-8")
    with pytest.raises(ValueError, match="repetido"):
        cargar_catalogo(ruta)
