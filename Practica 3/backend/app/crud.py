from sqlalchemy.orm import Session

from . import models, schemas


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()
    
def get_items(db: Session, skip: int = 0, limit: int = 10, name: str | None = None):
    query = db.query(models.Item)
    if name is not None:
        query = query.filter(models.Item.name == name)
    return query.offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


# Integración de TiendaService (Práctica 1).
"""Adaptación entre los esquemas HTTP y la lógica de la Práctica 1.

Sigue el papel de crud.py del material FastAPI. Aquí las operaciones se
delegan en TiendaService y los datos se guardan en memoria, sin SQLAlchemy.
"""

from threading import RLock

from . import schemas
from .Services.Tienda_service import TiendaService
from .dominio.Pedido import Pedido
from .dominio.Producto import Producto, ProductoElectronico, ProductoRopa
from .dominio.Usuario import Cliente, Usuario

tienda = TiendaService()
# Una compra comprueba y descuenta stock sin intercalarse con otra petición.
_lock = RLock()


class NoEncontrado(ValueError):
    """Identificador que no corresponde a un recurso existente."""


def usuario_read(usuario: Usuario) -> schemas.UsuarioRead:
    return schemas.UsuarioRead(
        id=usuario.id, nombre=usuario.nombre,
        email=usuario.email, es_admin=usuario.is_admin(),
    )


def producto_read(producto: Producto) -> schemas.ProductoRead:
    tipo = "generico"
    extras = {}
    if isinstance(producto, ProductoElectronico):
        tipo = "electronico"
        extras["meses_garantia"] = producto.garantia_meses
    elif isinstance(producto, ProductoRopa):
        tipo = "ropa"
        extras.update(talla=producto.talla, color=producto.color)
    return schemas.ProductoRead(
        id=producto.id, tipo=tipo, nombre=producto.nombre,
        precio=producto.precio, stock=producto.stock, **extras,
    )


def pedido_read(pedido: Pedido) -> schemas.PedidoRead:
    items = []
    for (producto, cantidad), precio in zip(pedido.productos, pedido.precios_unitarios):
        items.append(schemas.PedidoItemRead(
            producto_id=producto.id, nombre=producto.nombre, cantidad=cantidad,
            precio_unitario=precio, subtotal=round(precio * cantidad, 2),
        ))
    return schemas.PedidoRead(
        id=pedido.id, fecha=pedido.fecha, cliente=usuario_read(pedido.cliente),
        total=pedido.calcular_total(), items=items,
    )


def _usuario(usuario_id: str) -> Usuario:
    if usuario_id not in tienda.usuarios:
        raise NoEncontrado("El usuario no existe.")
    return tienda.usuarios[usuario_id]


def _producto(producto_id: str) -> Producto:
    if producto_id not in tienda.productos:
        raise NoEncontrado("El producto no existe.")
    return tienda.productos[producto_id]


def crear_usuario(datos: schemas.UsuarioCreate) -> schemas.UsuarioRead:
    with _lock:
        usuario = tienda.registrar_usuario(
            datos.tipo, datos.nombre, str(datos.email), datos.direccion or "",
        )
        return usuario_read(usuario)


def obtener_usuario(usuario_id: str) -> schemas.UsuarioRead:
    with _lock:
        return usuario_read(_usuario(usuario_id))


def listar_usuarios() -> list[schemas.UsuarioRead]:
    with _lock:
        return [usuario_read(usuario) for usuario in tienda.usuarios.values()]


def crear_producto(datos: schemas.ProductoCreate) -> schemas.ProductoRead:
    with _lock:
        argumentos = (datos.nombre, datos.precio, datos.stock)
        if datos.tipo == "electronico":
            producto = ProductoElectronico(*argumentos, datos.meses_garantia)
        elif datos.tipo == "ropa":
            producto = ProductoRopa(*argumentos, datos.talla, datos.color)
        else:
            producto = Producto(*argumentos)
        tienda.agregar_producto(producto)
        return producto_read(producto)


def listar_productos() -> list[schemas.ProductoRead]:
    with _lock:
        return [producto_read(producto) for producto in tienda.listar_productos()]


def obtener_producto(producto_id: str) -> schemas.ProductoRead:
    with _lock:
        return producto_read(_producto(producto_id))


def eliminar_producto(producto_id: str) -> None:
    with _lock:
        _producto(producto_id)
        tienda.eliminar_producto(producto_id)


def crear_pedido(datos: schemas.PedidoCreate) -> schemas.PedidoRead:
    with _lock:
        _usuario(datos.cliente_id)
        for item in datos.items:
            _producto(item.producto_id)
        pedido = tienda.realizar_pedido(
            datos.cliente_id, [(item.producto_id, item.cantidad) for item in datos.items],
        )
        return pedido_read(pedido)


def listar_pedidos(cliente_id: str) -> list[schemas.PedidoRead]:
    with _lock:
        if not isinstance(_usuario(cliente_id), Cliente):
            raise ValueError("El usuario debe ser un cliente.")
        return [pedido_read(pedido) for pedido in tienda.listar_pedidos_usuario(cliente_id)]
