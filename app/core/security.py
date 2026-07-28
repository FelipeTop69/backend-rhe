from datetime import datetime, timedelta
from jose import jwt

# 🔐 CLAVE MAESTRA (En un entorno real, esto iría en un archivo .env)
SECRET_KEY = "mi_clave_maestra_super_secreta_rhe" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120 # El pase VIP durará 2 horas

def create_access_token(data: dict):
    """Genera un Token JWT firmado digitalmente."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Crea y firma el token con la clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt