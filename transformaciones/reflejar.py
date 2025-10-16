from PIL import ImageOps

class Reflejar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Refleja la imagen según el tipo del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetros del frontend Angular
            tipo = parametros.get("tipo", "horizontal")  # "flip" o "flop" del frontend
            
            print(f"Aplicando reflejo tipo: {tipo}")
            
            if tipo == "flip" or tipo == "horizontal":
                return ImageOps.mirror(img)  # Volteo horizontal
            elif tipo == "flop" or tipo == "vertical":
                return ImageOps.flip(img)    # Volteo vertical
            else:
                return img
                
        except Exception as e:
            print(f"Error en reflejo: {e}")
            return img