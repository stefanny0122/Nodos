from PIL import ImageOps

class Reflejar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Refleja la imagen horizontal o verticalmente"""
        if parametros is None:
            parametros = {}
        
        try:
            tipo = parametros.get("tipo", "horizontal")  # "horizontal" o "vertical"
            
            if tipo == "horizontal":
                return ImageOps.mirror(img)
            elif tipo == "vertical":
                return ImageOps.flip(img)
            else:
                return img
                
        except Exception as e:
            print(f"Error en reflejo: {e}")
            return img