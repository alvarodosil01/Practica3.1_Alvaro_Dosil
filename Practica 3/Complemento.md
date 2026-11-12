# Complemento de la práctica 2.2

EsEste documento explica las ampliaciones realizadas sobre fast-api-uie-main. Las instrucciones generales del ejemplo se encuentran en el README de esa carpeta.

1. Integración de la práctica 1

Se conservan el modelo Item, su almacenamiento en SQLite y sus endpoints originales. Sobre esa misma aplicación FastAPI se incorpora la tienda online de la práctica 1.

Las clases Producto, ProductoElectronico, ProductoRopa, Usuario, Cliente, Administrador y Pedido se encuentran en app/dominio/. Esta carpeta permite mantenerlas separadas del archivo app/models.py, que contiene el modelo SQLAlchemy del ejemplo.

La clase TiendaService, situada en app/Services/, conserva la lógica de registro de usuarios, inventario y pedidos.

## Integración de la tienda

Las clases `Producto`, `Usuario`, `Pedido` y sus especializaciones están en `app/dominio/`, para evitar conflictos con el archivo `app/models.py` del ejemplo. La lógica de negocio se mantiene en `TiendaService`.

Se añaden esquemas Pydantic y endpoints para gestionar usuarios, productos y pedidos. Al crear un pedido, el servicio comprueba las existencias, descuenta el stock y conserva el precio del momento de compra.

## Clientes de la API

- **`cliente/cliente.py`:** utiliza `requests` para crear un usuario, crear productos, realizar un pedido y consultar los listados y el historial. Comprueba los códigos HTTP y procesa las respuestas JSON.
- **`frontend/`:** permite gestionar la tienda desde el navegador. La función `api()` de `app.js` centraliza las peticiones con `fetch()` y el tratamiento de las respuestas.

Ambos clientes se comunican exclusivamente mediante HTTP. No importan `TiendaService` ni acceden directamente a los modelos del servidor. Se añade CORS para permitir que el frontend y la API funcionen en puertos locales distintos.

## Datos y simulación

La simulación crea dos productos y un pedido de **120 €**. Estos datos pueden consultarse también desde la web y `/docs`, mientras siga ejecutándose la misma API.

Los usuarios, productos y pedidos se guardan **en memoria** y se pierden al reiniciar el servidor. El archivo `test.db` sigue almacenando únicamente los `Item` del ejemplo original.

## Alcance

Esta versión incluye el cliente Python y el frontend con ejecución local. La prueba entre dos ordenadores indicada en el enunciado no se ha realizado.