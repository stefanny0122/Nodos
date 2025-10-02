import subprocess
import time
import requests
import Pyro5.api
import sys
import os

def test_nodo_worker_corregido():
    print("=== TEST NODO WORKER CORREGIDO ===")
    
    # 1. Verificar que el NameServer este corriendo
    print("1. Verificando NameServer...")
    try:
        ns = Pyro5.api.locate_ns(host="localhost", port=9090)
        print("   OK - NameServer encontrado en localhost:9090")
    except Exception as e:
        print(f"   ERROR - NameServer no encontrado: {e}")
        print("   Ejecuta: python -m Pyro5.nameserver")
        return False
    
    # 2. Iniciar nodo worker en segundo plano
    print("2. Iniciando nodo worker...")
    try:
        worker_process = subprocess.Popen([
            sys.executable, "nodo_worker.py", "worker01"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        # Esperar a que se inicie
        time.sleep(3)
        
        # Verificar si el proceso sigue activo
        if worker_process.poll() is not None:
            stdout, stderr = worker_process.communicate()
            print(f"   ERROR - Nodo worker fallo al iniciar")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return False
            
        print("   OK - Nodo worker iniciado")
        
    except Exception as e:
        print(f"   ERROR - Error iniciando nodo worker: {e}")
        return False
    
    # 3. Verificar que el nodo se registro
    print("3. Verificando registro en NameServer...")
    try:
        ns = Pyro5.api.locate_ns(host="localhost", port=9090)
        nodos = ns.list(prefix="nodo.")
        
        if nodos:
            print(f"   OK - Nodos registrados: {len(nodos)}")
            for nombre, uri in nodos.items():
                print(f"     - {nombre}: {uri}")
                
                # Probar conexion con el nodo
                try:
                    proxy = Pyro5.api.Proxy(uri)
                    proxy._pyroTimeout = 5
                    proxy._pyroBind()
                    
                    estado = proxy.obtener_estado()
                    print(f"       OK - Conectado - Estado: {estado}")
                    
                    # Probar metodo de saludo
                    saludo = proxy.saludar()
                    print(f"       Saludo: {saludo}")
                    
                except Exception as e:
                    print(f"       ERROR - Error conectando: {e}")
        else:
            print("   ERROR - No hay nodos registrados")
            
    except Exception as e:
        print(f"   ERROR - Error verificando NameServer: {e}")
    
    # 4. Probar procesamiento de imagen
    print("4. Probando procesamiento de imagen...")
    try:
        ns = Pyro5.api.locate_ns(host="localhost", port=9090)
        uri = ns.lookup("nodo.worker01")
        proxy = Pyro5.api.Proxy(uri)
        proxy._pyroTimeout = 10
        proxy._pyroBind()
        
        # Crear archivo de prueba temporal
        test_input = "test_input_worker.png"
        test_output = "test_output_worker.png"
        
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(test_input)
        
        # Probar procesamiento
        transformaciones = [
            {"tipo": "escala_grises", "parametros": {}},
            {"tipo": "redimensionar", "parametros": {"ancho": 50, "alto": 50}}
        ]
        
        resultado = proxy.procesar(
            id_trabajo="test_worker_01",
            ruta_entrada=test_input,
            ruta_salida=test_output,
            lista_transformaciones=transformaciones
        )
        
        print(f"   OK - Procesamiento completado: {resultado}")
        
        # Limpiar archivos temporales
        if os.path.exists(test_input):
            os.remove(test_input)
        if os.path.exists(test_output):
            os.remove(test_output)
            
    except Exception as e:
        print(f"   ERROR - Error en procesamiento: {e}")
    
    # 5. Limpiar
    print("5. Limpiando...")
    try:
        worker_process.terminate()
        worker_process.wait(timeout=5)
        print("   OK - Nodo worker detenido")
    except:
        print("   AVISO - No se pudo detener el nodo worker correctamente")
        worker_process.kill()
    
    return True

if __name__ == "__main__":
    test_nodo_worker_corregido()