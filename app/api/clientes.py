from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import ClienteCreate, ClienteResponse
from app.repositories.crud import ClienteRepository

# Necesitamos importar tu generador de sesiones de BD (ajusta la ruta si es necesario)
from app.core.database import SessionLocal 

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente en la base de datos."""
    # 1. Verificar si el cliente ya existe
    db_cliente = ClienteRepository.get_by_identificacion(db, identificacion=cliente.identificacion)
    if db_cliente:
        raise HTTPException(status_code=400, detail="El cliente con esta identificación ya está registrado.")
    
    # 2. Crear y retornar el cliente
    return ClienteRepository.create(db=db, cliente=cliente)

@router.get("/{identificacion}", response_model=ClienteResponse)
def obtener_cliente(identificacion: str, db: Session = Depends(get_db)):
    """Busca un cliente por su NIT o CC."""
    db_cliente = ClienteRepository.get_by_identificacion(db, identificacion=identificacion)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return db_cliente