from PIL import ImageDraw, ImageFont

class MarcaAgua:
    @staticmethod
    def aplicar(img, parametros=None):
        if parametros is None:
            parametros = {}
        texto = parametros.get("texto", "Marca de agua")
        posicion = parametros.get("posicion", (10, 10))

        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text(posicion, texto, font=font, fill=(255, 255, 255, 128))
        return img
