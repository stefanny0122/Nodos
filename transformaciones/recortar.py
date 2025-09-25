class Recortar:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        izquierda = parametros.get("izq", 0)
        arriba = parametros.get("arriba", 0)
        derecha = parametros.get("der", img.width)
        abajo = parametros.get("abajo", img.height)
        return img.crop((izquierda, arriba, derecha, abajo))
