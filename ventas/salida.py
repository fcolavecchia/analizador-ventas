"""Escritura de los informes generados por el programa."""

import csv
import json
from decimal import Decimal
from pathlib import Path


def escribir_informes(
    directorio: Path,
    resumen: dict,
    mensual: dict[str, Decimal],
    categorias: dict[str, tuple[Decimal, int]],
    para_revisar: list[tuple[str, str]] = (),
) -> None:
    directorio.mkdir(parents=True, exist_ok=True)
    with (directorio / "mensual.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["mes", "facturacion"])
        escritor.writerows((mes, f"{importe:.2f}") for mes, importe in sorted(mensual.items()))

    with (directorio / "resumen.json").open("w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2, default=float)
        archivo.write("\n")

    categorias_ordenadas = sorted(
        categorias.items(), key=lambda par: (-par[1][0], par[0])
    )
    with (directorio / "categorias.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["categoria", "facturacion", "unidades"])
        escritor.writerows(
            (categoria, f"{facturacion:.2f}", unidades)
            for categoria, (facturacion, unidades) in categorias_ordenadas
        )

    with (directorio / "revision.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["producto", "categoria_original"])
        escritor.writerows(para_revisar)
