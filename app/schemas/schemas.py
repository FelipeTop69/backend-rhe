from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ==========================================
# 1. SCHEMAS: USUARIO
# ==========================================
class UsuarioBase(BaseModel):
    username: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: UUID

    class Config:
        from_attributes = True


# ==========================================
# 2. SCHEMAS: CONSECUTIVO
# ==========================================
class ConsecutivoBase(BaseModel):
    prefijo: str = "CAJP-"
    numero_actual: int = Field(..., ge=1, description="El número debe ser mayor o igual a 1")

class ConsecutivoResponse(ConsecutivoBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# 3. SCHEMAS: CLIENTE
# ==========================================
class ClienteBase(BaseModel):
    identificacion: str = Field(..., min_length=3, description="NIT o CC del cliente")
    nombre: str = Field(..., min_length=2, description="Nombre o razón social")

    @field_validator('nombre')
    @classmethod
    def a_mayusculas(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator('identificacion')
    @classmethod
    def limpiar_identificacion(cls, v: str) -> str:
        # Si el usuario digita comas o puntos por error, los limpiamos
        return v.replace(".", "").replace(",", "").strip()

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: UUID

    class Config:
        from_attributes = True


# ==========================================
# 4. SCHEMAS: PRODUCTO
# ==========================================
class ProductoBase(BaseModel):
    codigo: str = Field(..., min_length=1, description="Código del producto")
    descripcion: str = Field(..., min_length=2, description="Descripción del producto")
    precio_base: float = Field(..., gt=0, description="Precio unitario base (mayor a 0)")

    @field_validator('descripcion')
    @classmethod
    def a_mayusculas(cls, v: str) -> str:
        return v.upper().strip()

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: UUID

    class Config:
        from_attributes = True


# ==========================================
# 5. SCHEMAS: FACTURA DETALLE (INTERMEDIA)
# ==========================================
class FacturaDetalleCreate(BaseModel):
    producto_id: UUID
    cantidad: float = Field(..., gt=0, description="La cantidad debe ser mayor a 0")
    precio_aplicado: float = Field(..., gt=0, description="Precio de venta unitario")

class FacturaDetalleResponse(BaseModel):
    id: UUID
    producto_id: UUID
    cantidad: float
    precio_aplicado: float
    subtotal: float
    producto: Optional[ProductoResponse] = None

    class Config:
        from_attributes = True


# ==========================================
# 6. SCHEMAS: FACTURA (CABECERA)
# ==========================================
class FacturaCreate(BaseModel):
    cliente_id: UUID
    usuario_id: UUID
    hora_generacion: time
    hora_expedicion: time
    # Regla de negocio: Máximo 3 ítems por factura según la plantilla
    detalles: List[FacturaDetalleCreate] = Field(
        ..., min_items=1, max_items=3, description="Lista de 1 a 3 productos"
    )

class FacturaResponse(BaseModel):
    id: UUID
    numero_factura: str
    fecha_emision: date
    hora_generacion: time
    hora_expedicion: time
    valor_total: float
    cliente: ClienteResponse
    usuario: UsuarioResponse
    detalles: List[FacturaDetalleResponse]

    class Config:
        from_attributes = True