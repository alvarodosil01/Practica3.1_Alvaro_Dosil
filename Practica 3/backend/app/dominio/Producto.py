"""Productos de la tienda y sus categorías."""

from math import isfinite
from uuid import uuid4


class Producto:
    """Representa un producto con precio y stock disponible."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    id: str
    nombre: str
    precio: float
    stock: int

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto con un identificador automático."""
        if not nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if not isfinite(precio) or precio < 0:
            raise ValueError("El precio debe ser un número finito no negativo.")
        if type(stock) is not int or stock < 0:
            raise ValueError("El stock debe ser un entero no negativo.")

        self.id = str(uuid4())
        self.nombre = nombre
        self.precio = round(float(precio), 2)
        self.stock = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si se puede atender una cantidad entera positiva."""
        if type(cantidad) is not int or cantidad <= 0:
            return False
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Suma reposiciones o resta compras sin permitir stock negativo."""
        if type(cantidad) is not int:
            raise ValueError("La variación del stock debe ser un entero.")
        if self.stock + cantidad < 0:
            raise ValueError("No hay stock suficiente.")
        self.stock += cantidad

    def __str__(self) -> str:
        """Devuelve las características principales del producto."""
        return (
            f"{self.nombre} | ID: {self.id} | "
            f"Precio: {self.precio:.2f} EUR | Stock: {self.stock}"
        )


class ProductoElectronico(Producto):
    """Producto que incluye una garantía en meses."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    garantia_meses: int

    def __init__(
        self, nombre: str, precio: float, stock: int, garantia_meses: int
    ) -> None:
        """Inicializa los atributos comunes y la garantía."""
        super().__init__(nombre, precio, stock)
        if type(garantia_meses) is not int or garantia_meses < 0:
            raise ValueError("La garantía debe ser un entero no negativo.")
        self.garantia_meses = garantia_meses

    def __str__(self) -> str:
        """Añade la garantía a la descripción heredada."""
        return f"{super().__str__()} | Garantía: {self.garantia_meses} meses"


class ProductoRopa(Producto):
    """Producto de ropa con talla y color."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    talla: str
    color: str

    def __init__(
        self, nombre: str, precio: float, stock: int, talla: str, color: str
    ) -> None:
        """Inicializa los atributos comunes, la talla y el color."""
        super().__init__(nombre, precio, stock)
        if not talla.strip() or not color.strip():
            raise ValueError("La talla y el color no pueden estar vacíos.")
        self.talla = talla
        self.color = color

    def __str__(self) -> str:
        """Añade la talla y el color a la descripción heredada."""
        return f"{super().__str__()} | Talla: {self.talla} | Color: {self.color}"
