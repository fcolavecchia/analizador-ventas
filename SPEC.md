# Analizador de ventas — v1

## Objetivo

Resumir las ventas de los locales del comercio a partir de un archivo CSV.

## Entrada

Un archivo CSV con encabezado y estas columnas:

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

## Definiciones

- **Importe de una línea** = `cantidad * precio_unitario`.
- **Facturación** = suma de los importes de las líneas.
- **Facturación mensual**: facturación agrupada por el mes de `fecha` (`AAAA-MM`). Solo se listan los meses con ventas.
- **Ticket** = un `id_ticket` distinto. **Cantidad de tickets** = cantidad de `id_ticket` distintos.
- **Ticket promedio** = facturación total / cantidad de tickets.
- **Productos más vendidos**: ranking por **unidades** (suma de `cantidad`), no por importe. Si dos productos tienen las mismas unidades, se ordenan alfabéticamente por nombre. Se informan los primeros 5.
- Los importes se informan redondeados a 2 decimales.

## Interfaz

Desde la raíz del repositorio:

```
uv run python -m ventas <archivo.csv> --salida <directorio>
```

- Crea `<directorio>` si no existe.
- Imprime un resumen legible por consola (formato libre).
- Termina con código de salida 0 si todo salió bien.

## Salidas

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

## Criterios de aceptación

- Con `tests/aceptacion/datos/caso_minimo.csv` (calculado a mano) los resultados coinciden con los esperados.
- La suma de la facturación mensual es igual a la facturación total.
- `uv run pytest` pasa sin errores.
