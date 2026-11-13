"""Herramienta de propuestas de categoría (fuera del análisis).

Uso:
    uv run python -m ventas.proponer <entrada.csv> --metodo reglas|llm --salida <propuestas.csv>

Solo propone: no modifica el catálogo. Una persona revisa y actualiza el catálogo a mano.
"""

import argparse
import csv
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Callable

from ventas.categorias import CATEGORIAS_VALIDAS, normalizar_texto

# Reglas armadas a partir de la tabla de categorías de SPEC.md (no de las etiquetas de evaluación).
# El orden importa: una palabra de un complemento ("funda para teclado", "mousepad") gana sobre el
# equipo que nombra, y una "tableta digitalizadora" no es una "tablet".
REGLAS: list[tuple[str, tuple[str, ...]]] = [
    ("Accesorios", ("cable", "adaptador", "hub", "soporte", "funda", "cargador", "mousepad",
                    "pendrive", "pila", "pilas", "bateria")),
    ("Periféricos", ("tableta digitalizadora", "teclado", "mouse", "webcam", "joystick", "gamepad")),
    ("Audio", ("auricular", "auriculares", "parlante", "parlantes", "microfono", "placa de sonido")),
    ("Computación", ("notebook", "monitor", "impresora", "disco", "ssd", "memoria", "ram",
                     "placa de video", "router", "tablet")),
]

Propuesta = tuple[str, str, float]  # (producto, categoria, confianza)


def proponer_reglas(productos: list[str]) -> list[Propuesta]:
    propuestas = []
    for producto in productos:
        texto = f" {normalizar_texto(producto)} "
        categoria, confianza = "", 0.0
        for nombre, palabras in REGLAS:
            if any(re.search(rf"(?<![a-z0-9]){re.escape(p)}(?![a-z0-9])", texto) for p in palabras):
                categoria, confianza = nombre, 1.0
                break
        propuestas.append((producto, categoria, confianza))
    return propuestas


TABLA_CATEGORIAS = """\
- Computación: equipos y componentes de computadora (notebooks, monitores, impresoras, discos, memorias, placas de video, routers, tablets).
- Audio: equipos que reproducen o capturan sonido (auriculares, parlantes, micrófonos, placas de sonido).
- Periféricos: dispositivos de entrada o captura que se conectan a la computadora (teclados, mouse, webcams, joysticks, tabletas digitalizadoras).
- Accesorios: complementos de otro equipo y consumibles (cables, adaptadores, hubs, soportes, fundas, cargadores, mousepads, pendrives, pilas)."""


def armar_prompt(productos: list[str]) -> str:
    return (
        "Clasificá cada producto de un comercio de tecnología en exactamente una de estas categorías:\n"
        f"{TABLA_CATEGORIAS}\n\n"
        "Si no podés decidir, devolvé categoria vacía y confianza baja. La confianza es tu probabilidad "
        "estimada de acierto, entre 0 y 1.\n"
        'Respondé solo con JSON: {"propuestas": [{"producto": "...", "categoria": "...", "confianza": 0.0}]}\n\n'
        "Productos:\n" + "\n".join(f"- {p}" for p in productos)
    )


def interpretar_respuesta(texto: str, productos: list[str]) -> list[Propuesta]:
    """Valida la respuesta del modelo: categoría fuera de las cuatro → vacía; confianza acotada a [0, 1]."""
    try:
        items = json.loads(texto)["propuestas"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ValueError(f"Respuesta del modelo inválida: {error}") from error
    por_producto = {i.get("producto"): i for i in items if isinstance(i, dict)}
    propuestas = []
    for producto in productos:
        item = por_producto.get(producto, {})
        categoria = item.get("categoria", "")
        try:
            confianza = min(1.0, max(0.0, float(item.get("confianza", 0))))
        except (TypeError, ValueError):
            confianza = 0.0
        if categoria not in CATEGORIAS_VALIDAS:
            categoria, confianza = "", 0.0
        propuestas.append((producto, categoria, confianza))
    return propuestas


def proponer_llm(productos: list[str], cliente: Callable[[str], str]) -> list[Propuesta]:
    """`cliente` recibe el prompt y devuelve el texto de la respuesta (en los tests es un doble)."""
    return interpretar_respuesta(cliente(armar_prompt(productos)), productos)


def cliente_openai() -> Callable[[str], str]:
    clave, modelo = os.environ.get("OPENAI_API_KEY"), os.environ.get("MODELO_LLM")
    if not clave or not modelo:
        raise ValueError("Para --metodo llm hay que definir OPENAI_API_KEY y MODELO_LLM")

    def cliente(prompt: str) -> str:
        pedido = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({
                "model": modelo,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            }).encode(),
            headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(pedido, timeout=60) as respuesta:
            return json.load(respuesta)["choices"][0]["message"]["content"]

    return cliente


def leer_productos(ruta: Path) -> list[str]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if "producto" not in (lector.fieldnames or []):
            raise ValueError(f"{ruta} no tiene la columna 'producto'")
        return list(dict.fromkeys(fila["producto"] for fila in lector))


def escribir_propuestas(ruta: Path, propuestas: list[Propuesta]) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["producto", "categoria", "confianza"])
        escritor.writerows((p, c, f"{conf:.2f}") for p, c, conf in propuestas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propone categorías para productos (no modifica el catálogo).")
    parser.add_argument("entrada", type=Path, help="CSV con una columna 'producto'")
    parser.add_argument("--metodo", required=True, choices=["reglas", "llm"])
    parser.add_argument("--salida", required=True, type=Path)
    argumentos = parser.parse_args(argv)
    try:
        productos = leer_productos(argumentos.entrada)
        if argumentos.metodo == "reglas":
            propuestas = proponer_reglas(productos)
        else:
            propuestas = proponer_llm(productos, cliente_openai())
    except (OSError, ValueError) as error:
        parser.error(str(error))
    escribir_propuestas(argumentos.salida, propuestas)
    print(f"{len(propuestas)} productos, {sum(1 for p in propuestas if p[1])} con propuesta → {argumentos.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
