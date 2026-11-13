"""Resolución de categorías (SPEC v4): catálogo, texto normalizado o `Sin clasificar`."""

import csv
import unicodedata
from dataclasses import replace
from pathlib import Path

from ventas.modelos import Venta

CATEGORIAS_VALIDAS = ("Computación", "Audio", "Periféricos", "Accesorios")
SIN_CLASIFICAR = "Sin clasificar"


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sin tildes y sin espacios al principio ni al final."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return sin_tildes.strip().casefold()


_POR_TEXTO_NORMALIZADO = {normalizar_texto(c): c for c in CATEGORIAS_VALIDAS}


def categoria_valida(texto: str) -> str | None:
    """Devuelve la categoría válida a la que equivale `texto`, o None."""
    return _POR_TEXTO_NORMALIZADO.get(normalizar_texto(texto))


def cargar_catalogo(ruta: Path) -> dict[str, str]:
    """Lee `producto,categoria`. Cada producto aparece una vez y su categoría es válida."""
    catalogo: dict[str, str] = {}
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        faltantes = {"producto", "categoria"} - set(lector.fieldnames or [])
        if faltantes:
            raise ValueError(f"Catálogo {ruta}: faltan columnas: " + ", ".join(sorted(faltantes)))
        for numero_fila, fila in enumerate(lector, start=2):
            producto, categoria = fila["producto"], fila["categoria"]
            if categoria not in CATEGORIAS_VALIDAS:
                raise ValueError(
                    f"Catálogo {ruta}, fila {numero_fila}: categoría inválida {categoria!r} "
                    f"para {producto!r}; las válidas son: " + ", ".join(CATEGORIAS_VALIDAS)
                )
            if producto in catalogo:
                raise ValueError(f"Catálogo {ruta}, fila {numero_fila}: {producto!r} está repetido")
            catalogo[producto] = categoria
    return catalogo


def resolver_categoria(producto: str, original: str, catalogo: dict[str, str]) -> str:
    if producto in catalogo:
        return catalogo[producto]
    return categoria_valida(original) or SIN_CLASIFICAR


def resolver_categorias(
    ventas: list[Venta], catalogo: dict[str, str] | None = None
) -> tuple[list[Venta], list[tuple[str, str]]]:
    """Devuelve las ventas con la categoría resuelta y los pares (producto, categoría original)
    que quedaron sin clasificar, ordenados por producto y después por categoría original."""
    catalogo = catalogo or {}
    resueltas: list[Venta] = []
    para_revisar: set[tuple[str, str]] = set()
    for venta in ventas:
        categoria = resolver_categoria(venta.producto, venta.categoria, catalogo)
        if categoria == SIN_CLASIFICAR:
            para_revisar.add((venta.producto, venta.categoria))
        resueltas.append(replace(venta, categoria=categoria))
    return resueltas, sorted(para_revisar)
