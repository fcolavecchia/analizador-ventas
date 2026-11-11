"""Generación de archivos de salida."""

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def _redondear(valor: Decimal) -> float:
    return float(valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def escribir_salidas(resultado: dict, directorio: Path) -> None:
    directorio.mkdir(parents=True, exist_ok=True)
    with (directorio / "mensual.csv").open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["mes", "facturacion"])
        for mes, importe in resultado["facturacion_mensual"].items():
            escritor.writerow([mes, f"{_redondear(importe):.2f}"])

    resumen = {
        "facturacion_total": _redondear(resultado["facturacion_total"]),
        "cantidad_tickets": resultado["cantidad_tickets"],
        "ticket_promedio": _redondear(resultado["ticket_promedio"]),
        "top5_productos": resultado["top5_productos"],
    }
    (directorio / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

