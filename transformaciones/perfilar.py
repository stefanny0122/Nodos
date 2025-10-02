from PIL import ImageFilter

class Perfilar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Aplica filtro de realce de bordes (perfilado)"""
        if parametros is None:
            parametros = {}
        
        try:
            # Usar unsharp mask para perfilar
            radio = parametros.get("radio", 2)
            porcentaje = parametros.get("porcentaje", 150)
            umbral = parametros.get("umbral", 3)
            
            return img.filter(ImageFilter.UnsharpMask(
                radius=radio, 
                percent=porcentaje, 
                threshold=umbral
            ))
            
        except Exception as e:
            print(f"Error en perfilado: {e}")
            return img