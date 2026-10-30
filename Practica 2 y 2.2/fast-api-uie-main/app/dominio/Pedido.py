"""Pedidos realizados por los clientes."""

from datetime import datetime
from uuid import uuid4

from .Producto import Producto
from .Usuario import Cliente


class Pedido:
    """Agrupa un cliente y una lista de productos con sus cantidades."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    id: str
    fecha: datetime
    cliente: Cliente
    productos: list[tuple[Producto, int]]
    precios_unitarios: list[float]

    def __init__(
        self, cliente: Cliente, productos: list[tuple[Producto, int]]
    ) -> None:
        """Crea el pedido y conserva los precios del momento de compra."""
        if not isinstance(cliente, Cliente):
            raise ValueError("El pedido debe pertenecer a un cliente.")
        if not productos:
            raise ValueError("El pedido debe contener algún producto.")
        for producto, cantidad in productos:
            if not isinstance(producto, Producto):
                raise ValueError("El pedido contiene un producto incorrecto.")
            if type(cantidad) is not int or cantidad <= 0:
                raise ValueError("Las cantidades deben ser enteros positivos.")

        self.id = str(uuid4())
        self.fecha = datetime.now()
        self.cliente = cliente
        self.productos = productos.copy()
        self.precios_unitarios = []
        for producto, cantidad in self.productos:
            self.precios_unitarios.append(producto.precio)

    def calcular_total(self) -> float:
        """Suma el precio de compra por la cantidad de cada producto."""
        total: float = 0.0
        for indice, (producto, cantidad) in enumerate(self.productos):
            total += self.precios_unitarios[indice] * cantidad
        return round(total, 2)

    def __str__(self) -> str:
        """Devuelve un resumen del pedido, su cliente y su total."""
        return (
            f"Pedido {self.id} | Fecha: {self.fecha:%d/%m/%Y %H:%M:%S} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Total: {self.calcular_total():.2f} EUR"
        )
