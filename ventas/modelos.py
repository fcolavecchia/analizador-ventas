"""Tipos normalizados que usa la lógica de negocio."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Venta:
    id_ticket: str
    fecha: date
    producto: str
    categoria: str
    cantidad: int
    precio_unitario: float
    sucursal: str

    @property
    def importe(self) -> float:
        return self.cantidad * self.precio_unitario
