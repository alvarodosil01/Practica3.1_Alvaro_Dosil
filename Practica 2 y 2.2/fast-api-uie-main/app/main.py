from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# Crear la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependencia para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints CRUD
@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 10, name: str | None = None, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit, name=name)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    result = crud.delete_item(db, item_id=item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found in database")
    return {"message": "Item removed successfully"}


# Endpoints añadidos para la tienda online de la Práctica 1.
"""Punto de entrada y endpoints, siguiendo el ejemplo fast-api-uie-main."""

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from . import crud, schemas

@app.exception_handler(crud.NoEncontrado)
async def recurso_no_encontrado(request: Request, exc: crud.NoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def operacion_invalida(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.post("/usuarios", response_model=schemas.UsuarioRead, status_code=201, tags=["Usuarios"])
def crear_usuario(datos: schemas.UsuarioCreate):
    return crud.crear_usuario(datos)


@app.get("/usuarios", response_model=list[schemas.UsuarioRead], tags=["Usuarios"])
def listar_usuarios():
    return crud.listar_usuarios()


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioRead, tags=["Usuarios"], responses={404: {"description": "Usuario inexistente"}})
def obtener_usuario(usuario_id: str):
    return crud.obtener_usuario(usuario_id)


@app.post("/productos", response_model=schemas.ProductoRead, status_code=201, tags=["Productos"])
def crear_producto(datos: schemas.ProductoCreate):
    return crud.crear_producto(datos)


@app.get("/productos", response_model=list[schemas.ProductoRead], tags=["Productos"])
def listar_productos():
    return crud.listar_productos()


@app.get("/productos/{producto_id}", response_model=schemas.ProductoRead, tags=["Productos"], responses={404: {"description": "Producto inexistente"}})
def obtener_producto(producto_id: str):
    return crud.obtener_producto(producto_id)


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"], responses={404: {"description": "Producto inexistente"}})
def eliminar_producto(producto_id: str):
    crud.eliminar_producto(producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/pedidos", response_model=schemas.PedidoRead, status_code=201, tags=["Pedidos"], responses={400: {"description": "Compra no válida o stock insuficiente"}, 404: {"description": "Cliente o producto inexistente"}})
def crear_pedido(datos: schemas.PedidoCreate):
    return crud.crear_pedido(datos)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[schemas.PedidoRead], tags=["Pedidos"], responses={400: {"description": "El usuario no es cliente"}, 404: {"description": "Cliente inexistente"}})
def listar_pedidos(cliente_id: str):
    return crud.listar_pedidos(cliente_id)


# P2_2: permite al frontend, servido por separado, consumir la misma API.
# El frontend y la API se ejecutan en este mismo ordenador, en puertos distintos.
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
