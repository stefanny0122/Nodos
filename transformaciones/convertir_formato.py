class ConvertirFormato:
    @staticmethod
    def aplicar(img, parametros=None):
        """Convierte la imagen al formato especificado"""
        if parametros is None:
            parametros = {}
        
        try:
            # Esta transformación principalmente cambia el formato al guardar
            # pero podemos hacer algunas conversiones básicas aquí
            formato = parametros.get("formato", "PNG").upper()
            
            if formato == "JPG" or formato == "JPEG":
                # Convertir a RGB si es necesario para JPEG
                if img.mode in ('RGBA', 'LA'):
                    # Crear fondo blanco para imágenes con transparencia
                    fondo = Image.new('RGB', img.size, (255, 255, 255))
                    fondo.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    return fondo
                elif img.mode != 'RGB':
                    return img.convert('RGB')
            
            return img
            
        except Exception as e:
            print(f"Error en conversión de formato: {e}")
            return img