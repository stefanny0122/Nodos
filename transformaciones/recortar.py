from PIL import Image

class Recortar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Recorta una imagen según las coordenadas especificadas"""
        if parametros is None:
            parametros = {}
        
        try:
            izquierda = parametros.get("izquierda", 0)
            superior = parametros.get("superior", 0)
            derecha = parametros.get("derecha", img.width)
            inferior = parametros.get("inferior", img.height)
            
            # Asegurar que las coordenadas estén dentro de los límites
            izquierda = max(0, min(izquierda, img.width))
            superior = max(0, min(superior, img.height))
            derecha = max(izquierda + 1, min(derecha, img.width))
            inferior = max(superior + 1, min(inferior, img.height))
            
            return img.crop((izquierda, superior, derecha, inferior))
            
        except Exception as e:
            print(f"Error en recorte: {e}")
            return img