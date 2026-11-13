import json
from datetime import date
from decimal import Decimal

import pytest

from ventas.analisis import resumir
from ventas.entrada import cargar_ventas_archivo, cargar_ventas_json


def test_carga_json_normaliza_items_y_usa_fecha_local(tmp_path):
    ruta = tmp_path / "online.json"
    ruta.write_text(
        json.dumps(
            [
                {
                    "order_id": "W-1",
                    "date": "2026-01-02T00:30:00-08:00",
                    "status": "completed",
                    "items": [
                        {"item": "Mouse", "category": "Periféricos", "units": 2, "unit_price": 12.5}
                    ],
                },
                {
                    "order_id": "W-2",
                    "date": "2026-01-03T12:00:00",
                    "status": "cancelled",
                    "items": [
                        {"item": "Monitor", "category": "Computación", "units": 1, "unit_price": 99}
                    ],
                },
            ]
        ),
        encoding="utf-8",
    )

    ventas = cargar_ventas_json(ruta)

    assert len(ventas) == 1
    assert ventas[0].id_ticket == "W-1"
    assert ventas[0].fecha == date(2026, 1, 2)
    assert ventas[0].producto == "Mouse"
    assert ventas[0].categoria == "Periféricos"
    assert ventas[0].cantidad == 2
    assert ventas[0].precio_unitario == Decimal("12.5")
    assert ventas[0].sucursal == "Online"


@pytest.mark.parametrize(
    ("campo", "valor", "mensaje"),
    [("units", 0, "units debe ser mayor que cero"), ("unit_price", 0, "unit_price debe ser mayor que cero")],
)
def test_json_rechaza_unidades_o_precio_no_positivos(tmp_path, campo, valor, mensaje):
    item = {"item": "Mouse", "category": "Periféricos", "units": 1, "unit_price": 10}
    item[campo] = valor
    ruta = tmp_path / "online.json"
    ruta.write_text(
        json.dumps(
            [{"order_id": "W-1", "date": "2026-01-02T12:00:00", "status": "completed", "items": [item]}]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=mensaje):
        cargar_ventas_json(ruta)


def test_json_rechaza_status_desconocido_y_json_mal_formado(tmp_path):
    ruta = tmp_path / "online.json"
    ruta.write_text(
        json.dumps([{"order_id": "W-1", "date": "2026-01-02", "status": "pending", "items": []}]),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="status desconocido"):
        cargar_ventas_json(ruta)

    ruta.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON inválido"):
        cargar_ventas_json(ruta)


def test_fuente_sin_ventas_validas_aporta_lista_vacia(tmp_path):
    csv_vacio = tmp_path / "vacio.csv"
    csv_vacio.write_text(
        "id_ticket,fecha,producto,categoria,cantidad,precio_unitario,sucursal\n",
        encoding="utf-8",
    )
    json_cancelado = tmp_path / "cancelado.json"
    json_cancelado.write_text(
        json.dumps(
            [{"order_id": "W-1", "date": "2026-01-02", "status": "cancelled", "items": []}]
        ),
        encoding="utf-8",
    )

    assert cargar_ventas_archivo(csv_vacio) == []
    assert cargar_ventas_archivo(json_cancelado) == []


def test_combina_csv_y_json_en_un_mismo_analisis(tmp_path):
    csv_path = tmp_path / "local.csv"
    csv_path.write_text(
        "id_ticket,fecha,producto,categoria,cantidad,precio_unitario,sucursal\n"
        "T-1,2026-01-02,Mouse,Periféricos,1,10,Centro\n",
        encoding="utf-8",
    )
    json_path = tmp_path / "online.json"
    json_path.write_text(
        json.dumps(
            [{
                "order_id": "W-1",
                "date": "2026-02-02T12:00:00",
                "status": "completed",
                "items": [{"item": "Mouse", "category": "Periféricos", "units": 2, "unit_price": 5}],
            }]
        ),
        encoding="utf-8",
    )

    ventas_combinadas = cargar_ventas_archivo(csv_path) + cargar_ventas_archivo(json_path)
    resumen, mensual, _ = resumir(ventas_combinadas)

    assert resumen["facturacion_total"] == 20
    assert resumen["cantidad_tickets"] == 2
    assert resumen["top5_productos"] == [{"producto": "Mouse", "unidades": 3}]
    assert mensual == {"2026-01": Decimal("10.00"), "2026-02": Decimal("10.00")}


def test_rechaza_extension_no_admitida(tmp_path):
    with pytest.raises(ValueError, match="extensión debe ser .csv o .json"):
        cargar_ventas_archivo(tmp_path / "ventas.txt")
