"""Cálculos de negocio sobre ventas normalizadas."""

from collections import defaultdict
from decimal import Decimal

from .modelos import Venta


def analizar(ventas: list[Venta]) -> dict:
    total = sum((venta.importe for venta in ventas), Decimal("0"))
    tickets = {venta.id_ticket for venta in ventas}
    por_mes = defaultdict(lambda: Decimal("0"))
    productos = defaultdict(int)
    for venta in ventas:
        por_mes[venta.fecha.strftime("%Y-%m")] += venta.importe
        productos[venta.producto] += venta.cantidad
    top5 = [
        {"producto": producto, "unidades": unidades}
        for producto, unidades in sorted(productos.items(), key=lambda item: (-item[1], item[0]))[:5]
    ]
    return {
        "facturacion_total": total,
        "cantidad_tickets": len(tickets),
        "ticket_promedio": total / len(tickets),
        "facturacion_mensual": dict(sorted(por_mes.items())),
        "top5_productos": top5,
    }

