from PIL import ImageDraw, ImageFont

class MarcaAgua:
    @staticmethod
    def aplicar(img, parametros=None):
        """Agrega marca de agua de texto a la imagen"""
        if parametros is None:
            parametros = {}
        
        try:
            texto = parametros.get("texto", "Marca de Agua")
            posicion = parametros.get("posicion", (10, 10))
            color = parametros.get("color", (255, 255, 255, 128))
            tamaño_fuente = parametros.get("tamaño_fuente", 20)
            
            # Crear una imagen temporal para dibujar
            img_con_marca = img.convert("RGBA")
            
            # Crear capa de texto
            txt = Image.new('RGBA', img_con_marca.size, (255,255,255,0))
            draw = ImageDraw.Draw(txt)
            
            # Intentar cargar fuente, usar default si falla
            try:
                font = ImageFont.truetype("arial.ttf", tamaño_fuente)
            except:
                font = ImageFont.load_default()
            
            # Dibujar texto
            draw.text(posicion, texto, fill=color, font=font)
            
            # Combinar imágenes
            img_resultado = Image.alpha_composite(img_con_marca, txt)
            
            return img_resultado.convert("RGB")  # Volver a RGB para compatibilidad
            
        except Exception as e:
            print(f"Error agregando marca de agua: {e}")
            return img