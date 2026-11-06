# Tienda online

**Autor:** Álvaro Dosil Pérez

Aplicación para gestionar una tienda online. Permite registrar usuarios, gestionar productos y realizar pedidos con control de stock.

## Tecnologías

- Python y FastAPI para la API.
- HTML, CSS y JavaScript para la interfaz web.
- Requests para el cliente Python de simulación.
- Docker y Docker Compose para ejecutar el backend y el frontend.

## Estructura

```text
Practica 2 y 2.2/
├── compose.yaml             # Arranque conjunto de backend y frontend
├── dockerfile               # Imagen del backend
├── .dockerignore
├── requirements.txt
├── Complemento.md
├── fast-api-uie-main/       # API y lógica de la tienda
│   ├── app/
│   └── requirements.txt
├── frontend/               # Interfaz web y su imagen Docker
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── dockerfile
│   └── .dockerignore
└── cliente/                # Cliente de simulación independiente
    ├── cliente.py
    └── requirements.txt
```

## Ejecutar con Docker Compose

Docker instalado y en ejecución, con Docker Compose disponible. 

Desde la raíz del repositorio:

```powershell
cd "Practica 2 y 2.2"
docker compose up --build
```

Compose construye las imágenes y arranca dos servicios:

| Servicio | Función | Acceso desde el equipo |
| --- | --- | --- |
| `backend` | Ejecuta FastAPI con Uvicorn | http://localhost:8000 |
| `frontend` | Sirve HTML, CSS y JavaScript con el servidor HTTP de Python | http://localhost:8080 |

Abre la [tienda](http://localhost:8080). El campo **Servidor de la tienda** debe apuntar a `http://127.0.0.1:8000` o `http://localhost:8000`. Si tenías otra dirección guardada, cámbiala y pulsa **Conectar**.

El JavaScript se ejecuta en el navegador y accede al puerto publicado de la API. La dirección `backend:8000` es interna de Docker y no se utiliza en ese campo.

La documentación interactiva de la API está en [Swagger UI](http://localhost:8000/docs).

Para ejecutar los servicios en segundo plano:

```powershell
docker compose up --build -d
```

Para consultar el estado y los registros:

```powershell
docker compose ps
docker compose logs -f
```

Para detener y eliminar los contenedores, desde la misma carpeta:

```powershell
docker compose down
```

## Ejecutar el cliente simulado

El cliente `cliente/cliente.py` **no se ejecuta automáticamente con Compose**. Es un script independiente que consume la API mediante HTTP y comprueba el funcionamiento de la tienda. El frontend puede utilizarse sin ejecutar este cliente.

Con los servicios en marcha, abre otra terminal en `Practica 2 y 2.2`. Necesitas Python y pip instalados en tu equipo:

```powershell
python -m pip install -r cliente/requirements.txt
python cliente/cliente.py --base-url http://127.0.0.1:8000
```

La simulación:

- Crea un usuario y dos productos.
- Realiza un pedido de **120 €**.
- Consulta los listados y el historial de pedidos.
- Comprueba la actualización del stock y las respuestas de error esperadas.

Al terminar correctamente muestra:

```text
Flujo completado: usuario, productos, pedido e historial. Total: 120 EUR.
Los datos ya pueden consultarse desde /docs y desde el frontend.
```

Pulsa **Actualizar** en la interfaz web para ver los usuarios y productos creados. En la sección de pedidos puedes consultar el historial del cliente. Cada ejecución añade nuevos datos a la API en marcha.

También puedes configurar la dirección mediante la variable `BASE_URL`. Ejemplo en PowerShell:

```powershell
$env:BASE_URL = "http://127.0.0.1:8000"
python cliente/cliente.py
```

El argumento `--base-url` tiene prioridad sobre esa variable.

## Almacenamiento

Los usuarios, productos y pedidos de la tienda se guardan **en memoria** y se pierden al reiniciar la API. Docker Compose no cambia este comportamiento.

El CRUD original de `items` utiliza SQLite (`test.db`), separado de los datos de la tienda. La configuración actual no monta un volumen: la base de datos creada dentro del contenedor se pierde al eliminarlo o sustituirlo.
