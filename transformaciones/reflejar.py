from PIL import ImageOps

class Reflejar:
    @staticmethod
    def aplicar(img, parametros=None):
        return ImageOps.mirror(img)
