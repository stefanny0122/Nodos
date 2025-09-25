class ConvertirFormato:
    @staticmethod
    def aplicar(img, parametros=None):
        """Convierte la imagen a diferentes formatos"""
        if parametros is None:
            parametros = {}
        formato = parametros.get("formato", "PNG").upper()
        # La conversión real se maneja en el guardado
        return img