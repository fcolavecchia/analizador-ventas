"""Corre el juez sobre los casos etiquetados a mano y compara sus respuestas con las etiquetas.

Uso (desde la raíz del repo):
    python3 revision/calibrar.py            # todos los casos
    python3 revision/calibrar.py caso5      # uno solo

Cada caso tarda unos segundos (una llamada al modelo por caso).
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

REVISION = Path(__file__).resolve().parent
CRITERIOS = ["C1", "C2", "C3", "C4"]
LINEA = re.compile(r"^\s*(C[1-4])\s*:\s*(S[IÍ]|NO)\b", re.IGNORECASE | re.MULTILINE)


def juzgar(caso: str) -> tuple[dict[str, str], str]:
    salida = subprocess.run(
        [REVISION / "juzgar.sh", REVISION / "casos" / f"{caso}.diff"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    respuestas = {
        criterio.upper(): valor.upper().replace("Í", "I") for criterio, valor in LINEA.findall(salida)
    }
    return respuestas, salida


def main() -> int:
    with (REVISION / "etiquetas.csv").open(newline="", encoding="utf-8") as archivo:
        etiquetas = list(csv.DictReader(archivo))
    if len(sys.argv) > 1:
        etiquetas = [fila for fila in etiquetas if fila["caso"] in sys.argv[1:]]

    coincidencias = total = 0
    for fila in etiquetas:
        respuestas, salida = juzgar(fila["caso"])
        print(f"\n== {fila['caso']}: {fila['nota']}")
        print(salida.strip())
        marcas = []
        for criterio in CRITERIOS:
            juez = respuestas.get(criterio, "?")
            ok = juez == fila[criterio]
            coincidencias += ok
            total += 1
            marcas.append(f"{criterio} juez={juez} esperado={fila[criterio]} {'✓' if ok else '✗'}")
        print("   " + " | ".join(marcas))

    print(f"\nCoincidencia con las etiquetas: {coincidencias}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
