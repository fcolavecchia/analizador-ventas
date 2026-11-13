from datetime import date
from decimal import Decimal

from ventas.analisis import resumir
from ventas.modelos import Venta


def test_top5_ordena_unidades_y_resuelve_empates_alfabeticamente():
    ventas = [
        Venta("T1", date(2026, 1, 1), "Teclado", "Periféricos", 3, Decimal("1"), "Centro"),
        Venta("T1", date(2026, 1, 1), "Mouse", "Periféricos", 3, Decimal("100"), "Centro"),
        Venta("T2", date(2026, 1, 2), "Cable USB", "Accesorios", 4, Decimal("1"), "Norte"),
    ]

    resumen, _ = resumir(ventas)

    assert resumen["top5_productos"] == [
        {"producto": "Cable USB", "unidades": 4},
        {"producto": "Mouse", "unidades": 3},
        {"producto": "Teclado", "unidades": 3},
    ]
