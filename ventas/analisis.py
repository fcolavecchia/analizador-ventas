"""Cálculos de negocio sobre ventas ya normalizadas."""

from collections import defaultdict
from decimal import Decimal

from ventas.modelos import Venta


def a_dos_decimales(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"))


def resumir(ventas: list[Venta]) -> tuple[dict, dict[str, Decimal]]:
    if not ventas:
        raise ValueError("No hay ventas para analizar")

    total = sum(venta.importe for venta in ventas)
    tickets = {venta.id_ticket for venta in ventas}
    por_mes: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    unidades_por_producto: defaultdict[str, int] = defaultdict(int)
    for venta in ventas:
        por_mes[venta.fecha.strftime("%Y-%m")] += venta.importe
        unidades_por_producto[venta.producto] += venta.cantidad

    promedio = total / len(tickets)
    resumen = {
        "facturacion_total": a_dos_decimales(total),
        "cantidad_tickets": len(tickets),
        "ticket_promedio": a_dos_decimales(promedio),
        "top5_productos": [
            {"producto": producto, "unidades": unidades}
            for producto, unidades in sorted(
                unidades_por_producto.items(), key=lambda par: (-par[1], par[0])
            )[:5]
        ],
    }
    mensual = {mes: a_dos_decimales(por_mes[mes]) for mes in sorted(por_mes)}
    return resumen, mensual
