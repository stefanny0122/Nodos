"""
Procesador de imágenes para nodos workers
Implementa transformaciones usando Pillow (PIL)
"""

import os
from PIL import Image, ImageFilter, ImageEnhance
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

# Importar todas las transformaciones
from transformaciones.escala_grises import EscalaGrises
from transformaciones.redimensionar import Redimensionar
from transformaciones.recortar import Recortar
from transformaciones.rotar import Rotar
from transformaciones.reflejar import Reflejar
from transformaciones.desenfocar import Desenfocar
from transformaciones.perfilar import Perfilar
from transformaciones.brillo_contraste import BrilloContraste
from transformaciones.marca_agua import MarcaAgua
from transformaciones.convertir_formato import ConvertirFormato

logger = get_logger("ProcesadorImagen")


class ProcesadorImagenesImpl:
    """
    Implementación del procesador de imágenes.
    Aplica transformaciones usando la biblioteca Pillow.
    """
    
    def __init__(self):
        # Diccionario de transformaciones disponibles con mapeo desde el frontend
        self.transformaciones = {
            # Mapeo de IDs del frontend a clases de transformación
            'grayscale': EscalaGrises,
            'brightness': BrilloContraste,
            'contrast': BrilloContraste,
            'blur': Desenfocar,
            'sharpen': Perfilar,
            'rotate': Rotar,
            'watermark': MarcaAgua,
            'flip': Reflejar,
            'flop': Reflejar,
            'resize': Redimensionar,
            'crop': Recortar,
            'convert_format': ConvertirFormato
        }
        
        logger.info(f"Procesador inicializado con {len(self.transformaciones)} transformaciones")

    def procesar(self, ruta_entrada: str, ruta_salida: str, 
                 lista_transformaciones: List[Dict], id_trabajo: str = None) -> bool:
        """
        Procesa una imagen aplicando una lista de transformaciones.
        Devuelve UNA SOLA imagen con todos los cambios aplicados.
        
        Args:
            ruta_entrada: Ruta del archivo de entrada
            ruta_salida: Ruta donde guardar el resultado
            lista_transformaciones: Lista de dicts con 'tipo' y 'parametros' del frontend
            id_trabajo: ID del trabajo para logging
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        id_trabajo = id_trabajo or "desconocido"
        
        try:
            logger.info(f"[Trabajo {id_trabajo}] Procesando imagen con {len(lista_transformaciones)} transformaciones")
            
            # Validar archivo de entrada
            if not os.path.exists(ruta_entrada):
                logger.error(f"[Trabajo {id_trabajo}] Archivo no existe: {ruta_entrada}")
                return False
            
            # Abrir imagen
            with Image.open(ruta_entrada) as img:
                # Convertir a RGB si es necesario (para JPEG)
                if img.mode in ('P', 'RGBA', 'LA'):
                    img = img.convert('RGB')
                
                logger.info(f"[Trabajo {id_trabajo}] Imagen original: {img.size}px, formato: {img.format}")
                
                # Aplicar transformaciones en orden - SOBRE LA MISMA IMAGEN
                transformaciones_aplicadas = []
                for i, transformacion in enumerate(lista_transformaciones):
                    tipo_frontend = transformacion.get('tipo')  # ID del frontend
                    parametros = transformacion.get('parametros', {})
                    
                    # Mapear tipo del frontend a clase de transformación
                    if tipo_frontend in self.transformaciones:
                        clase_transformacion = self.transformaciones[tipo_frontend]
                        
                        # Para flip/flop, pasar el tipo como parámetro
                        if tipo_frontend in ['flip', 'flop']:
                            parametros['tipo'] = tipo_frontend
                        
                        logger.debug(f"[Trabajo {id_trabajo}] Aplicando transformación {i+1}: {tipo_frontend} con parámetros: {parametros}")
                        
                        # Aplicar la transformación
                        img = clase_transformacion.aplicar(img, parametros)
                        transformaciones_aplicadas.append(tipo_frontend)
                    else:
                        logger.warning(f"[Trabajo {id_trabajo}] Transformación no soportada: {tipo_frontend}, omitiendo")
                        continue
                
                # Crear directorio de salida si no existe
                os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
                
                # Guardar ÚNICA imagen resultante con todos los cambios
                logger.info(f"[Trabajo {id_trabajo}] Guardando imagen final: {ruta_salida}")
                
                # Determinar formato basado en extensión
                formato = 'PNG'
                if ruta_salida.lower().endswith('.jpg') or ruta_salida.lower().endswith('.jpeg'):
                    formato = 'JPEG'
                    img.save(ruta_salida, format=formato, quality=95, optimize=True)
                elif ruta_salida.lower().endswith('.webp'):
                    formato = 'WEBP'
                    img.save(ruta_salida, format=formato, quality=95)
                else:
                    # Por defecto PNG
                    img.save(ruta_salida, format='PNG', optimize=True)
                
                # Verificar que el archivo se creó correctamente
                if os.path.exists(ruta_salida):
                    tamaño = os.path.getsize(ruta_salida)
                    logger.info(
                        f"[Trabajo {id_trabajo}] ✓ Procesamiento completado. "
                        f"Transformaciones aplicadas: {len(transformaciones_aplicadas)}. "
                        f"Archivo final: {tamaño/1024:.2f} KB"
                    )
                    return True
                else:
                    logger.error(f"[Trabajo {id_trabajo}] ✗ No se pudo crear archivo de salida")
                    return False
                    
        except Exception as e:
            logger.error(f"[Trabajo {id_trabajo}] Error procesando imagen: {e}", exc_info=True)
            return False