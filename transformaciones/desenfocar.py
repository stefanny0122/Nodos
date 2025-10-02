from PIL import ImageFilter

class Desenfocar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Aplica desenfoque gaussiano a la imagen"""
        if parametros is None:
            parametros = {}
        
        try:
            radio = parametros.get("radio", 2)
            return img.filter(ImageFilter.GaussianBlur(radius=radio))
            
        except Exception as e:
            print(f"Error en desenfoque: {e}")
            return img