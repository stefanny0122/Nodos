from PIL import Image

class Rotar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Rota una imagen los grados especificados"""
        if parametros is None:
            parametros = {}
        
        try:
            grados = parametros.get("grados", 90)
            expandir = parametros.get("expandir", True)
            
            return img.rotate(grados, expand=expandir)
            
        except Exception as e:
            print(f"Error en rotación: {e}")
            return img