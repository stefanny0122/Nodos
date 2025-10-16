from PIL import ImageEnhance

class BrilloContraste:
    @staticmethod
    def aplicar(img, parametros=None):
        """Ajusta el brillo y contraste de la imagen usando parámetros del frontend"""
        if parametros is None:
            parametros = {}
        
        try:
            # Parámetros del frontend Angular
            brillo = parametros.get("value", 0)  # Valor de -100 a 100
            contraste = parametros.get("contraste", 0)  # Valor de -100 a 100
            
            # Convertir valores de -100 a 100 a factores de 0.0 a 2.0
            factor_brillo = 1.0 + (brillo / 100.0)  # -100 -> 0.0, 0 -> 1.0, 100 -> 2.0
            factor_contraste = 1.0 + (contraste / 100.0)  # -100 -> 0.0, 0 -> 1.0, 100 -> 2.0
            
            print(f"Aplicando brillo: {brillo} -> factor: {factor_brillo}")
            print(f"Aplicando contraste: {contraste} -> factor: {factor_contraste}")
            
            # Aplicar brillo
            if factor_brillo != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(factor_brillo)
            
            # Aplicar contraste
            if factor_contraste != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(factor_contraste)
            
            return img
            
        except Exception as e:
            print(f"Error en brillo/contraste: {e}")
            return img