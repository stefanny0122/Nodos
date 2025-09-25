from PIL import ImageFilter

class Perfilar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Aplica filtro de nitidez (perfilado)"""
        if parametros is None:
            parametros = {}
        factor = parametros.get("factor", 2.0)
        return img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))