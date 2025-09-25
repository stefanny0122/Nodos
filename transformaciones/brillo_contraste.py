from PIL import ImageEnhance

class BrilloContraste:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        brillo = parametros.get("brillo", 1.0)
        contraste = parametros.get("contraste", 1.0)

        enhancer_b = ImageEnhance.Brightness(img)
        img = enhancer_b.enhance(brillo)

        enhancer_c = ImageEnhance.Contrast(img)
        img = enhancer_c.enhance(contraste)

        return img
