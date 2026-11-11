# Instrucciones para agentes

## Antes de cambiar código

- Leer `SPEC.md`: es el contrato de qué debe hacer el programa.
- Si un cambio afecta varias partes del código, proponer primero un plan breve y esperar aprobación.
- Si la especificación es ambigua o no cubre un caso, preguntar en lugar de decidir.

## Organización del código

- Paquete `ventas/`, ejecutable con `uv run python -m ventas`.
- Separar la lectura y normalización de datos de los cálculos de negocio.
  Los cálculos no deben saber de qué formato de archivo vinieron los datos.
- Dependencias: agregarlas con `uv add`, no con `pip`.

## Restricciones

- No modificar nada dentro de `data/`.
- No modificar `tests/aceptacion/`: son los tests del docente.
- Los tests propios van en `tests/` (fuera de `aceptacion/`).

## Verificación

- Escribir tests para las reglas nuevas.
- Ejecutar `uv run pytest` antes de dar una tarea por terminada.

## Al terminar, informar

- Archivos modificados.
- Pruebas ejecutadas y su resultado.
- Decisiones tomadas que no estaban en `SPEC.md` y preguntas pendientes.
