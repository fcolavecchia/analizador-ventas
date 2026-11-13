"""Interfaz de línea de comandos del analizador."""

import argparse
from pathlib import Path

from .analisis import analizar
from .lector import cargar_archivo
from .salidas import escribir_salidas


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume ventas desde archivos CSV o JSON")
    parser.add_argument("archivo", type=Path, nargs="+")
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()

    ventas = []
    for archivo in args.archivo:
        ventas.extend(cargar_archivo(archivo))
    resultado = analizar(ventas)
    escribir_salidas(resultado, args.salida)
    print(f"Facturación total: {resultado['facturacion_total']:.2f}")
    print(f"Cantidad de tickets: {resultado['cantidad_tickets']}")
    print(f"Ticket promedio: {resultado['ticket_promedio']:.2f}")
    print(f"Archivos generados en: {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

