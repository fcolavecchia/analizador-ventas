import json
from decimal import Decimal

import pytest

from ventas.lector import cargar_archivo, cargar_ventas_online


def test_carga_json_excluye_canceladas_y_normaliza_items(tmp_path):
    ruta = tmp_path / "ventas.json"
    ruta.write_text(json.dumps([
        {
            "order_id": "W1",
            "date": "2026-01-10T23:30:00-03:00",
            "status": "completed",
            "items": [{"item": "Mouse", "category": "Periféricos", "units": 2, "unit_price": 12000}],
        },
        {
            "order_id": "W2",
            "date": "2026-01-11T10:00:00",
            "status": "cancelled",
            "items": [{"item": "Notebook", "category": "Computación", "units": 1, "unit_price": 800000}],
        },
    ]), encoding="utf-8")

    ventas = cargar_ventas_online(ruta)

    assert len(ventas) == 1
    assert ventas[0].fecha.isoformat() == "2026-01-10"
    assert ventas[0].sucursal == "Online"
    assert ventas[0].importe == Decimal("24000")


def test_cargar_archivo_rechaza_extension_desconocida(tmp_path):
    ruta = tmp_path / "ventas.txt"
    ruta.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Formato no soportado"):
        cargar_archivo(ruta)
