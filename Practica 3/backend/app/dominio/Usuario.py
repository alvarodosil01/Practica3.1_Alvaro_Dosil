"""Usuarios, clientes y administradores de la tienda."""

from uuid import uuid4


class Usuario:
    """Representa un usuario identificado por un UUID."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    id: str
    nombre: str
    email: str

    def __init__(self, nombre: str, email: str) -> None:
        """Guarda los datos básicos y genera un identificador."""
        if not nombre.strip() or not email.strip():
            raise ValueError("El nombre y el correo no pueden estar vacíos.")
        self.id = str(uuid4())
        self.nombre = nombre
        self.email = email

    def is_admin(self) -> bool:
        """Indica que un usuario común no es administrador."""
        return False


class Cliente(Usuario):
    """Usuario que puede realizar pedidos y tiene dirección postal."""

    # Tipos de los atributos de instancia; sus valores se asignan en __init__.
    direccion: str

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """Inicializa el usuario y añade su dirección postal."""
        super().__init__(nombre, email)
        if not direccion.strip():
            raise ValueError("La dirección postal no puede estar vacía.")
        self.direccion = direccion


class Administrador(Usuario):
    """Usuario que representa a un gestor de la tienda."""

    def is_admin(self) -> bool:
        """Sobrescribe el método para identificar al administrador."""
        return True
