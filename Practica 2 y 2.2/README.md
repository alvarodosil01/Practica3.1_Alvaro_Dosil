# Práctica 2.2 · Tienda online

Proyecto basado en fast-api-uie-main y la tienda de la Práctica 1.
Contiene el backend FastAPI, el cliente Python con requests y el frontend web.

## Instalación

Requiere Python 3.11 o posterior. Desde esta carpeta P2_2, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecución local

Abre tres terminales, inicialmente situadas en esta carpeta P2_2.

Terminal 1: iniciar la API y mantenerla abierta.

```powershell
cd fast-api-uie-main
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2: ejecutar la simulación.

```powershell
.venv\Scripts\python.exe cliente\cliente.py --base-url http://127.0.0.1:8000
```

Terminal 3: iniciar la web y mantenerla abierta.

```powershell
.venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

- Tienda: http://127.0.0.1:8080
- Documentación interactiva: http://127.0.0.1:8000/docs
- Pulsa Actualizar en la web para ver los datos creados por el cliente Python.
- Para detener los servidores, pulsa Ctrl+C en sus terminales.

La simulación crea un usuario, dos productos y un pedido de 120 euros.
Comprueba las listas, el historial, el stock, los códigos HTTP y las respuestas
JSON, incluidos errores esperados 400, 404 y 422. Cada ejecución genera nuevos
recursos. La dirección base puede cambiarse con --base-url o BASE_URL.

## Comunicación con la API

El cliente Python no importa el servidor. En cliente/cliente.py, la función
ClienteAPI.peticion() envía las peticiones con requests.Session.request(),
comprueba status_code y procesa json(). demostrar() ejecuta el recorrido.

En frontend/app.js, api() centraliza fetch(), los métodos HTTP, JSON.stringify(),
la comprobación de response.status y response.json(). Los formularios llaman
a api() y las funciones de presentación muestran las respuestas recibidas.

| Operación | Endpoint |
|---|---|
| Crear/listar usuarios | POST /usuarios, GET /usuarios |
| Crear/listar productos | POST /productos, GET /productos |
| Crear pedido | POST /pedidos |
| Consultar historial | GET /usuarios/{cliente_id}/pedidos |

La web permite las cinco operaciones mínimas del enunciado y también crear
usuarios. Su dirección base se modifica en el campo «Servidor de la tienda».
FastAPI incluye CORS para permitir las llamadas desde los puertos locales.

Los tres clientes (/docs, Python y web) comparten los datos de la misma API.
Usuarios, productos y pedidos están en memoria y se vacían al reiniciar el
servidor. Los Item del ejemplo original se conservan en SQLite (test.db).
Se mantienen los endpoints originales /items y la lógica de TiendaService.

## Alcance

Se incluyen el cliente Python y el frontend con funcionamiento local.
La prueba entre dos ordenadores de la Parte 2 del enunciado no se ha realizado
ni se incluye como completada en esta entrega.
