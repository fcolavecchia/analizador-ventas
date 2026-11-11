"""Interfaz de línea de comandos del analizador."""

import argparse
from pathlib import Path

from .analisis import analizar
from .lector import cargar_ventas
from .salidas import escribir_salidas


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume ventas desde un archivo CSV")
    parser.add_argument("archivo", type=Path)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()

    resultado = analizar(cargar_ventas(args.archivo))
    escribir_salidas(resultado, args.salida)
    print(f"Facturación total: {resultado['facturacion_total']:.2f}")
    print(f"Cantidad de tickets: {resultado['cantidad_tickets']}")
    print(f"Ticket promedio: {resultado['ticket_promedio']:.2f}")
    print(f"Archivos generados en: {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

