"""Modelos normalizados de ventas."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Venta:
    id_ticket: str
    fecha: date
    producto: str
    categoria: str
    cantidad: int
    precio_unitario: Decimal
    sucursal: str

    @property
    def importe(self) -> Decimal:
        return self.cantidad * self.precio_unitario

