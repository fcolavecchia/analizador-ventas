"""Lectura y normalización de fuentes de ventas."""

import csv
import json
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


def cargar_ventas_online(ruta: Path) -> list[Venta]:
    """Carga órdenes online y las normaliza al modelo común de ventas."""
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer el JSON: {error}") from error

    if not isinstance(datos, list) or not datos:
        raise ValueError("El JSON debe contener una lista no vacía de órdenes")

    ventas = []
    for numero, orden in enumerate(datos, start=1):
        try:
            if not isinstance(orden, dict):
                raise ValueError("la orden debe ser un objeto")
            if orden["status"] not in {"completed", "cancelled"}:
                raise ValueError("status debe ser completed o cancelled")
            if orden["status"] == "cancelled":
                continue

            order_id = orden["order_id"]
            fecha = datetime.fromisoformat(orden["date"]).date()
            items = orden["items"]
            if not isinstance(items, list):
                raise ValueError("items debe ser una lista")

            for item_numero, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    raise ValueError(f"ítem {item_numero} debe ser un objeto")
                unidades = int(item["units"])
                precio = Decimal(str(item["unit_price"]))
                if unidades <= 0 or precio <= 0:
                    raise ValueError("units y unit_price deben ser mayores que cero")
                ventas.append(Venta(
                    id_ticket=order_id,
                    fecha=fecha,
                    producto=item["item"],
                    categoria=item["category"],
                    cantidad=unidades,
                    precio_unitario=precio,
                    sucursal="Online",
                ))
        except (KeyError, TypeError, ValueError, ArithmeticError) as error:
            raise ValueError(f"Orden inválida en la posición {numero}: {error}") from error

    if not ventas:
        raise ValueError("El archivo no contiene ventas online completadas")
    return ventas


def cargar_archivo(ruta: Path) -> list[Venta]:
    """Carga una fuente soportada según su extensión."""
    if ruta.suffix.lower() == ".csv":
        return cargar_ventas(ruta)
    if ruta.suffix.lower() == ".json":
        return cargar_ventas_online(ruta)
    raise ValueError(f"Formato no soportado: {ruta.suffix or '(sin extensión)'}")

