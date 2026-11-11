"""Utilidades de los tests de aceptación (provistos por el docente).

Los tests son de caja negra: ejecutan el programa como lo indica SPEC.md
y verifican los archivos que produce. No dependen de la estructura interna.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture
def ejecutar(tmp_path):
    """Corre `python -m ventas <archivos> --salida <dir>` y devuelve (resumen, mensual)."""

    def _ejecutar(*archivos, nombre="salida"):
        salida = tmp_path / nombre
        proceso = subprocess.run(
            [sys.executable, "-m", "ventas", *map(str, archivos), "--salida", str(salida)],
            cwd=RAIZ,
            capture_output=True,
            text=True,
        )
        assert proceso.returncode == 0, f"El programa falló:\n{proceso.stderr}"

        resumen = json.loads((salida / "resumen.json").read_text(encoding="utf-8"))
        with (salida / "mensual.csv").open(newline="", encoding="utf-8") as f:
            mensual = {fila["mes"]: float(fila["facturacion"]) for fila in csv.DictReader(f)}
        return resumen, mensual

    return _ejecutar
