import os
import fitz  # PyMuPDF
from abc import ABC, abstractmethod
from typing import Dict
from supabase import create_client, Client # Supabase

SUPABASE_URL = "https://hxsivpxspofiwclmefvo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh4c2l2cHhzcG9maXdjbG1lZnZvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE2NzcwOCwiZXhwIjoyMTAwNzQzNzA4fQ.VBvdxnymlAsePN9NSpsRB1zlHAlikVUEjlwJPAOigtg"

# ==========================================
# 1. INTERFAZ BASE DEL PATRÓN STRATEGY
# ==========================================
class FacturaStrategy(ABC):
    @abstractmethod
    def get_plantilla_path(self) -> str:
        """Devuelve el nombre del archivo de la plantilla PDF."""
        pass

# ==========================================
# 2. ESTRATEGIAS CONCRETAS (1, 2 y 3 Productos)
# ==========================================
class Factura1ProductoStrategy(FacturaStrategy):
    def get_plantilla_path(self) -> str:
        return "Plantilla_Base_1P.pdf"

class Factura2ProductosStrategy(FacturaStrategy):
    def get_plantilla_path(self) -> str:
        return "Plantilla_Base_2P.pdf"

class Factura3ProductosStrategy(FacturaStrategy):
    def get_plantilla_path(self) -> str:
        return "Plantilla_Base_3P.pdf"

# ==========================================
# 3. EL CEREBRO: SERVICIO GENERADOR (CONTEXTO)
# ==========================================
class PdfService:
    def __init__(self, base_dir: str = "assets/plantillas", output_dir: str = "assets/salidas"):
        self.base_dir = base_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Inicializar cliente de Supabase Storage
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def _seleccionar_estrategia(self, cantidad_productos: int) -> FacturaStrategy:
        """Selecciona la estrategia (plantilla) basada en la cantidad de productos."""
        if cantidad_productos == 1:
            return Factura1ProductoStrategy()
        elif cantidad_productos == 2:
            return Factura2ProductosStrategy()
        elif cantidad_productos == 3:
            return Factura3ProductosStrategy()
        else:
            raise ValueError("La cantidad de productos debe estar entre 1 y 3.")

    def _construir_payload(self, factura_obj) -> Dict[str, str]:
        """Traduce los objetos de la Base de Datos a los Tags del PDF."""
        # Formateadores básicos (Para Colombia: . para miles, , para decimales)
        def formato_moneda(valor: float) -> str:
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        def formato_cantidad(valor: float) -> str:
            return f"{valor:,.2f}".replace(".", ",")

        # Datos Cabecera y Cliente
        payload = {
            "@@CONSECUTIVO@@": factura_obj.numero_factura,
            "@@FECHA@@": factura_obj.fecha_emision.strftime("%Y-%m-%d"),
            "@@HORA_GEN@@": factura_obj.hora_generacion.strftime("%H:%M:%S"),
            "@@HORA_EXP@@": factura_obj.hora_expedicion.strftime("%H:%M:%S"),
            "@@CLIENTE_NOMBRE@@": factura_obj.cliente.nombre,
            "@@CLIENTE_NIT@@": factura_obj.cliente.identificacion,
            "@@VALOR_TOTAL@@": formato_moneda(factura_obj.valor_total)
        }

        # Datos Dinámicos de Productos
        for i, detalle in enumerate(factura_obj.detalles, start=1):
            payload[f"@@PROD{i}_DESC@@"] = detalle.producto.descripcion
            payload[f"@@PROD{i}_CANT@@"] = formato_cantidad(detalle.cantidad)
            # Manejo del valor del producto para el payload dinámico
            payload[f"@@PROD{i}_VALOR@@"] = formato_moneda(detalle.subtotal)

        return payload

    def generar_factura(self, factura_obj) -> str:
        """Lógica Principal de inyección unificada con PyMuPDF."""
        
        # 1. Seleccionar la plantilla correcta
        estrategia = self._seleccionar_estrategia(len(factura_obj.detalles))
        ruta_plantilla = os.path.join(self.base_dir, estrategia.get_plantilla_path())
        
        if not os.path.exists(ruta_plantilla):
            raise FileNotFoundError(f"No se encontró la plantilla en: {ruta_plantilla}")

        # 2. Construir el diccionario de reemplazos
        payload = self._construir_payload(factura_obj)

        # 3. Procesamiento PyMuPDF (Unificado)
        doc = fitz.open(ruta_plantilla)
        page = doc[0]
        operaciones = []
        diccionario_texto = page.get_text("dict")

        # Escanear el documento buscando los Tags
        for tag, nuevo_valor in payload.items():
            instancias = page.search_for(tag)
            for inst in instancias:
                span_match = None
                for bloque in diccionario_texto.get("blocks", []):
                    for linea in bloque.get("lines", []):
                        for span in linea.get("spans", []):
                            if tag in span.get("text", ""):
                                # Precisión de línea base adaptada de tus scripts
                                if abs(span["bbox"][1] - inst.y0) < 5:
                                    span_match = span
                                    break
                        if span_match: break
                    if span_match: break

                if span_match:
                    origen_x, origen_y = span_match["origin"]
                    tamaño = span_match["size"]
                    fuente_original = span_match["font"].lower()

                    if "bold" in fuente_original or "black" in fuente_original:
                        fuente_final = "hebo"
                    elif "courier" in fuente_original:
                        fuente_final = "cour"
                    else:
                        fuente_final = "helv"

                    operaciones.append({
                        "rect": inst,
                        "texto": nuevo_valor,
                        "fuente": fuente_final,
                        "tamaño": tamaño,
                        "origen": (origen_x, origen_y)
                    })

        # Borrado Inteligente
        for op in operaciones:
            page.add_redact_annot(op["rect"])
        page.apply_redactions(images=0, graphics=0)

        # Inyectar Nuevo Texto
        for op in operaciones:
            page.insert_text(
                op["origen"],
                op["texto"],
                fontname=op["fuente"],
                fontsize=op["tamaño"],
                color=(0, 0, 0) # Tinta negra para facturas finales
            )

        # 4. Guardado Local
        nombre_salida = f"Factura_{factura_obj.numero_factura}.pdf"
        ruta_salida = os.path.join(self.output_dir, nombre_salida)
        
        doc.save(ruta_salida)
        doc.close()

        # --- NUEVO PASO: 5. SUBIR A SUPABASE STORAGE ---
        # Leemos el archivo PDF que acabamos de crear
        with open(ruta_salida, "rb") as f:
            # Subimos al bucket 'facturas' y le decimos que sobrescriba si ya existe uno con ese nombre
            self.supabase.storage.from_("facturas").upload(
                path=nombre_salida,
                file=f,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
            
        # 6. Obtener la URL pública donde quedó alojado el PDF en la nube
        url_publica = self.supabase.storage.from_("facturas").get_public_url(nombre_salida)

        # 7. Limpieza: Borramos el archivo local porque ya está seguro en la nube
        os.remove(ruta_salida)

        # Retornamos la URL de la nube en lugar de la ruta local
        return url_publica