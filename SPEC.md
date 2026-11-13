# Analizador de ventas — v2

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
- Los importes se informan redondeados a 2 decimales.

## Interfaz

Desde la raíz del repositorio:

```
uv run python -m ventas <archivo> [<archivo> ...] --salida <directorio>
```

- Crea `<directorio>` si no existe.
- Imprime un resumen legible por consola (formato libre).
- Termina con código de salida 0 si todo salió bien.

## Salidas

Sin cambios respecto de v1.

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

## Restricciones

- No modificar los archivos de entrada.
- Python ≥ 3.12, proyecto gestionado con `uv`.
- Ejecutar el programa solo con el CSV debe dar los mismos resultados que en v1.

## Criterios de aceptación

- Todos los criterios de v1 se siguen cumpliendo.
- Con `tests/aceptacion/datos/caso_minimo_online.json` (calculado a mano), solo o combinado con `caso_minimo.csv`, los resultados coinciden con los esperados.
- Combinar fuentes equivale a sumar sus resultados (facturación, tickets, meses).
- `uv run pytest` pasa sin errores.
