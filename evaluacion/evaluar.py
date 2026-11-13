"""Compara propuestas de categoría con las etiquetas hechas a mano (script del docente).

Uso (desde la raíz del repo):
    python3 evaluacion/evaluar.py evaluacion/etiquetas.csv propuestas.csv [--umbral 0.8]

Las propuestas tienen el formato de la SPEC: producto,categoria,confianza. Un producto etiquetado que no
aparece en las propuestas cuenta como "sin propuesta".
"""

import argparse
import csv
from pathlib import Path

TRAMOS = [(0.9, 1.0, "0.9 – 1.0"), (0.7, 0.9, "0.7 – 0.9"), (0.0, 0.7, "0.0 – 0.7")]


def leer(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def porcentaje(parte: int, total: int) -> str:
    return f"{parte}/{total} ({parte / total:.0%})" if total else "0/0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("etiquetas", type=Path)
    parser.add_argument("propuestas", type=Path)
    parser.add_argument("--umbral", type=float, default=0.8)
    args = parser.parse_args()

    etiquetas = leer(args.etiquetas)
    propuestas = {fila["producto"]: fila for fila in leer(args.propuestas)}

    filas = []
    for etiqueta in etiquetas:
        propuesta = propuestas.get(etiqueta["producto"], {})
        categoria = propuesta.get("categoria", "")
        confianza = float(propuesta.get("confianza") or 0)
        filas.append((etiqueta["producto"], etiqueta["categoria"], categoria, confianza, etiqueta["nota"]))

    total = len(filas)
    con_propuesta = [f for f in filas if f[2]]
    aciertos = [f for f in con_propuesta if f[2] == f[1]]

    print(f"Productos etiquetados: {total}")
    print(f"Con propuesta:         {porcentaje(len(con_propuesta), total)}")
    print(f"Aciertos (sobre todos):     {porcentaje(len(aciertos), total)}")
    print(f"Aciertos (sobre propuestas): {porcentaje(len(aciertos), len(con_propuesta))}")

    print("\nPor confianza declarada:")
    for desde, hasta, nombre in TRAMOS:
        tramo = [f for f in con_propuesta if desde <= f[3] <= hasta and not (hasta < 1.0 and f[3] == hasta)]
        bien = sum(f[2] == f[1] for f in tramo)
        print(f"  {nombre}: {porcentaje(bien, len(tramo))} aciertos")

    aceptadas = [f for f in con_propuesta if f[3] >= args.umbral]
    bien = sum(f[2] == f[1] for f in aceptadas)
    print(f"\nCon umbral {args.umbral}: se aceptan {len(aceptadas)} (aciertos {porcentaje(bien, len(aceptadas))}),"
          f" van a revisión {total - len(aceptadas)}")

    errores = [f for f in filas if f[2] != f[1]]
    if errores:
        print("\nErrores y faltantes:")
        for producto, esperada, propuesta, confianza, nota in errores:
            propuesta_texto = f"{propuesta} ({confianza:.2f})" if propuesta else "sin propuesta"
            print(f"  {producto}: esperada {esperada}, propuesta {propuesta_texto}" + (f"  — {nota}" if nota else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
