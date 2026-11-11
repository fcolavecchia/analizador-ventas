#!/usr/bin/env python3
"""Analizador simple de ventas para data/ventas.csv."""

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def cargar_ventas(ruta: Path) -> list[dict]:
    with ruta.open(newline="", encoding="utf-8") as archivo:
        ventas = []
        for fila in csv.DictReader(archivo):
            fila["fecha"] = datetime.strptime(fila["fecha"], "%Y-%m-%d").date()
            fila["cantidad"] = int(fila["cantidad"])
            fila["precio_unitario"] = float(fila["precio_unitario"])
            fila["importe"] = fila["cantidad"] * fila["precio_unitario"]
            ventas.append(fila)
    if not ventas:
        raise ValueError("El archivo no contiene ventas")
    return ventas


def agrupar(ventas, clave):
    resultado = defaultdict(lambda: {"importe": 0.0, "unidades": 0, "tickets": set()})
    for venta in ventas:
        grupo = resultado[clave(venta)]
        grupo["importe"] += venta["importe"]
        grupo["unidades"] += venta["cantidad"]
        grupo["tickets"].add(venta["id_ticket"])
    return resultado


def analizar(ventas):
    total = sum(v["importe"] for v in ventas)
    unidades = sum(v["cantidad"] for v in ventas)
    tickets = {v["id_ticket"] for v in ventas}
    por_mes = agrupar(ventas, lambda v: v["fecha"].strftime("%Y-%m"))
    por_producto = agrupar(ventas, lambda v: v["producto"])
    por_categoria = agrupar(ventas, lambda v: v["categoria"])
    por_sucursal = agrupar(ventas, lambda v: v["sucursal"])
    return {
        "periodo": (min(v["fecha"] for v in ventas), max(v["fecha"] for v in ventas)),
        "total": total,
        "unidades": unidades,
        "tickets": len(tickets),
        "ticket_promedio": total / len(tickets),
        "por_mes": por_mes,
        "por_producto": por_producto,
        "por_categoria": por_categoria,
        "por_sucursal": por_sucursal,
    }


def moneda(valor):
    return f"${valor:,.0f}".replace(",", ".")


def imprimir_tabla(titulo, datos, limite=None, ascendente=False):
    print(f"\n{titulo}")
    if ascendente:
        ordenados = sorted(datos.items(), key=lambda item: item[0])
    else:
        ordenados = sorted(datos.items(), key=lambda item: item[1]["importe"], reverse=True)
    if limite:
        ordenados = ordenados[:limite]
    for nombre, dato in ordenados:
        print(f"  {nombre:<22} {moneda(dato['importe']):>14} | {dato['unidades']:>5} unidades | {len(dato['tickets']):>4} tickets")


def main():
    parser = argparse.ArgumentParser(description="Resume ventas por período, producto, categoría y sucursal")
    parser.add_argument("archivo", nargs="?", type=Path, default=Path("data/ventas.csv"))
    parser.add_argument("--top", type=int, default=5, help="cantidad de productos destacados (por defecto: 5)")
    args = parser.parse_args()

    resultado = analizar(cargar_ventas(args.archivo))
    inicio, fin = resultado["periodo"]
    print("ANÁLISIS DE VENTAS")
    print(f"Período: {inicio:%d/%m/%Y} al {fin:%d/%m/%Y}")
    print(f"Facturación total: {moneda(resultado['total'])}")
    print(f"Tickets: {resultado['tickets']:,} | Unidades: {resultado['unidades']:,} | Ticket promedio: {moneda(resultado['ticket_promedio'])}")
    imprimir_tabla("EVOLUCIÓN MENSUAL", resultado["por_mes"], ascendente=True)
    imprimir_tabla("POR SUCURSAL", resultado["por_sucursal"])
    imprimir_tabla("POR CATEGORÍA", resultado["por_categoria"])
    imprimir_tabla(f"TOP {args.top} PRODUCTOS", resultado["por_producto"], args.top)


if __name__ == "__main__":
    main()
