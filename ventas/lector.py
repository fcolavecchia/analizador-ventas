"""Lectura y normalización del CSV de ventas."""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .modelos import Venta

_COLUMNAS = {
    "id_ticket", "fecha", "producto", "categoria", "cantidad",
    "precio_unitario", "sucursal",
}


def cargar_ventas(ruta: Path) -> list[Venta]:
    with ruta.open(newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        if not lector.fieldnames or set(lector.fieldnames) != _COLUMNAS:
            raise ValueError("El CSV no contiene las columnas requeridas")
        ventas = []
        for numero, fila in enumerate(lector, start=2):
            try:
                cantidad = int(fila["cantidad"])
                precio = Decimal(fila["precio_unitario"])
                if cantidad <= 0 or precio <= 0:
                    raise ValueError("cantidad y precio_unitario deben ser mayores que cero")
                ventas.append(Venta(
                    id_ticket=fila["id_ticket"],
                    fecha=datetime.strptime(fila["fecha"], "%Y-%m-%d").date(),
                    producto=fila["producto"],
                    categoria=fila["categoria"],
                    cantidad=cantidad,
                    precio_unitario=precio,
                    sucursal=fila["sucursal"],
                ))
            except (KeyError, ValueError, ArithmeticError) as error:
                raise ValueError(f"Fila inválida en la línea {numero}: {error}") from error
    if not ventas:
        raise ValueError("El archivo no contiene ventas")
    return ventas

