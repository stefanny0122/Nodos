from PIL import ImageFilter

class Desenfocar:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        radio = parametros.get("radio", 2)
        return img.filter(ImageFilter.GaussianBlur(radius=radio))
