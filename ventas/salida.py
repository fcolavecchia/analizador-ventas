"""Escritura de los informes generados por el programa."""

import csv
import json
from decimal import Decimal
from pathlib import Path


def escribir_informes(
    directorio: Path, resumen: dict, mensual: dict[str, Decimal]
) -> None:
    directorio.mkdir(parents=True, exist_ok=True)
    with (directorio / "mensual.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["mes", "facturacion"])
        escritor.writerows((mes, f"{importe:.2f}") for mes, importe in sorted(mensual.items()))

    with (directorio / "resumen.json").open("w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2, default=float)
        archivo.write("\n")
