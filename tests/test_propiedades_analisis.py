from datetime import date
from decimal import Decimal

from hypothesis import given, strategies as st

from ventas.analisis import resumir
from ventas.modelos import Venta


@st.composite
def ventas_validas(draw):
    cantidad = draw(st.integers(min_value=1, max_value=20))
    ids = st.sampled_from([f"T{i}" for i in range(5)])
    productos = st.sampled_from(["Cable", "Mouse", "Teclado", "Monitor", "Webcam", "Parlante"])
    fechas = st.dates(min_value=date(2025, 1, 1), max_value=date(2027, 12, 31))
    ventas = []
    for _ in range(cantidad):
        ventas.append(
            Venta(
                id_ticket=draw(ids),
                fecha=draw(fechas),
                producto=draw(productos),
                categoria="Categoría",
                cantidad=draw(st.integers(min_value=1, max_value=20)),
                precio_unitario=Decimal(draw(st.integers(min_value=1, max_value=100_000))) / 100,
                sucursal="Centro",
            )
        )
    return ventas


@given(ventas_validas())
def test_facturacion_mensual_suma_la_facturacion_total(ventas):
    resumen, mensual, _ = resumir(ventas)

    assert sum(mensual.values(), Decimal("0.00")) == resumen["facturacion_total"]


@given(ventas_validas())
def test_tickets_y_promedio_se_calculan_a_partir_de_ids_distintos(ventas):
    resumen, _, _ = resumir(ventas)
    total = sum((venta.importe for venta in ventas), Decimal("0.00"))
    cantidad_tickets = len({venta.id_ticket for venta in ventas})

    assert resumen["cantidad_tickets"] == cantidad_tickets
    assert resumen["ticket_promedio"] == round(total / cantidad_tickets, 2)


@given(ventas_validas())
def test_top5_es_el_ranking_de_unidades_con_desempate_alfabetico(ventas):
    resumen, _, _ = resumir(ventas)
    unidades = {}
    for venta in ventas:
        unidades[venta.producto] = unidades.get(venta.producto, 0) + venta.cantidad
    esperado = [
        {"producto": producto, "unidades": cantidad}
        for producto, cantidad in sorted(unidades.items(), key=lambda par: (-par[1], par[0]))[:5]
    ]

    assert resumen["top5_productos"] == esperado
