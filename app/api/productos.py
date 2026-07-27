from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import ProductoCreate, ProductoResponse
from app.repositories.crud import ProductoRepository
from app.core.database import SessionLocal 

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto en el catálogo."""
    db_producto = ProductoRepository.get_by_codigo(db, codigo=producto.codigo)
    if db_producto:
        raise HTTPException(status_code=400, detail="Ya existe un producto con este código.")
    
    return ProductoRepository.create(db=db, producto=producto)

@router.get("/{codigo}", response_model=ProductoResponse)
def obtener_producto(codigo: str, db: Session = Depends(get_db)):
    """Busca un producto específico por su código interno."""
    db_producto = ProductoRepository.get_by_codigo(db, codigo=codigo)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return db_producto