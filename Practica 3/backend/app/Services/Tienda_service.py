"""Servicio central de usuarios, inventario y pedidos."""

from ..dominio.Pedido import Pedido
from ..dominio.Producto import Producto
from ..dominio.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Gestiona la tienda en memoria sin depender de la consola."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    usuarios: dict[str, Usuario]
    productos: dict[str, Producto]
    pedidos: list[Pedido]

    def __init__(self) -> None:
        """Inicializa los usuarios, el inventario y los pedidos."""
        self.usuarios = {}
        self.productos = {}
        self.pedidos = []

    def registrar_usuario(
        self, tipo: str, nombre: str, email: str, direccion: str = ""
    ) -> Usuario:
        """Crea y registra un cliente o un administrador según su tipo."""
        usuario: Usuario
        if tipo.lower() == "cliente":
            usuario = Cliente(nombre, email, direccion)
        elif tipo.lower() == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError("El tipo debe ser cliente o administrador.")
        self.usuarios[usuario.id] = usuario
        return usuario

    def agregar_producto(self, producto: Producto) -> None:
        """Añade un producto de cualquier categoría al inventario."""
        if not isinstance(producto, Producto):
            raise ValueError("Se debe proporcionar un objeto Producto.")
        if producto.id in self.productos:
            raise ValueError("El producto ya está en el inventario.")
        self.productos[producto.id] = producto

    def eliminar_producto(self, producto_id: str) -> None:
        """Elimina del inventario el producto con el identificador dado."""
        if producto_id not in self.productos:
            raise ValueError("El producto no existe.")
        del self.productos[producto_id]

    def listar_productos(self) -> list[Producto]:
        """Devuelve todos los productos del inventario y su stock actual."""
        return list(self.productos.values())

    def realizar_pedido(
        self, usuario_id: str, solicitudes: list[tuple[str, int]]
    ) -> Pedido:
        """Valida la compra completa, descuenta el stock y guarda el pedido."""
        if usuario_id not in self.usuarios:
            raise ValueError("El usuario no está registrado.")
        cliente = self.usuarios[usuario_id]
        if not isinstance(cliente, Cliente):
            raise ValueError("Solo los clientes pueden realizar pedidos.")
        if not solicitudes:
            raise ValueError("El pedido debe contener algún producto.")

        # Si un producto aparece varias veces, sumamos sus cantidades.
        cantidades: dict[str, int] = {}
        for producto_id, cantidad in solicitudes:
            if type(cantidad) is not int or cantidad <= 0:
                raise ValueError("Las cantidades deben ser enteros positivos.")
            if producto_id not in self.productos:
                raise ValueError("Uno de los productos no existe.")
            if producto_id in cantidades:
                cantidades[producto_id] += cantidad
            else:
                cantidades[producto_id] = cantidad

        # Se comprueba todo antes de modificar el inventario.
        lineas: list[tuple[Producto, int]] = []
        for producto_id, cantidad in cantidades.items():
            producto = self.productos[producto_id]
            if not producto.hay_stock(cantidad):
                raise ValueError(f"Stock insuficiente de {producto.nombre}.")
            lineas.append((producto, cantidad))

        pedido = Pedido(cliente, lineas)
        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        """Devuelve los pedidos del usuario de más antiguo a más reciente."""
        if usuario_id not in self.usuarios:
            raise ValueError("El usuario no está registrado.")
        pedidos_usuario: list[Pedido] = []
        for pedido in self.pedidos:
            if pedido.cliente.id == usuario_id:
                pedidos_usuario.append(pedido)
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
