from PIL import ImageFilter

class Desenfocar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Aplica desenfoque gaussiano usando el radio del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetro del frontend Angular - radio en píxeles
            radio = parametros.get("radius", 0)
            
            print(f"Aplicando desenfoque con radio: {radio}px")
            
            # Solo aplicar si el radio es mayor a 0
            if radio > 0:
                return img.filter(ImageFilter.GaussianBlur(radius=radio))
            else:
                return img
            
        except Exception as e:
            print(f"Error en desenfoque: {e}")
            return img