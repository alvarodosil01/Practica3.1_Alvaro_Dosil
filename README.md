# Tienda online

**Autor:** [Álvaro Dosil Pérez]

Aplicación desarrollada en Python para gestionar una tienda online. Permite registrar usuarios, gestionar productos y realizar pedidos con control de stock.

## Tecnologías

- Python y FastAPI.
- Requests para el cliente Python.
- HTML, CSS y JavaScript para la interfaz web.

## Estructura

- `fast-api-uie-main/`: API y lógica de la tienda. (Practica 02)
- `cliente/`: cliente Python que consume la API.(Practica 2.2 )
- `frontend/`: interfaz web.(Practica 2.2)


## Almacenamiento

Los usuarios, productos y pedidos se guardan en memoria y se pierden al reiniciar la API.

## Docker

Los siguientes comandos se ejecutan desde `Practica 2 y 2.2`, donde están el
Dockerfile y el `.dockerignore`.

### Construir la imagen

```powershell
docker build -t tienda-api -f dockerfile .
```

### Ejecutar la API

En primer plano:

```powershell
docker run --rm -p 8000:8000 --name tienda-api tienda-api
```

O en segundo plano:

```powershell
docker run -d -p 8000:8000 --name tienda-api tienda-api
docker logs -f tienda-api
```

Para detener el contenedor en segundo plano:

```powershell
docker stop tienda-api
```

La API queda disponible en `http://localhost:8000` y su documentación
interactiva en `http://localhost:8000/docs`. El contenedor no requiere
variables de entorno.

### Probar el cliente y el frontend

El cliente Python y la interfaz web se ejecutan fuera del contenedor de la API,
pero se conectan a su puerto publicado. Con la API en marcha, desde otra
terminal situada en `Practica 2 y 2.2`, ejecuta el cliente:

```powershell
python -m pip install -r cliente/requirements.txt
python cliente/cliente.py --base-url http://127.0.0.1:8000
```

El cliente también admite `BASE_URL` (por defecto
`http://127.0.0.1:8000`); `--base-url` permite indicar la dirección
explícitamente. Por ejemplo, en PowerShell:

```powershell
$env:BASE_URL = "http://127.0.0.1:8000"
python cliente/cliente.py
```

El cliente crea un usuario, dos productos y un pedido de 120 euros, y comprueba
el stock y respuestas HTTP esperadas. Al finalizar correctamente imprime:

```text
Flujo completado: usuario, productos, pedido e historial. Total: 120 EUR.
Los datos ya pueden consultarse desde /docs y desde el frontend.
```

Para servir la interfaz desde otra terminal:

```powershell
python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Abre `http://127.0.0.1:8080` y conecta al servidor
`http://127.0.0.1:8000`. También puedes probar `GET /usuarios` y
`GET /productos` en `http://localhost:8000/docs`. Los usuarios, productos y
pedidos se guardan en memoria y se pierden al reiniciar la API.
