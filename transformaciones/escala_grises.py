from PIL import Image

class EscalaGrises:
    @staticmethod
    def aplicar(img, parametros=None):
        """Convierte imagen a escala de grises"""
        try:
            print("Aplicando escala de grises")
            
            if img.mode != 'L':
                return img.convert('L')
            return img
        except Exception as e:
            print(f"Error en escala de grises: {e}")
            return img