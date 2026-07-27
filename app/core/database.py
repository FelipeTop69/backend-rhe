import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "ERROR: La variable DATABASE_URL no está definida en el archivo .env"
    )

# Crear el motor de SQLAlchemy para PostgreSQL
engine = create_engine(DATABASE_URL)

# Crear la fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán nuestros modelos (Tablas)
Base = declarative_base()


def get_db():
    """
    Inyección de dependencia para FastAPI.
    Abre una sesión de base de datos por cada petición y la cierra al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Código de prueba directo
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("¡Conexión exitosa a Supabase (PostgreSQL)!")
            print(f"Versión del servidor: {result.scalar()}")
    except Exception as e:  # noqa: BLE001
        print("Error al conectar con la base de datos:")
        print(e)