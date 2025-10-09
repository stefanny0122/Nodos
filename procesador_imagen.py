"""
Procesador de imágenes para nodos workers
Implementa transformaciones usando Pillow (PIL)
"""

import os
from PIL import Image, ImageFilter, ImageEnhance
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger("ProcesadorImagen")


class ProcesadorImagenesImpl:
    """
    Implementación del procesador de imágenes.
    Aplica transformaciones usando la biblioteca Pillow.
    """
    
    def __init__(self):
        # Diccionario de transformaciones disponibles con alias
        self.transformaciones = {
            # Transformaciones básicas
            'escala_grises': self._aplicar_escala_grises,
            'grayscale': self._aplicar_escala_grises,  # Alias en inglés
            'redimensionar': self._aplicar_redimensionar,
            'resize': self._aplicar_redimensionar,     # Alias en inglés
            'rotar': self._aplicar_rotar,
            'rotate': self._aplicar_rotar,             # Alias en inglés
            'recortar': self._aplicar_recortar,
            'crop': self._aplicar_recortar,            # Alias en inglés
            'desenfocar': self._aplicar_desenfocar,
            'blur': self._aplicar_desenfocar,          # Alias en inglés
            
            # Efectos avanzados
            'brillo_contraste': self._aplicar_brillo_contraste,
            'brightness_contrast': self._aplicar_brillo_contraste,  # Alias
            'perfilar': self._aplicar_perfilar,
            'edge_enhance': self._aplicar_perfilar,    # Alias en inglés
            
            # Formatos y marcas de agua
            'convertir_formato': self._aplicar_convertir_formato,
            'convert_format': self._aplicar_convertir_formato,  # Alias
            'marca_agua': self._aplicar_marca_agua,
            'watermark': self._aplicar_marca_agua,     # Alias en inglés
            'reflejar': self._aplicar_reflejar,
            'flip': self._aplicar_reflejar             # Alias en inglés
        }
        
        logger.info(f"Procesador inicializado con {len(self.transformaciones)} transformaciones")
    
    def procesar(self, ruta_entrada: str, ruta_salida: str, 
                 lista_transformaciones: List[Dict], id_trabajo: str = None) -> bool:
        """
        Procesa una imagen aplicando una lista de transformaciones.
        
        Args:
            ruta_entrada: Ruta del archivo de entrada
            ruta_salida: Ruta donde guardar el resultado
            lista_transformaciones: Lista de dicts con 'tipo' y 'parametros'
            id_trabajo: ID del trabajo para logging
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        id_trabajo = id_trabajo or "desconocido"
        
        try:
            logger.info(f"[Trabajo {id_trabajo}] Abriendo imagen: {ruta_entrada}")
            
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
                
                # Aplicar transformaciones en orden
                transformaciones_aplicadas = []
                for i, transformacion in enumerate(lista_transformaciones):
                    tipo = transformacion.get('tipo')
                    parametros = transformacion.get('parametros', {})
                    
                    if tipo in self.transformaciones:
                        logger.debug(f"[Trabajo {id_trabajo}] Aplicando transformación {i+1}: {tipo}")
                        img = self.transformaciones[tipo](img, parametros)
                        transformaciones_aplicadas.append(tipo)
                    else:
                        logger.error(f"[Trabajo {id_trabajo}] Transformación no soportada: {tipo}")
                        return False
                
                # Guardar imagen resultante
                logger.info(f"[Trabajo {id_trabajo}] Guardando resultado: {ruta_salida}")
                img.save(ruta_salida, quality=95)
                
                logger.info(f"[Trabajo {id_trabajo}] ✓ Procesamiento completado. "  f"Transformaciones: {transformaciones_aplicadas}")
                return True
                
        except Exception as e:
            logger.error(f"[Trabajo {id_trabajo}] Error procesando imagen: {e}", exc_info=True)
            return False
    
    # ========== IMPLEMENTACIONES DE TRANSFORMACIONES ==========
    
    def _aplicar_escala_grises(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Convierte imagen a escala de grises"""
        return img.convert('L').convert('RGB')
    
    def _aplicar_redimensionar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Redimensiona imagen"""
        ancho = parametros.get('ancho', img.width)
        alto = parametros.get('alto', img.height)
        return img.resize((ancho, alto), Image.Resampling.LANCZOS)
    
    def _aplicar_rotar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Rota imagen"""
        angulo = parametros.get('degrees', 90)
        return img.rotate(angulo, expand=True)
    
    def _aplicar_recortar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Recorta imagen"""
        izquierda = parametros.get('left', 0)
        superior = parametros.get('top', 0)
        derecha = parametros.get('right', img.width)
        inferior = parametros.get('bottom', img.height)
        return img.crop((izquierda, superior, derecha, inferior))
    
    def _aplicar_desenfocar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Aplica desenfoque gaussiano"""
        radio = parametros.get('radio', 2)
        return img.filter(ImageFilter.GaussianBlur(radius=radio))
    
    def _aplicar_brillo_contraste(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Ajusta brillo y contraste"""
        factor_brillo = parametros.get('brillo', 1.0)
        factor_contraste = parametros.get('contraste', 1.0)
        
        # Aplicar brillo
        if factor_brillo != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor_brillo)
        
        # Aplicar contraste
        if factor_contraste != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor_contraste)
        
        return img
    
    def _aplicar_perfilar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Realza bordes de la imagen"""
        return img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    
    def _aplicar_convertir_formato(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Convierte formato (se aplica al guardar)"""
        # Esta transformación se maneja en el guardado
        return img
    
    def _aplicar_marca_agua(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Aplica marca de agua de texto"""
        from PIL import ImageDraw, ImageFont
        
        texto = parametros.get('texto', 'MARCA DE AGUA')
        posicion = parametros.get('posicion', 'centro')
        
        draw = ImageDraw.Draw(img)
        
        # Configurar fuente
        try:
            font_size = parametros.get('tamaño_fuente', 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calcular posición
        bbox = draw.textbbox((0, 0), texto, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if posicion == 'centro':
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        elif posicion == 'esquina_inf_derecha':
            x = img.width - text_width - 10
            y = img.height - text_height - 10
        else:  # esquina_sup_izquierda
            x = 10
            y = 10
        
        # Dibujar texto
        color = parametros.get('color', (255, 255, 255, 128))
        draw.text((x, y), texto, fill=color, font=font)
        
        return img
    
    def _aplicar_reflejar(self, img: Image.Image, parametros: Dict) -> Image.Image:
        """Refleja imagen horizontal o verticalmente"""
        direccion = parametros.get('direccion', 'horizontal')
        
        if direccion == 'horizontal':
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        else:  # vertical
            return img.transpose(Image.FLIP_TOP_BOTTOM)