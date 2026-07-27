from app.core.database import engine, Base

from app.models.models import Usuario, Consecutivo, Cliente, Producto, Factura, FacturaDetalle

def init_db():
    print("Creando tablas en la base de datos de Supabase...")
    Base.metadata.create_all(bind=engine)
    print("¡Todas las tablas del MER han sido creadas exitosamente en PostgreSQL!")

if __name__ == "__main__":
    init_db()