from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Usuario
from app.core.security import create_access_token

router = APIRouter(tags=["Autenticación"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Valida credenciales y devuelve un Token JWT."""
    
    # 1. Buscar al usuario en la base de datos por su username
    usuario = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    
    # 2. Validar que exista y que la contraseña coincida
    if not usuario or usuario.password_hash != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generar el pase VIP (Token JWT) guardando el UUID del usuario dentro
    access_token = create_access_token(data={"sub": str(usuario.id)})
    
    # 4. Retornar el token en el formato estándar de OAuth2
    return {"access_token": access_token, "token_type": "bearer"}