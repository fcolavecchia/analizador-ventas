#!/usr/bin/env bash
# Falla si hay cambios en archivos que solo modifica el docente (ver AGENTS.md).
#
# Uso:
#     scripts/verificar_intocables.sh          # cambios en el staging (hook pre-commit)
#     scripts/verificar_intocables.sh <base>   # cambios de HEAD respecto de <base> (CI)
set -euo pipefail

PROTEGIDOS=(data tests/aceptacion revision evaluacion)

if [ $# -eq 0 ]; then
    cambios=$(git diff --cached --name-only -- "${PROTEGIDOS[@]}")
else
    cambios=$(git diff --name-only "$1"...HEAD -- "${PROTEGIDOS[@]}")
fi

if [ -n "$cambios" ]; then
    echo "Estos archivos los modifica solo el docente (ver AGENTS.md):"
    echo "$cambios" | sed 's/^/    /'
    exit 1
fi
