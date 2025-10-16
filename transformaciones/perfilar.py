from PIL import ImageFilter

class Perfilar:
    @staticmethod
    def aplicar(img, parametros=None):
        """Aplica filtro de realce de bordes usando parámetros del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetros del frontend Angular
            nivel_nitidez = parametros.get("value", 0)  # Valor de 0 a 100
            
            print(f"Aplicando nitidez con nivel: {nivel_nitidez}")
            
            # Convertir nivel de 0-100 a parámetros de UnsharpMask
            if nivel_nitidez > 0:
                # Mapear 0-100 a parámetros razonables para UnsharpMask
                radio = 2.0
                porcentaje = 50 + (nivel_nitidez * 1.5)  # 0 -> 50%, 100 -> 200%
                umbral = 3
                
                return img.filter(ImageFilter.UnsharpMask(
                    radius=radio, 
                    percent=porcentaje, 
                    threshold=umbral
                ))
            else:
                return img
            
        except Exception as e:
            print(f"Error en perfilado: {e}")
            return img