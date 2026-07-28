from sqlalchemy.orm import Session
from uuid import UUID

from app.models.models import Cliente, Producto, Factura, FacturaDetalle, Consecutivo
from app.schemas.schemas import ClienteCreate, ProductoCreate, FacturaCreate


# ==========================================
# 1. REPOSITORY: CONSECUTIVO
# ==========================================
class ConsecutivoRepository:
    @staticmethod
    def get_current(db: Session) -> Consecutivo:
        """Obtiene el registro actual del consecutivo. Si no existe, lo crea."""
        consecutivo = db.query(Consecutivo).first()
        if not consecutivo:
            consecutivo = Consecutivo(prefijo="CAJP-", numero_actual=112500)
            db.add(consecutivo)
            db.commit()
            db.refresh(consecutivo)
        return consecutivo

    @staticmethod
    def increment(db: Session, consecutivo: Consecutivo) -> Consecutivo:
        """Incrementa el número del consecutivo después de generar una factura."""
        consecutivo.numero_actual += 1
        db.commit()
        db.refresh(consecutivo)
        return consecutivo

    @staticmethod
    def update(db: Session, consecutivo_obj: Consecutivo, nuevo_prefijo: str, nuevo_numero: int) -> Consecutivo:
        """Actualiza el prefijo y el número de facturación."""
        consecutivo_obj.prefijo = nuevo_prefijo
        consecutivo_obj.numero_actual = nuevo_numero
        db.commit()
        db.refresh(consecutivo_obj)
        return consecutivo_obj


# ==========================================
# 2. REPOSITORY: CLIENTE
# ==========================================
class ClienteRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Cliente).all()

    @staticmethod
    def get_by_identificacion(db: Session, identificacion: str):
        return db.query(Cliente).filter(Cliente.identificacion == identificacion).first()

    @staticmethod
    def create(db: Session, cliente: ClienteCreate):
        db_cliente = Cliente(
            identificacion=cliente.identificacion,
            nombre=cliente.nombre
        )
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente


# ==========================================
# 3. REPOSITORY: PRODUCTO
# ==========================================
class ProductoRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Producto).all()

    @staticmethod
    def get_by_codigo(db: Session, codigo: str):
        return db.query(Producto).filter(Producto.codigo == codigo).first()

    @staticmethod
    def create(db: Session, producto: ProductoCreate):
        db_producto = Producto(
            codigo=producto.codigo,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base
        )
        db.add(db_producto)
        db.commit()
        db.refresh(db_producto)
        return db_producto


# ==========================================
# 4. REPOSITORY: FACTURA Y DETALLES
# ==========================================
class FacturaRepository:
    @staticmethod
    def create_factura(db: Session, factura_data: FacturaCreate, numero_factura_str: str):
        """
        Crea la cabecera de la factura y sus detalles en una sola transacción.
        """
        # 1. Crear Cabecera (Aún sin valor total)
        db_factura = Factura(
            numero_factura=numero_factura_str,
            hora_generacion=factura_data.hora_generacion,
            hora_expedicion=factura_data.hora_expedicion,
            valor_total=0.0,  # Se calcula en el siguiente paso
            cliente_id=factura_data.cliente_id,
            usuario_id=factura_data.usuario_id
        )
        db.add(db_factura)
        
        # Hacemos flush() para que PostgreSQL le asigne un ID (UUID) a la factura,
        # pero SIN hacer commit() todavía (protegiendo la transacción).
        db.flush()

        total_factura = 0.0

        # 2. Crear Detalles
        for detalle in factura_data.detalles:
            subtotal = detalle.cantidad * detalle.precio_aplicado
            total_factura += subtotal
            
            db_detalle = FacturaDetalle(
                factura_id=db_factura.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_aplicado=detalle.precio_aplicado,
                subtotal=subtotal
            )
            db.add(db_detalle)

        # 3. Actualizar el total en la cabecera
        db_factura.valor_total = total_factura

        # 4. Guardar todo definitivamente en la base de datos
        db.commit()
        db.refresh(db_factura)
        
        return db_factura