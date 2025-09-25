from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from typing import List, Dict, Any
import importlib
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("ProcesadorImagen")

class ProcesadorImagenesImpl:
    def __init__(self):
        # Mapeo completo de transformaciones según requisitos
        self.transformaciones = {
            "escala_grises": "transformaciones.escala_grises.EscalaGrises",
            "redimensionar": "transformaciones.redimensionar.Redimensionar",
            "recortar": "transformaciones.recortar.Recortar",
            "rotar": "transformaciones.rotar.Rotar",
            "reflejar": "transformaciones.reflejar.Reflejar",
            "desenfocar": "transformaciones.desenfocar.Desenfocar",
            "perfilar": "transformaciones.perfilar.Perfilar",
            "brillo_contraste": "transformaciones.brillo_contraste.BrilloContraste",
            "marca_agua": "transformaciones.marca_agua.MarcaAgua",
            "convertir_formato": "transformaciones.convertir_formato.ConvertirFormato"
        }

    def procesar(self, ruta_entrada: str, ruta_salida: str, 
                 lista_transformaciones: List[Dict], id_trabajo: str = None) -> bool:
        """
        Aplica una lista de transformaciones a una imagen con manejo robusto de errores
        """
        try:
            logger.info(f"[Trabajo {id_trabajo}] Abriendo imagen: {ruta_entrada}")
            img = Image.open(ruta_entrada)
            formato_original = img.format
            
            # Log de metadatos iniciales
            logger.info(f"[Trabajo {id_trabajo}] Imagen original: {img.size}px, formato: {formato_original}")

            for i, transformacion in enumerate(lista_transformaciones):
                nombre = transformacion["tipo"]
                parametros = transformacion.get("parametros", {})
                
                if nombre not in self.transformaciones:
                    logger.error(f"[Trabajo {id_trabajo}] Transformación no soportada: {nombre}")
                    return False
                
                try:
                    # Cargar dinámicamente la clase de transformación
                    modulo, clase = self.transformaciones[nombre].rsplit(".", 1)
                    mod = importlib.import_module(modulo)
                    clase_trans = getattr(mod, clase)

                    logger.info(f"[Trabajo {id_trabajo}] Aplicando {nombre} ({i+1}/{len(lista_transformaciones)})")
                    img = clase_trans.aplicar(img, parametros)
                    
                    # Validar imagen después de cada transformación
                    if img is None:
                        logger.error(f"[Trabajo {id_trabajo}] Transformación {nombre} devolvió None")
                        return False
                        
                except Exception as e:
                    logger.error(f"[Trabajo {id_trabajo}] Error en transformación {nombre}: {e}")
                    return False

            # Determinar formato de salida
            formato_salida = parametros.get("formato", formato_original)
            if formato_salida.lower() == "jpg":
                formato_salida = "JPEG"
            
            # Guardar imagen resultante
            img.save(ruta_salida, format=formato_salida)
            logger.info(f"[Trabajo {id_trabajo}] Imagen guardada en {ruta_salida}")
            
            return True
            
        except Exception as e:
            logger.error(f"[Trabajo {id_trabajo}] Error procesando imagen: {e}")
            return False