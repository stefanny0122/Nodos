import sys
import Pyro5.api
import threading
from typing import Dict, Any
from datetime import datetime
from procesador_imagen import ProcesadorImagenesImpl
from utils.logger import get_logger

logger = get_logger("NodoWorker")

@Pyro5.api.expose
class NodoWorker:
    def __init__(self, id_nodo: str):
        self.id_nodo = id_nodo
        self.estado = "activo"
        self.procesador = ProcesadorImagenesImpl()
        self.trabajos_activos = 0
        self.lock = threading.Lock()
        
    def obtener_estado(self) -> Dict[str, Any]:
        """Retorna el estado actual del nodo"""
        with self.lock:
            return {
                "id_nodo": self.id_nodo,
                "estado": self.estado,
                "trabajos_activos": self.trabajos_activos,
                "timestamp": datetime.now().isoformat()
            }
    
    def saludar(self) -> str:
        """Metodo de prueba"""
        return f"Hola desde nodo {self.id_nodo}"
    
    def procesar(self, id_trabajo: str, ruta_entrada: str, ruta_salida: str, 
            lista_transformaciones: list) -> Dict[str, Any]:
        """Procesa una imagen con las transformaciones solicitadas"""
        logger.info(f"[Nodo {self.id_nodo}] Iniciando trabajo {id_trabajo}")
        
        with self.lock:
            self.trabajos_activos += 1
            self.estado = "procesando"
        
        try:
            # Procesar imagen usando el procesador
            exito = self.procesador.procesar(
                ruta_entrada, 
                ruta_salida, 
                lista_transformaciones,
                id_trabajo
            )
            
            resultado = {
                "id_trabajo": id_trabajo,
                "nodo": self.id_nodo,
                "exito": exito,
                "ruta_resultado": ruta_salida if exito else None,
                "timestamp_fin": datetime.now().isoformat()
            }
            
            if exito:
                logger.info(f"[Nodo {self.id_nodo}] Trabajo {id_trabajo} completado exitosamente")
            else:
                logger.error(f"[Nodo {self.id_nodo}] Trabajo {id_trabajo} fallo")
                
            return resultado
            
        except Exception as e:
            logger.error(f"[Nodo {self.id_nodo}] Error en trabajo {id_trabajo}: {e}")
            return {
                "id_trabajo": id_trabajo,
                "nodo": self.id_nodo,
                "exito": False,
                "error": str(e),
                "timestamp_fin": datetime.now().isoformat()
            }
        finally:
            with self.lock:
                self.trabajos_activos -= 1
                if self.trabajos_activos == 0:
                    self.estado = "activo"

def main():
    if len(sys.argv) < 2:
        print("Uso: python nodo_worker.py <id_nodo>")
        print("Ejemplo: python nodo_worker.py worker01")
        sys.exit(1)

    id_nodo = sys.argv[1]
    
    print(f"Iniciando nodo worker: {id_nodo}")
    
    # Verificar dependencias
    try:
        import Pyro5.api
    except ImportError:
        print("ERROR: Pyro5 no esta instalado. Ejecuta: pip install Pyro5")
        sys.exit(1)
    
    # Verificar que el procesador de imagenes funciona
    try:
        from procesador_imagen import ProcesadorImagenesImpl
        print("OK - Procesador de imagenes cargado correctamente")
    except Exception as e:
        print(f"ERROR - Error cargando procesador de imagenes: {e}")
        sys.exit(1)
    
    nodo = NodoWorker(id_nodo)

    try:
        # Configurar el daemon para escuchar en localhost
        daemon = Pyro5.server.Daemon(host="localhost")
        
        # Registrar en el NameServer
        ns = Pyro5.api.locate_ns()
        uri = daemon.register(nodo)
        ns.register(f"nodo.{id_nodo}", uri)
        
        print("=" * 50)
        print(f"NODO WORKER {id_nodo} INICIADO CORRECTAMENTE")
        print(f"URI: {uri}")
        print(f"Host: localhost")
        print(f"Estado inicial: {nodo.estado}")
        print("Transformaciones disponibles:")
        for transformacion in nodo.procesador.transformaciones.keys():
            print(f"  - {transformacion}")
        print("Esperando trabajos...")
        print("=" * 50)
        
        # Mantener el nodo activo
        daemon.requestLoop()
        
    except Pyro5.errors.NamingError as e:
        print(f"ERROR: No se puede encontrar el NameServer")
        print("Asegurate de ejecutar primero: python -m Pyro5.nameserver")
        print(f"Error detallado: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()