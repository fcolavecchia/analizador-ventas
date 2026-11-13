# Analizador de ventas — v4

## Objetivo

Resumir las ventas del comercio combinando las ventas de los locales (CSV) y las ventas online (JSON).

## Entradas

El programa recibe uno o más archivos. El formato se determina por la extensión: `.csv` o `.json`.

### Ventas en local (`.csv`)

Archivo CSV con encabezado y estas columnas:

| Columna | Tipo | Ejemplo |
|---|---|---|
| `id_ticket` | texto | `T00042` |
| `fecha` | fecha `AAAA-MM-DD` | `2026-01-10` |
| `producto` | texto | `Mouse` |
| `categoria` | texto | `Periféricos` |
| `cantidad` | entero > 0 | `2` |
| `precio_unitario` | número > 0 | `12000` |
| `sucursal` | texto | `Centro` |

Cada fila es **una línea de un ticket**. Un ticket (una compra) puede tener varias filas con el mismo `id_ticket`.

### Ventas online (`.json`)

Una lista de órdenes. Cada orden tiene una lista de ítems:

```json
[
  {
    "order_id": "W-0001",
    "date": "2026-01-10T14:32:00",
    "status": "completed",
    "items": [
      {"item": "Mouse", "category": "Periféricos", "units": 1, "unit_price": 12600}
    ]
  }
]
```

Correspondencia con los campos del CSV:

| CSV | JSON |
|---|---|
| `id_ticket` | `order_id` |
| `fecha` | parte de fecha de `date` (sin conversión de zona horaria) |
| `producto` | `items[].item` |
| `categoria` | `items[].category` |
| `cantidad` | `items[].units` |
| `precio_unitario` | `items[].unit_price` |
| `sucursal` | siempre `Online` |

`status` puede ser `completed` o `cancelled`.

### Catálogo de categorías (`--catalogo`, opcional)

CSV con encabezado `producto,categoria`. Lo mantiene el equipo del comercio (no el programa). Cada producto
aparece una sola vez y su categoría es una de las categorías válidas. Si no se cumple, el programa termina con un
error claro.

## Categorías

Las únicas categorías válidas son estas cuatro:

| Categoría | Qué incluye |
|---|---|
| `Computación` | Equipos y componentes de computadora: notebooks, monitores, impresoras, discos, memorias, placas de video, routers, tablets. |
| `Audio` | Equipos que reproducen o capturan sonido: auriculares, parlantes, micrófonos, placas de sonido. |
| `Periféricos` | Dispositivos de entrada o captura que se conectan a la computadora: teclados, mouse, webcams, joysticks, tabletas digitalizadoras. |
| `Accesorios` | Complementos de otro equipo y consumibles: cables, adaptadores, hubs, soportes, fundas, cargadores, mousepads, pendrives, pilas. |

La categoría de cada línea se resuelve así, en este orden:

1. Si el producto está en el catálogo, se usa la categoría del catálogo (aunque la línea diga otra cosa).
2. Si no, se usa la categoría de la línea (`categoria` o `category`) si coincide con una válida **sin distinguir
   mayúsculas, tildes ni espacios al principio o al final** (`" perifericos"` → `Periféricos`).
3. Si no, la línea queda en la categoría **`Sin clasificar`** y el producto se informa en `revision.csv`.

La categoría solo afecta la facturación por categoría y `revision.csv`. Ninguna línea se descarta por su
categoría: la facturación total, los tickets, el mensual y el ranking no cambian.

## Definiciones

- **Importe de una línea** = `cantidad * precio_unitario`.
- **Facturación** = suma de los importes de las líneas.
- **Facturación mensual**: facturación agrupada por el mes de `fecha` (`AAAA-MM`). Solo se listan los meses con ventas.
- **Ticket** = un `id_ticket` distinto. **Cantidad de tickets** = cantidad de `id_ticket` distintos.
- **Ticket promedio** = facturación total / cantidad de tickets.
- **Productos más vendidos**: ranking por **unidades** (suma de `cantidad`), no por importe. Si dos productos tienen las mismas unidades, se ordenan alfabéticamente por nombre. Se informan los primeros 5.
- **Órdenes canceladas** (`status == "cancelled"`): se excluyen por completo. No suman facturación, ni unidades, ni cuentan como ticket.
- **Duplicados**: no se esperan. Los identificadores del CSV y del JSON no se superponen. No se deduplica.
- Los productos se identifican por nombre exacto en ambas fuentes.
- **Facturación por categoría**: facturación y unidades agrupadas por la categoría resuelta (ver
  *Categorías*), incluida `Sin clasificar` si hay líneas en esa situación. Se ordena por facturación
  descendente; si dos categorías facturan lo mismo, alfabéticamente por nombre. Solo se listan las categorías con
  ventas. Las órdenes canceladas no cuentan, igual que en el resto de los cálculos.
- Los importes se informan redondeados a 2 decimales.

## Interfaz

Desde la raíz del repositorio:

```
uv run python -m ventas <archivo> [<archivo> ...] --salida <directorio> [--catalogo <archivo>]
```

- Sin `--catalogo`, la resolución de categorías empieza en el paso 2.

- Crea `<directorio>` si no existe.
- Imprime un resumen legible por consola (formato libre).
- Termina con código de salida 0 si todo salió bien.

## Salidas

Las de v3, más `revision.csv`.

`<directorio>/mensual.csv`, ordenado por mes ascendente:

```
mes,facturacion
2026-01,840000.00
```

`<directorio>/resumen.json`:

```json
{
  "facturacion_total": 1550000.0,
  "cantidad_tickets": 5,
  "ticket_promedio": 310000.0,
  "top5_productos": [
    {"producto": "Cable USB", "unidades": 15}
  ]
}
```

`<directorio>/categorias.csv`, en el orden definido arriba:

```
categoria,facturacion,unidades
Computación,1300000.00,3
```

`<directorio>/revision.csv`: los pares distintos (producto, categoría original) de las líneas que quedaron en
`Sin clasificar`, ordenados por producto y después por categoría original. La categoría original es el texto
tal como vino en el archivo. Se escribe siempre; si no hay nada para revisar, queda solo el encabezado.

```
producto,categoria_original
Hub USB-C,
Soporte para monitor,Varios
```

## Herramienta de propuestas (fuera del análisis)

El programa **no** clasifica productos por su cuenta. Para ayudar a la persona que mantiene el catálogo hay una
herramienta aparte que **propone** categorías:

```
uv run python -m ventas.proponer <entrada.csv> --metodo reglas|llm --salida <propuestas.csv>
```

- `<entrada.csv>`: cualquier CSV con una columna `producto` (sirven `revision.csv` y
  `evaluacion/etiquetas.csv`). Las demás columnas se ignoran. Cada producto distinto se propone una vez.
- `<propuestas.csv>`: `producto,categoria,confianza`, en el orden en que aparecen los productos en la entrada.
  `categoria` es una de las cuatro válidas o queda vacía (sin propuesta). `confianza` es un número entre 0 y 1.
- `--metodo reglas`: palabras clave, sin red. Si ninguna regla aplica, `categoria` vacía y `confianza` 0.
- `--metodo llm`: un modelo de lenguaje vía la API de OpenAI. El modelo se toma de la variable de entorno
  `MODELO_LLM` y la clave de `OPENAI_API_KEY`. El modelo recibe la tabla de categorías de esta especificación y
  devuelve categoría y confianza para cada producto. Nunca recibe las etiquetas de `evaluacion/`.
- La herramienta no modifica el catálogo: una persona revisa las propuestas y actualiza el catálogo a mano.
- Los tests no llaman a la API.

La calidad de las propuestas se mide con el script del docente:

```
python3 evaluacion/evaluar.py evaluacion/etiquetas.csv <propuestas.csv> [--umbral 0.8]
```

## Restricciones

- No modificar los archivos de entrada.
- Python ≥ 3.12, proyecto gestionado con `uv`.
- Ejecutar el programa solo con el CSV debe dar los mismos resultados que en v1.
- Las fuentes de v1 a v3 dan los mismos resultados con o sin `--catalogo data/catalogo_categorias.csv`.

## Criterios de aceptación

- Todos los criterios de v1 se siguen cumpliendo.
- Con `tests/aceptacion/datos/caso_minimo_online.json` (calculado a mano), solo o combinado con `caso_minimo.csv`, los resultados coinciden con los esperados.
- Combinar fuentes equivale a sumar sus resultados (facturación, tickets, meses).
- Con los casos mínimos de `tests/aceptacion/datos/` (calculados a mano), `categorias.csv` coincide con lo esperado.
- La facturación por categoría suma la facturación total.
- Con `tests/aceptacion/datos/caso_oeste.csv` y `catalogo_minimo.csv` (calculados a mano), `categorias.csv` y
  `revision.csv` coinciden con lo esperado, con y sin catálogo.
- `uv run pytest` pasa sin errores, sin acceso a la red.
