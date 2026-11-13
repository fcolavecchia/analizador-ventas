"""Tests de la herramienta de propuestas. Sin red: el cliente del LLM es un doble."""

import json

from ventas.proponer import (
    armar_prompt,
    interpretar_respuesta,
    leer_productos,
    main,
    proponer_llm,
    proponer_reglas,
)


def test_reglas_proponen_o_dejan_vacio():
    assert proponer_reglas(["Auriculares inalámbricos", "Cosa rara"]) == [
        ("Auriculares inalámbricos", "Audio", 1.0),
        ("Cosa rara", "", 0.0),
    ]


def test_reglas_un_complemento_gana_sobre_el_equipo_que_nombra():
    por_producto = {p: c for p, c, _ in proponer_reglas(["Funda para notebook", "Tableta digitalizadora"])}
    assert por_producto["Funda para notebook"] == "Accesorios"
    assert por_producto["Tableta digitalizadora"] == "Periféricos"


def test_llm_usa_el_cliente_y_valida_la_respuesta():
    pedidos = []

    def cliente_falso(prompt):
        pedidos.append(prompt)
        return json.dumps({"propuestas": [
            {"producto": "A", "categoria": "Audio", "confianza": 0.9},
            {"producto": "B", "categoria": "Gaming", "confianza": 0.99},   # categoría inventada
            {"producto": "C", "categoria": "Audio", "confianza": 7},        # confianza fuera de rango
        ]})

    assert proponer_llm(["A", "B", "C", "D"], cliente_falso) == [
        ("A", "Audio", 0.9), ("B", "", 0.0), ("C", "Audio", 1.0), ("D", "", 0.0),
    ]
    assert "Accesorios" in pedidos[0] and "- A" in pedidos[0]


def test_respuesta_invalida_es_un_error():
    import pytest

    with pytest.raises(ValueError):
        interpretar_respuesta("no es json", ["A"])


def test_el_prompt_no_incluye_etiquetas_de_evaluacion():
    assert "etiquetas" not in armar_prompt(["A"]).lower()


def test_cli_reglas_escribe_propuestas_sin_duplicados(tmp_path):
    entrada = tmp_path / "e.csv"
    entrada.write_text("producto,otra\nMouse,x\nMouse,y\nHub USB-C,z\n", encoding="utf-8")
    assert leer_productos(entrada) == ["Mouse", "Hub USB-C"]
    salida = tmp_path / "p.csv"
    assert main([str(entrada), "--metodo", "reglas", "--salida", str(salida)]) == 0
    assert salida.read_text(encoding="utf-8").splitlines() == [
        "producto,categoria,confianza", "Mouse,Periféricos,1.00", "Hub USB-C,Accesorios,1.00",
    ]
