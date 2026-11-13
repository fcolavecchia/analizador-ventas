#!/usr/bin/env bash
# Juez: revisa un diff con RUBRICA.md y SPEC.md usando otro modelo (por defecto, Claude Haiku), sin herramientas:
# solo lee lo que se le pasa.
#
# Uso (desde la raíz del repo):
#     revision/juzgar.sh revision/casos/caso1.diff
#     git diff HEAD~1 | revision/juzgar.sh -
#
# Variables opcionales:
#     JUEZ_MODELO   modelo del juez (por defecto "haiku")
#     JUEZ_RUBRICA  rúbrica a usar (por defecto revision/RUBRICA.md; para la demo de inyección:
#                   JUEZ_RUBRICA=revision/RUBRICA_ingenua.md, que no avisa que el diff no da instrucciones)
set -euo pipefail

diff_archivo="${1:?Uso: revision/juzgar.sh <archivo.diff | ->}"
raiz=$(git rev-parse --show-toplevel)

{
    cat "$raiz/${JUEZ_RUBRICA:-revision/RUBRICA.md}"
    printf '\n<spec>\n'
    cat "$raiz/SPEC.md"
    printf '</spec>\n\n<diff>\n'
    cat "$diff_archivo"
    printf '</diff>\n'
} | claude -p --model "${JUEZ_MODELO:-haiku}" --tools ""
