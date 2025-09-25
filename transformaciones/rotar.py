class Rotar:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        grados = parametros.get("grados", 90)
        return img.rotate(grados, expand=True)
