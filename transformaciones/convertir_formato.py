from PIL import Image

class ConvertirFormato:
    @staticmethod
    def aplicar(img, parametros=None):
        """Convierte la imagen al formato especificado desde el frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Esta transformación principalmente cambia el formato al guardar
            # pero podemos hacer algunas conversiones básicas aquí
            formato = parametros.get("formato", "PNG").upper()
            
            print(f"Preparando conversión a formato: {formato}")
            
            if formato == "JPG" or formato == "JPEG":
                # Convertir a RGB si es necesario para JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Crear fondo blanco para imágenes con transparencia
                    fondo = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        fondo.paste(img, mask=img.split()[-1])
                    else:
                        fondo.paste(img)
                    return fondo
                elif img.mode != 'RGB':
                    return img.convert('RGB')
            elif formato == "PNG":
                # Para PNG, mantener transparencia si existe
                if img.mode != 'RGBA':
                    return img.convert('RGBA')
            
            return img
            
        except Exception as e:
            print(f"Error en conversión de formato: {e}")
            return img