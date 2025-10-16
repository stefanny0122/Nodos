from PIL import ImageDraw, ImageFont, Image

class MarcaAgua:
    @staticmethod
    def aplicar(img, parametros=None):
        """Agrega marca de agua de texto usando parámetros del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetros del frontend Angular
            texto = parametros.get("text", "")
            
            print(f"Aplicando marca de agua con texto: '{texto}'")
            
            # Solo aplicar si hay texto
            if not texto or texto.strip() == "":
                return img
            
            # Crear una imagen temporal para dibujar
            img_con_marca = img.convert("RGBA")
            
            # Crear capa de texto
            txt = Image.new('RGBA', img_con_marca.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt)
            
            # Configurar fuente - tamaño basado en la imagen
            try:
                tamaño_base = max(img.width, img.height)
                tamaño_fuente = max(20, tamaño_base // 20)  # Fuente proporcional al tamaño de imagen
                font = ImageFont.truetype("arial.ttf", tamaño_fuente)
            except:
                # Fallback a fuente por defecto
                font = ImageFont.load_default()
            
            # Calcular posición centrada
            bbox = draw.textbbox((0, 0), texto, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
            
            # Color semi-transparente
            color = (255, 255, 255, 128)  # Blanco semi-transparente
            
            # Dibujar texto
            draw.text((x, y), texto, fill=color, font=font)
            
            # Combinar imágenes
            img_resultado = Image.alpha_composite(img_con_marca, txt)
            
            return img_resultado.convert("RGB")  # Volver a RGB para compatibilidad
            
        except Exception as e:
            print(f"Error agregando marca de agua: {e}")
            return img