import sys
import os
from PIL import Image
import io

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from procesador_imagen import ProcesadorImagenesImpl

def test_transformaciones():
    print("=== PRUEBA DE TODAS LAS TRANSFORMACIONES ===")
    
    # Crear una imagen de prueba
    print("1. Creando imagen de prueba...")
    img = Image.new('RGB', (200, 200), color='red')
    
    # Guardar imagen temporal
    test_input = "test_input.png"
    test_output = "test_output.png"
    img.save(test_input)
    
    # Procesador
    procesador = ProcesadorImagenesImpl()
    
    # Lista de todas las transformaciones para probar
    transformaciones_test = [
        {
            "nombre": "Escala de Grises",
            "transformaciones": [{"tipo": "escala_grises", "parametros": {}}]
        },
        {
            "nombre": "Redimensionar", 
            "transformaciones": [{"tipo": "redimensionar", "parametros": {"ancho": 100, "alto": 100}}]
        },
        {
            "nombre": "Recortar",
            "transformaciones": [{"tipo": "recortar", "parametros": {"izquierda": 50, "superior": 50, "derecha": 150, "inferior": 150}}]
        },
        {
            "nombre": "Rotar",
            "transformaciones": [{"tipo": "rotar", "parametros": {"grados": 45}}]
        },
        {
            "nombre": "Reflejar",
            "transformaciones": [{"tipo": "reflejar", "parametros": {"tipo": "horizontal"}}]
        },
        {
            "nombre": "Desenfocar",
            "transformaciones": [{"tipo": "desenfocar", "parametros": {"radio": 2}}]
        },
        {
            "nombre": "Brillo y Contraste", 
            "transformaciones": [{"tipo": "brillo_contraste", "parametros": {"brillo": 1.5, "contraste": 1.2}}]
        },
        {
            "nombre": "Múltiples Transformaciones",
            "transformaciones": [
                {"tipo": "escala_grises", "parametros": {}},
                {"tipo": "redimensionar", "parametros": {"ancho": 150, "alto": 150}},
                {"tipo": "desenfocar", "parametros": {"radio": 1}}
            ]
        }
    ]
    
    resultados = []
    
    for test in transformaciones_test:
        print(f"\n2. Probando: {test['nombre']}...")
        try:
            exito = procesador.procesar(
                test_input,
                test_output,
                test['transformaciones'],
                f"test_{test['nombre'].replace(' ', '_').lower()}"
            )
            
            if exito:
                print(f"   ✅ {test['nombre']} - EXITOSO")
                resultados.append(True)
            else:
                print(f"   ❌ {test['nombre']} - FALLIDO")
                resultados.append(False)
                
        except Exception as e:
            print(f"   💥 {test['nombre']} - ERROR: {e}")
            resultados.append(False)
    
    # Limpiar archivos temporales
    if os.path.exists(test_input):
        os.remove(test_input)
    if os.path.exists(test_output):
        os.remove(test_output)
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    print(f"Transformaciones exitosas: {sum(resultados)}/{len(resultados)}")
    
    if all(resultados):
        print("🎉 ¡TODAS LAS TRANSFORMACIONES FUNCIONAN CORRECTAMENTE!")
    else:
        print("⚠️  Algunas transformaciones tienen problemas")

if __name__ == "__main__":
    test_transformaciones()