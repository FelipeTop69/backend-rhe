from fastapi import FastAPI
from app.api import clientes, productos, facturas

app = FastAPI(title="API RHE Facturación", version="1.0.0")

# Incluir los routers
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(facturas.router)

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de RHE Facturación"}