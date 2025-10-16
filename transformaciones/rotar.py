from PIL import Image

class Rotar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Rota una imagen usando los grados del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetros del frontend Angular
            grados = parametros.get("degrees", 0)
            
            print(f"Aplicando rotación: {grados} grados")
            
            # Solo rotar si los grados no son 0
            if grados != 0:
                return img.rotate(grados, expand=True)
            else:
                return img
            
        except Exception as e:
            print(f"Error en rotación: {e}")
            return img