class Redimensionar:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        ancho = parametros.get("ancho", 100)
        alto = parametros.get("alto", 100)
        return img.resize((ancho, alto))
