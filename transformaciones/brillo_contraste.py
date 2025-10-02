from PIL import ImageEnhance

class BrilloContraste:
    @staticmethod
    def aplicar(img, parametros=None):
        """Ajusta el brillo y contraste de la imagen"""
        if parametros is None:
            parametros = {}
        
        try:
            brillo = parametros.get("brillo", 1.0)
            contraste = parametros.get("contraste", 1.0)
            
            # Aplicar brillo
            if brillo != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brillo)
            
            # Aplicar contraste
            if contraste != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contraste)
            
            return img
            
        except Exception as e:
            print(f"Error en brillo/contraste: {e}")
            return img