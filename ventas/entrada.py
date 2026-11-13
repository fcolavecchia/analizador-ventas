"""Lectura, validación y normalización de archivos de entrada."""

import csv
import json
import math
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from ventas.modelos import Venta

COLUMNAS_REQUERIDAS = {
    "id_ticket",
    "fecha",
    "producto",
    "categoria",
    "cantidad",
    "precio_unitario",
    "sucursal",
}


def cargar_ventas(ruta: Path) -> list[Venta]:
    ventas: list[Venta] = []
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        faltantes = COLUMNAS_REQUERIDAS - set(lector.fieldnames or [])
        if faltantes:
            raise ValueError("Faltan columnas requeridas: " + ", ".join(sorted(faltantes)))

        for numero_fila, fila in enumerate(lector, start=2):
            try:
                fecha_texto = fila["fecha"]
                fecha = date.fromisoformat(fecha_texto)
                if fecha.isoformat() != fecha_texto:
                    raise ValueError("la fecha debe tener formato AAAA-MM-DD")
                cantidad = int(fila["cantidad"])
                precio = Decimal(fila["precio_unitario"])
            except (ValueError, TypeError, InvalidOperation) as error:
                raise ValueError(f"Datos inválidos en la fila {numero_fila}: {error}") from error

            if cantidad <= 0:
                raise ValueError(f"La cantidad debe ser mayor que cero en la fila {numero_fila}")
            if not precio.is_finite() or precio <= 0:
                raise ValueError(f"El precio debe ser mayor que cero en la fila {numero_fila}")

            ventas.append(
                Venta(
                    id_ticket=fila["id_ticket"],
                    fecha=fecha,
                    producto=fila["producto"],
                    categoria=fila["categoria"],
                    cantidad=cantidad,
                    precio_unitario=precio,
                    sucursal=fila["sucursal"],
                )
            )

    return ventas


def _error_orden(numero: int, detalle: str) -> ValueError:
    return ValueError(f"Orden {numero} inválida: {detalle}")


def _precio_json(valor: Any, numero_orden: int, numero_item: int) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise _error_orden(numero_orden, f"items[{numero_item}].unit_price debe ser un número")
    precio = Decimal(str(valor))
    if not precio.is_finite() or precio <= 0:
        raise _error_orden(numero_orden, f"items[{numero_item}].unit_price debe ser mayor que cero")
    return precio


def cargar_ventas_json(ruta: Path) -> list[Venta]:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            ordenes = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON inválido en {ruta}, línea {error.lineno}, columna {error.colno}: {error.msg}"
        ) from error

    if not isinstance(ordenes, list):
        raise ValueError(f"El archivo JSON {ruta} debe contener una lista de órdenes")

    ventas: list[Venta] = []
    campos_orden = {"order_id", "date", "status", "items"}
    campos_item = {"item", "category", "units", "unit_price"}

    for numero_orden, orden in enumerate(ordenes, start=1):
        if not isinstance(orden, dict):
            raise _error_orden(numero_orden, "se esperaba un objeto")
        faltantes = campos_orden - orden.keys()
        if faltantes:
            raise _error_orden(numero_orden, "faltan campos: " + ", ".join(sorted(faltantes)))

        estado = orden["status"]
        if estado not in ("completed", "cancelled"):
            raise _error_orden(
                numero_orden,
                f"status desconocido {estado!r}; debe ser 'completed' o 'cancelled'",
            )

        items = orden["items"]
        if not isinstance(items, list):
            raise _error_orden(numero_orden, "items debe ser una lista")
        if estado == "cancelled":
            continue

        order_id = orden["order_id"]
        if not isinstance(order_id, str) or not order_id:
            raise _error_orden(numero_orden, "order_id debe ser texto no vacío")
        fecha_texto = orden["date"]
        if not isinstance(fecha_texto, str) or len(fecha_texto) < 10:
            raise _error_orden(numero_orden, "date debe comenzar con una fecha AAAA-MM-DD")
        fecha_parte = fecha_texto[:10]
        try:
            fecha = date.fromisoformat(fecha_parte)
        except ValueError as error:
            raise _error_orden(numero_orden, "date debe comenzar con una fecha AAAA-MM-DD") from error
        if fecha.isoformat() != fecha_parte:
            raise _error_orden(numero_orden, "date debe comenzar con una fecha AAAA-MM-DD")

        for numero_item, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                raise _error_orden(numero_orden, f"items[{numero_item}] debe ser un objeto")
            faltantes_item = campos_item - item.keys()
            if faltantes_item:
                raise _error_orden(
                    numero_orden,
                    f"items[{numero_item}] sin campos: " + ", ".join(sorted(faltantes_item)),
                )
            unidades = item["units"]
            if isinstance(unidades, bool) or not isinstance(unidades, int):
                raise _error_orden(numero_orden, f"items[{numero_item}].units debe ser un entero")
            if unidades <= 0:
                raise _error_orden(
                    numero_orden,
                    f"items[{numero_item}].units debe ser mayor que cero",
                )
            precio = _precio_json(item["unit_price"], numero_orden, numero_item)
            producto = item["item"]
            categoria = item["category"]
            if not isinstance(producto, str) or not isinstance(categoria, str):
                raise _error_orden(numero_orden, f"items[{numero_item}].item y category deben ser texto")

            ventas.append(
                Venta(
                    id_ticket=order_id,
                    fecha=fecha,
                    producto=producto,
                    categoria=categoria,
                    cantidad=unidades,
                    precio_unitario=precio,
                    sucursal="Online",
                )
            )

    return ventas


def cargar_ventas_archivo(ruta: Path) -> list[Venta]:
    if ruta.suffix == ".csv":
        return cargar_ventas(ruta)
    if ruta.suffix == ".json":
        return cargar_ventas_json(ruta)
    raise ValueError(
        f"Formato no admitido para {ruta}: la extensión debe ser .csv o .json"
    )
