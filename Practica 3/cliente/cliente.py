"""Cliente independiente: solo requests y biblioteca estándar, nunca app.*.

Ejemplo: python cliente.py --base-url http://127.0.0.1:8000
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


def validar_url(valor: str) -> str:
    valor = valor.strip().rstrip("/")
    partes = urlsplit(valor)
    if partes.scheme not in ("http", "https") or not partes.hostname or partes.username or partes.password or partes.query or partes.fragment:
        raise argparse.ArgumentTypeError("Usa una dirección HTTP(S), por ejemplo http://127.0.0.1:8000")
    return valor


class ClienteAPI:
    def __init__(self, base_url: str, timeout: float = 10):
        self.base_url = validar_url(base_url)
        self.timeout = timeout
        self.peticiones = []
        self.sesion = requests.Session()
        # Las peticiones locales de la práctica no pasan por proxies del sistema.
        self.sesion.trust_env = False

    def cerrar(self):
        self.sesion.close()

    def peticion(self, metodo: str, ruta: str, esperado: int, datos=None):
        """Envía HTTP, comprueba el estado y convierte la respuesta JSON."""
        respuesta = self.sesion.request(
            metodo, self.base_url + ruta, json=datos, timeout=self.timeout,
        )
        try:
            contenido = respuesta.json()
        except ValueError as exc:
            raise RuntimeError(f"{metodo} {ruta}: respuesta sin JSON válido (HTTP {respuesta.status_code}).") from exc
        self.peticiones.append({
            "metodo": metodo, "ruta": ruta, "estado": respuesta.status_code,
            "esperado": esperado, "respuesta": contenido,
        })
        print(f"{metodo:4} {ruta} -> HTTP {respuesta.status_code}")
        if respuesta.status_code != esperado:
            raise RuntimeError(f"Se esperaba HTTP {esperado}: {json.dumps(contenido, ensure_ascii=False)}")
        return contenido

    def demostrar(self):
        """Flujo mínimo exigido, seguido de comprobaciones de stock y errores."""
        usuario = self.peticion("POST", "/usuarios", 201, {
            "nombre": "Álvaro · cliente Python", "email": "alvaro.python@example.com",
            "tipo": "cliente", "direccion": "Calle Mayor, 1",
        })
        usuarios = self.peticion("GET", "/usuarios", 200)
        if not any(u["id"] == usuario["id"] for u in usuarios):
            raise RuntimeError("El usuario creado no aparece en el listado.")

        electronico = self.peticion("POST", "/productos", 201, {
            "tipo": "electronico", "nombre": "Auriculares ",
            "precio": 50, "stock": 10, "meses_garantia": 24,
        })
        ropa = self.peticion("POST", "/productos", 201, {
            "tipo": "ropa", "nombre": "Camiseta", "precio": 20,
            "stock": 8, "talla": "M", "color": "Azul",
        })
        productos = self.peticion("GET", "/productos", 200)
        if not {electronico["id"], ropa["id"]} <= {p["id"] for p in productos}:
            raise RuntimeError("Los productos creados no aparecen en el listado.")

        pedido = self.peticion("POST", "/pedidos", 201, {
            "cliente_id": usuario["id"],
            "items": [{"producto_id": electronico["id"], "cantidad": 2},
                      {"producto_id": ropa["id"], "cantidad": 1}],
        })
        historial = self.peticion("GET", f"/usuarios/{usuario['id']}/pedidos", 200)
        if pedido["total"] != 120 or not any(p["id"] == pedido["id"] for p in historial):
            raise RuntimeError("El total o el historial del pedido no es el esperado.")
        actualizado = self.peticion("GET", f"/productos/{electronico['id']}", 200)
        if actualizado["stock"] != 8:
            raise RuntimeError("El stock no se ha actualizado correctamente.")

        # Los errores esperados también tienen un código HTTP y una respuesta JSON.
        self.peticion("POST", "/pedidos", 400, {
            "cliente_id": usuario["id"],
            "items": [{"producto_id": electronico["id"], "cantidad": 100}],
        })
        self.peticion("GET", "/productos/no-existe", 404)
        self.peticion("POST", "/pedidos", 422, {"cliente_id": usuario["id"], "items": []})
        return {"usuario_id": usuario["id"], "pedido_id": pedido["id"], "total": pedido["total"]}


def main():
    parser = argparse.ArgumentParser(description="Prueba la tienda exclusivamente mediante HTTP.")
    parser.add_argument("--base-url", type=validar_url, default=BASE_URL, help="URL de FastAPI; también admite la variable BASE_URL.")
    parser.add_argument("--timeout", type=float, default=10, help="Tiempo máximo por petición, en segundos.")
    parser.add_argument("--salida", type=Path, help="Guarda un informe JSON de las peticiones realizadas.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout debe ser positivo.")
    cliente = ClienteAPI(args.base_url, args.timeout)
    informe = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "base_url": cliente.base_url}
    print(f"Servidor: {cliente.base_url}\n")
    codigo = 0
    try:
        informe["resultado"] = cliente.demostrar()
        informe["correcto"] = True
        print("\nFlujo completado: usuario, productos, pedido e historial. Total: 120 EUR.")
        print("Los datos ya pueden consultarse desde /docs y desde el frontend.")
    except (requests.RequestException, RuntimeError, KeyError, TypeError, ValueError) as exc:
        informe.update(correcto=False, error=str(exc))
        print(f"\nNo se pudo completar la prueba: {exc}", file=sys.stderr)
        codigo = 1
    finally:
        cliente.cerrar()
        informe["peticiones"] = cliente.peticiones
    if args.salida:
        try:
            args.salida.parent.mkdir(parents=True, exist_ok=True)
            args.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            print(f"No se pudo guardar el informe: {exc}", file=sys.stderr)
            codigo = 1
    return codigo


if __name__ == "__main__":
    sys.exit(main())
