import uuid
from datetime import date, time  # noqa: F401

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# 1. Modelo Usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Relación 1 -> N con Facturas
    facturas = relationship("Factura", back_populates="usuario")


# 2. Modelo Consecutivo
class Consecutivo(Base):
    __tablename__ = "consecutivos"

    id = Column(Integer, primary_key=True, index=True)
    prefijo = Column(String, nullable=False, default="CAJP-")
    numero_actual = Column(Integer, nullable=False, default=112500)


# 3. Modelo Cliente
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identificacion = Column(String, unique=True, nullable=False, index=True) # NIT o CC
    nombre = Column(String, nullable=False)

    # Relación 1 -> N con Facturas
    facturas = relationship("Factura", back_populates="cliente")


# 4. Modelo Producto
class Producto(Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, nullable=False)
    precio_base = Column(Float, nullable=False)

    # Relación 1 -> N con FacturaDetalle
    detalles = relationship("FacturaDetalle", back_populates="producto")


# 5. Modelo Factura (Cabecera)
class Factura(Base):
    __tablename__ = "facturas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_factura = Column(String, unique=True, nullable=False, index=True) # Ej: CAJP-112500
    fecha_emision = Column(Date, nullable=False, default=date.today)
    hora_generacion = Column(Time, nullable=False)
    hora_expedicion = Column(Time, nullable=False)
    valor_total = Column(Float, nullable=False)

    # Llaves foráneas
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    cliente = relationship("Cliente", back_populates="facturas")
    usuario = relationship("Usuario", back_populates="facturas")
    detalles = relationship("FacturaDetalle", back_populates="factura", cascade="all, delete-orphan")


# 6. Modelo FacturaDetalle (Intermedia)
class FacturaDetalle(Base):
    __tablename__ = "factura_detalles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cantidad = Column(Float, nullable=False)
    precio_aplicado = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Llaves foráneas
    factura_id = Column(UUID(as_uuid=True), ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False)

    # Relaciones
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")