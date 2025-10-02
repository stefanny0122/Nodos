from PIL import Image

class Redimensionar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Redimensiona la imagen"""
        if parametros is None:
            parametros = {}
        
        try:
            ancho = parametros.get("ancho")
            alto = parametros.get("alto")
            
            # Si solo se proporciona un dimension, calcular la otra manteniendo aspect ratio
            if ancho and not alto:
                ratio = ancho / float(img.width)
                alto = int(img.height * ratio)
            elif alto and not ancho:
                ratio = alto / float(img.height)
                ancho = int(img.width * ratio)
            elif not ancho and not alto:
                # Si no se proporcionan dimensiones, mantener tamaño original
                return img
            
            return img.resize((ancho, alto), Image.Resampling.LANCZOS)
            
        except Exception as e:
            print(f"Error redimensionando: {e}")
            return img