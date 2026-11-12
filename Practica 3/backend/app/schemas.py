from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Esquemas añadidos para la tienda de la Práctica 1.
"""Contratos de entrada y salida de la API, validados con Pydantic 2."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, model_validator

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
TipoProducto = Literal["generico", "electronico", "ropa"]


class Esquema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UsuarioCreate(Esquema):
    nombre: Texto
    email: EmailStr
    tipo: Literal["cliente", "administrador"]
    direccion: Texto | None = None

    @model_validator(mode="after")
    def validar_direccion(self) -> Self:
        if self.tipo == "cliente" and self.direccion is None:
            raise ValueError("Los clientes necesitan una dirección postal.")
        return self


class UsuarioRead(Esquema):
    id: str
    nombre: str
    email: str
    es_admin: bool


class ProductoCreate(Esquema):
    tipo: TipoProducto
    nombre: Texto
    precio: float = Field(ge=0, allow_inf_nan=False)
    stock: int = Field(ge=0, strict=True)
    meses_garantia: int | None = Field(default=None, ge=0, strict=True)
    talla: Texto | None = None
    color: Texto | None = None

    @model_validator(mode="after")
    def validar_categoria(self) -> Self:
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Un electrónico necesita meses_garantia.")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un electrónico no admite talla ni color.")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("La ropa necesita talla y color.")
            if self.meses_garantia is not None:
                raise ValueError("La ropa no admite meses_garantia.")
        elif any(valor is not None for valor in (self.meses_garantia, self.talla, self.color)):
            raise ValueError("Un producto genérico no admite atributos de otras categorías.")
        return self


class ProductoRead(Esquema):
    id: str
    tipo: TipoProducto
    nombre: str
    precio: float
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None


class PedidoItemCreate(Esquema):
    producto_id: Texto
    cantidad: int = Field(gt=0, strict=True)


class PedidoCreate(Esquema):
    cliente_id: Texto
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(Esquema):
    producto_id: str
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(Esquema):
    id: str
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: list[PedidoItemRead]
