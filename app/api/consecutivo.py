from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import ConsecutivoBase, ConsecutivoResponse
from app.repositories.crud import ConsecutivoRepository # Ajusta crud o repositories según tu nombre
from app.core.database import SessionLocal

router = APIRouter(prefix="/consecutivo", tags=["Configuración"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=ConsecutivoResponse)
def obtener_consecutivo(db: Session = Depends(get_db)):
    """Obtiene el estado actual del consecutivo de facturación."""
    return ConsecutivoRepository.get_current(db)

@router.put("/", response_model=ConsecutivoResponse)
def actualizar_consecutivo(datos: ConsecutivoBase, db: Session = Depends(get_db)):
    """Sobrescribe el consecutivo y prefijo actuales."""
    consecutivo_actual = ConsecutivoRepository.get_current(db)
    return ConsecutivoRepository.update(
        db=db, 
        consecutivo_obj=consecutivo_actual, 
        nuevo_prefijo=datos.prefijo, 
        nuevo_numero=datos.numero_actual
    )