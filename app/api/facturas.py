from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import FacturaCreate, FacturaResponse
from app.repositories.crud import FacturaRepository, ConsecutivoRepository
from app.services.pdf_service import PdfService
from app.core.database import SessionLocal

router = APIRouter(prefix="/facturas", tags=["Facturas"])

# Instanciamos nuestro cerebro generador de PDFs
pdf_service = PdfService() 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generar", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
def generar_factura(factura_in: FacturaCreate, db: Session = Depends(get_db)):
    """Genera una nueva factura, la guarda en DB y crea el PDF físico."""
    try:
        # 1. Obtener el consecutivo actual y armar el string
        consecutivo_obj = ConsecutivoRepository.get_current(db)
        numero_factura_str = f"{consecutivo_obj.prefijo}{consecutivo_obj.numero_actual}"

        # 2. Guardar en Base de Datos (Esto calcula los totales de forma automática)
        db_factura = FacturaRepository.create_factura(
            db=db,
            factura_data=factura_in,
            numero_factura_str=numero_factura_str
        )

        # 3. Incrementar el consecutivo para la próxima transacción
        ConsecutivoRepository.increment(db, consecutivo_obj)

        # 4. Generar el PDF físico utilizando el Patrón Strategy
        ruta_pdf = pdf_service.generar_factura(factura_obj=db_factura)

        # Imprimimos en consola la ruta para confirmar en backend
        print(f"¡PDF generado con éxito en: {ruta_pdf}!")

        # 5. Retornar el objeto guardado como respuesta de la API
        return db_factura

    except FileNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Si algo falla, deshacemos los cambios en la base de datos
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generando factura: {str(e)}")