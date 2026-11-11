from datetime import date
from decimal import Decimal

from ventas.analisis import analizar
from ventas.modelos import Venta


def venta(ticket, producto, cantidad, precio, fecha="2026-01-01"):
    return Venta(ticket, date.fromisoformat(fecha), producto, "Cat", cantidad, Decimal(precio), "Local")


def test_ticket_promedio_y_mensual_sobre_lineas_repetidas():
    resultado = analizar([
        venta("T1", "B", 2, "10"),
        venta("T1", "A", 1, "5"),
        venta("T2", "A", 3, "5", "2026-02-01"),
    ])
    assert resultado["facturacion_total"] == Decimal("40")
    assert resultado["cantidad_tickets"] == 2
    assert resultado["ticket_promedio"] == Decimal("20")
    assert resultado["facturacion_mensual"] == {"2026-01": Decimal("25"), "2026-02": Decimal("15")}


def test_top5_usa_unidades_y_desempata_por_nombre():
    resultado = analizar([
        venta("T1", "Zeta", 3, "1"),
        venta("T2", "Alfa", 3, "100"),
        venta("T3", "Beta", 2, "1"),
    ])
    assert resultado["top5_productos"] == [
        {"producto": "Alfa", "unidades": 3},
        {"producto": "Zeta", "unidades": 3},
        {"producto": "Beta", "unidades": 2},
    ]
