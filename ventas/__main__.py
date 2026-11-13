"""Punto de entrada para ``python -m ventas``."""

import argparse
from pathlib import Path

from ventas.analisis import resumir
from ventas.categorias import cargar_catalogo, resolver_categorias
from ventas.entrada import cargar_ventas_archivo
from ventas.salida import escribir_informes


def main() -> int:
    parser = argparse.ArgumentParser(description="Analiza ventas desde archivos CSV o JSON.")
    parser.add_argument("archivos", nargs="+", type=Path, help="archivos de ventas CSV o JSON")
    parser.add_argument("--salida", required=True, type=Path, help="directorio para los informes")
    parser.add_argument("--catalogo", type=Path, help="CSV producto,categoria (opcional)")
    argumentos = parser.parse_args()

    try:
        ventas = [
            venta
            for ruta in argumentos.archivos
            for venta in cargar_ventas_archivo(ruta)
        ]
        if not ventas:
            raise ValueError("Los archivos indicados no contienen ventas válidas")
        catalogo = cargar_catalogo(argumentos.catalogo) if argumentos.catalogo else {}
        ventas, para_revisar = resolver_categorias(ventas, catalogo)
        resumen, mensual, categorias = resumir(ventas)
        escribir_informes(argumentos.salida, resumen, mensual, categorias, para_revisar)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Facturación total: $ {resumen['facturacion_total']:.2f}")
    print(f"Tickets: {resumen['cantidad_tickets']}")
    print(f"Ticket promedio: $ {resumen['ticket_promedio']:.2f}")
    if para_revisar:
        print(f"Productos para revisar: {len(para_revisar)} (ver revision.csv)")
    print(f"Informes guardados en: {argumentos.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
