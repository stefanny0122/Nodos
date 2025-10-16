#!/usr/bin/env python3
"""
Nodo Worker - Sistema de Procesamiento Distribuido de Imágenes
CON TRANSFERENCIA DE ARCHIVOS
"""

import sys
import os
import signal
import Pyro5.api
import Pyro5.server
import Pyro5.errors
import threading
import base64
import tempfile
import time
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Importaciones locales del nodo worker
from procesador_imagen import ProcesadorImagenesImpl
from utils.logger import get_logger

logger = get_logger("NodoWorker")

@Pyro5.api.expose
class NodoWorker:
    """
    Nodo worker distribuido que procesa imágenes.
    Expone sus métodos vía Pyro5 para ser llamados remotamente.
    """
    
    def __init__(self, id_nodo: str, capacidad_maxima: int = 5):
        self.id_nodo = id_nodo
        self.estado = "activo"
        self.procesador = ProcesadorImagenesImpl()
        self.trabajos_activos = 0
        self.capacidad_maxima = capacidad_maxima
        self.lock = threading.Lock()
        self.estadisticas = {
            "trabajos_completados": 0,
            "trabajos_fallidos": 0,
            "tiempo_total_procesamiento": 0.0,
            "ultima_actividad": None,
            "inicio": datetime.now().isoformat()
        }
        
        logger.info(f"Nodo {id_nodo} inicializado con capacidad: {capacidad_maxima}")
    
    # ==================== MÉTODOS EXPUESTOS VÍA PYRO5 ====================
    
    def obtener_estado(self) -> Dict[str, Any]:
        """
        Retorna el estado actual del nodo.
        Llamado remotamente por el servidor FastAPI.
        """
        with self.lock:
            tiempo_promedio = (
                self.estadisticas["tiempo_total_procesamiento"] / 
                self.estadisticas["trabajos_completados"]
                if self.estadisticas["trabajos_completados"] > 0 else 0
            )
            
            return {
                "id_nodo": self.id_nodo,
                "estado": self.estado,
                "trabajos_activos": self.trabajos_activos,
                "capacidad_maxima": self.capacidad_maxima,
                "capacidad_disponible": self.capacidad_maxima - self.trabajos_activos,
                "trabajos_completados": self.estadisticas["trabajos_completados"],
                "trabajos_fallidos": self.estadisticas["trabajos_fallidos"],
                "tiempo_promedio_procesamiento": round(tiempo_promedio, 2),
                "ultima_actividad": self.estadisticas["ultima_actividad"],
                "timestamp": datetime.now().isoformat()
            }
    
    def esta_disponible(self) -> bool:
        """
        Verifica si el nodo puede aceptar más trabajos.
        Llamado por el balanceador de carga del servidor.
        """
        with self.lock:
            disponible = (
                self.estado == "activo" and 
                self.trabajos_activos < self.capacidad_maxima
            )
            return disponible
    
    def ping(self) -> Dict[str, Any]:
        """
        Health check para verificar que el nodo está vivo.
        """
        return {
            "nodo": self.id_nodo,
            "activo": True,
            "estado": self.estado,
            "timestamp": datetime.now().isoformat()
        }
    
    def saludar(self) -> str:
        """Método de prueba para verificar conectividad RPC"""
        return f"Hola desde nodo {self.id_nodo} - Estado: {self.estado}"
    
    def procesar_con_archivo(
        self, 
        id_trabajo: str, 
        nombre_archivo: str, 
        imagen_codificada: str, 
        transformaciones: List[Dict]
    ) -> Dict[str, Any]:
        """
        Procesa una imagen recibida como base64 y devuelve UNA imagen con todos los cambios.
        
        Args:
            id_trabajo: ID único del trabajo
            nombre_archivo: Nombre original del archivo
            imagen_codificada: Imagen codificada en base64
            transformaciones: Lista de transformaciones a aplicar
            
        Returns:
            Dict con resultado del procesamiento incluyendo imagen codificada
        """
        tiempo_inicio = datetime.now()
        
        # Validar disponibilidad antes de aceptar
        if not self.esta_disponible():
            logger.warning(
                f"[{self.id_nodo}] Rechazando trabajo {id_trabajo} - "
                f"Capacidad: {self.trabajos_activos}/{self.capacidad_maxima}"
            )
            return {
                "id_trabajo": id_trabajo,
                "nodo": self.id_nodo,
                "exito": False,
                "error": "Nodo sin capacidad disponible",
                "timestamp_fin": datetime.now().isoformat()
            }
        
        logger.info(
            f"[{self.id_nodo}] Procesando trabajo: {id_trabajo} - "
            f"Archivo: {nombre_archivo}, Transformaciones: {len(transformaciones)}"
        )
        
        # Incrementar contador (thread-safe)
        with self.lock:
            self.trabajos_activos += 1
            if self.trabajos_activos > 0:
                self.estado = "procesando"
            self.estadisticas["ultima_actividad"] = datetime.now().isoformat()
        
        try:
            # Decodificar imagen
            try:
                imagen_bytes = base64.b64decode(imagen_codificada)
                logger.debug(f"[{id_trabajo}] Imagen decodificada: {len(imagen_bytes)} bytes")
            except Exception as e:
                raise ValueError(f"Error decodificando imagen base64: {e}")
            
            # Crear archivos temporales
            temp_entrada = None
            temp_salida = None
            
            try:
                # Crear archivo temporal de entrada
                extension = os.path.splitext(nombre_archivo)[1] or '.png'
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_entrada:
                    temp_entrada.write(imagen_bytes)
                    temp_entrada_path = temp_entrada.name
                
                # Crear archivo temporal de salida
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_salida:
                    temp_salida_path = temp_salida.name
                
                # Procesar imagen - TODAS LAS TRANSFORMACIONES EN UNA SOLA IMAGEN
                inicio_procesamiento = time.time()
                
                exito = self.procesador.procesar(
                    ruta_entrada=temp_entrada_path,
                    ruta_salida=temp_salida_path,
                    lista_transformaciones=transformaciones,
                    id_trabajo=id_trabajo
                )
                
                tiempo_procesamiento = time.time() - inicio_procesamiento
                
                # Leer y codificar RESULTADO FINAL si fue exitoso
                imagen_resultado_codificada = None
                if exito and os.path.exists(temp_salida_path):
                    with open(temp_salida_path, "rb") as f:
                        imagen_resultado_codificada = base64.b64encode(f.read()).decode('utf-8')
                    logger.debug(f"[{id_trabajo}] Imagen final codificada: {len(imagen_resultado_codificada)} caracteres")
                
                # Calcular tiempo total
                tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
                
                # Actualizar estadísticas
                with self.lock:
                    if exito and imagen_resultado_codificada:
                        self.estadisticas["trabajos_completados"] += 1
                    else:
                        self.estadisticas["trabajos_fallidos"] += 1
                    self.estadisticas["tiempo_total_procesamiento"] += tiempo_procesamiento
                    self.estadisticas["ultima_actividad"] = datetime.now().isoformat()
                
                resultado = {
                    "id_trabajo": id_trabajo,
                    "nodo": self.id_nodo,
                    "exito": exito and bool(imagen_resultado_codificada),
                    "imagen_resultado": imagen_resultado_codificada,  # ÚNICA IMAGEN CON TODOS LOS CAMBIOS
                    "tiempo_procesamiento": round(tiempo_procesamiento, 2),
                    "tiempo_total": round(tiempo_total, 2),
                    "transformaciones_aplicadas": len(transformaciones),
                    "timestamp_inicio": tiempo_inicio.isoformat(),
                    "timestamp_fin": datetime.now().isoformat()
                }
                
                if exito and imagen_resultado_codificada:
                    logger.info(
                        f"[{self.id_nodo}] ✓ Trabajo {id_trabajo} completado - "
                        f"{len(transformaciones)} transformaciones en {tiempo_procesamiento:.2f}s"
                    )
                else:
                    error_msg = "Error procesando imagen - no se generó resultado final"
                    logger.error(f"[{self.id_nodo}] ✗ Trabajo {id_trabajo} falló: {error_msg}")
                    resultado["error"] = error_msg
                
                return resultado
                
            finally:
                # Limpiar archivos temporales
                try:
                    if temp_entrada and os.path.exists(temp_entrada_path):
                        os.unlink(temp_entrada_path)
                    if temp_salida and os.path.exists(temp_salida_path):
                        os.unlink(temp_salida_path)
                except Exception as e:
                    logger.warning(f"[{id_trabajo}] Error limpiando temporales: {e}")
            
        except Exception as e:
            tiempo_fin = datetime.now()
            tiempo_total = (tiempo_fin - tiempo_inicio).total_seconds()
            
            logger.error(
                f"[{self.id_nodo}] Error en trabajo {id_trabajo}: {e}",
                exc_info=True
            )
            
            with self.lock:
                self.estadisticas["trabajos_fallidos"] += 1
                self.estadisticas["tiempo_total_procesamiento"] += tiempo_total
                self.estadisticas["ultima_actividad"] = tiempo_fin.isoformat()
            
            return {
                "id_trabajo": id_trabajo,
                "nodo": self.id_nodo,
                "exito": False,
                "error": str(e),
                "tiempo_total": round(tiempo_total, 2),
                "timestamp_inicio": tiempo_inicio.isoformat(),
                "timestamp_fin": tiempo_fin.isoformat()
            }
            
        finally:
            # Decrementar contador
            with self.lock:
                self.trabajos_activos -= 1
                if self.trabajos_activos == 0:
                    self.estado = "activo"
    
    def procesar(
        self, 
        id_trabajo: str, 
        ruta_entrada: str, 
        ruta_salida: str, 
        lista_transformaciones: list
    ) -> Dict[str, Any]:
        """
        MÉTODO ORIGINAL - ahora usa transferencia de archivos internamente
        """
        logger.warning(f"[{self.id_nodo}] Usando método obsoleto 'procesar' para {id_trabajo}")
        
        # Para compatibilidad, intentar leer el archivo localmente
        try:
            if os.path.exists(ruta_entrada):
                with open(ruta_entrada, "rb") as f:
                    imagen_codificada = base64.b64encode(f.read()).decode('utf-8')
                
                nombre_archivo = os.path.basename(ruta_entrada)
                
                return self.procesar_con_archivo(
                    id_trabajo=id_trabajo,
                    nombre_archivo=nombre_archivo,
                    imagen_codificada=imagen_codificada,
                    transformaciones=lista_transformaciones
                )
            else:
                return {
                    "id_trabajo": id_trabajo,
                    "nodo": self.id_nodo,
                    "exito": False,
                    "error": f"Archivo no existe: {ruta_entrada}"
                }
                
        except Exception as e:
            return {
                "id_trabajo": id_trabajo,
                "nodo": self.id_nodo,
                "exito": False,
                "error": str(e)
            }
    
    def detener(self) -> Dict[str, Any]:
        """Inicia shutdown ordenado del nodo"""
        logger.info(f"Nodo {self.id_nodo} iniciando detención...")
        with self.lock:
            self.estado = "deteniendo"
        return {
            "mensaje": f"Nodo {self.id_nodo} deteniendo",
            "trabajos_pendientes": self.trabajos_activos
        }


# ==================== FUNCIONES DE INICIALIZACIÓN ====================

def validar_dependencias():
    """Valida dependencias requeridas antes de iniciar"""
    errores = []
    
    try:
        import Pyro5.api
        logger.info("✓ Pyro5 instalado")
    except ImportError:
        errores.append("Pyro5 no instalado. Ejecuta: pip install Pyro5")
    
    try:
        from PIL import Image
        logger.info("✓ Pillow instalado")
    except ImportError:
        errores.append("Pillow no instalado. Ejecuta: pip install Pillow")
    
    try:
        from procesador_imagen import ProcesadorImagenesImpl
        logger.info("✓ ProcesadorImagenesImpl disponible")
    except Exception as e:
        errores.append(f"Error cargando procesador: {e}")
    
    if errores:
        print("\n❌ ERRORES DE DEPENDENCIAS:")
        for error in errores:
            print(f"   • {error}")
        print()
        sys.exit(1)


def configurar_signal_handlers(nodo: NodoWorker, daemon):
    """Configura manejadores para shutdown ordenado"""
    def signal_handler(signum, frame):
        nombre_signal = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info(f"Señal {nombre_signal} recibida. Shutdown ordenado...")
        print(f"\n\n🛑 Deteniendo nodo {nodo.id_nodo}...")
        nodo.detener()
        daemon.shutdown()
        print("✓ Nodo detenido correctamente\n")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Función principal del nodo worker"""
    print("\n" + "="*70)
    print("NODO WORKER - Sistema de Procesamiento Distribuido de Imágenes")
    print("="*70 + "\n")
    
    if len(sys.argv) < 2:
        print("❌ Argumentos insuficientes\n")
        print("Uso: python nodo_worker.py <id_nodo> [capacidad] [host] [puerto]")
        print("\nEjemplos:")
        print("  python nodo_worker.py worker01")
        print("  python nodo_worker.py worker01 10")
        print("  python nodo_worker.py worker01 10 0.0.0.0 9090")
        print("\nParámetros:")
        print("  id_nodo   : Identificador único (ej: worker01)")
        print("  capacidad : Trabajos concurrentes (default: 5)")
        print("  host      : IP para bind (default: localhost)")
        print("  puerto    : Puerto RPC (default: auto)")
        print()
        sys.exit(1)

    # Parsear argumentos
    id_nodo = sys.argv[1]
    capacidad = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    host = sys.argv[3] if len(sys.argv) > 3 else "localhost"
    puerto = int(sys.argv[4]) if len(sys.argv) > 4 else 0  # 0 = auto
    
    print(f"Configuración:")
    print(f"  ID Nodo   : {id_nodo}")
    print(f"  Capacidad : {capacidad} trabajos concurrentes")
    print(f"  Host      : {host}")
    print(f"  Puerto    : {puerto if puerto > 0 else 'automático'}")
    print()
    
    # Validar dependencias
    print("Validando dependencias...")
    validar_dependencias()
    print()
    
    # Crear nodo
    nodo = NodoWorker(id_nodo, capacidad)
    daemon = None

    try:
        # Configurar daemon Pyro5
        logger.info(f"Configurando daemon Pyro5 en {host}...")
        if puerto > 0:
            daemon = Pyro5.server.Daemon(host=host, port=puerto)
        else:
            daemon = Pyro5.server.Daemon(host=host)
        
        # Configurar signal handlers
        configurar_signal_handlers(nodo, daemon)
        
        # Registrar en NameServer
        logger.info("Conectando con NameServer...")
        ns = Pyro5.api.locate_ns()
        uri = daemon.register(nodo)
        nombre_registro = f"nodo.{id_nodo}"
        ns.register(nombre_registro, uri)
        
        # Banner de inicio exitoso
        print("="*70)
        print(f"✓ NODO WORKER '{id_nodo}' INICIADO CORRECTAMENTE")
        print("="*70)
        print(f"URI Pyro5     : {uri}")
        print(f"Nombre NS     : {nombre_registro}")
        print(f"Estado        : {nodo.estado}")
        print(f"Capacidad     : {capacidad} trabajos concurrentes")
        print(f"\nTransformaciones disponibles:")
        for trans in sorted(nodo.procesador.transformaciones.keys()):
            print(f"  • {trans}")
        print("\n" + "="*70)
        print("Esperando trabajos remotos... (Ctrl+C para detener)")
        print("="*70 + "\n")
        
        # Loop principal - espera llamadas RPC
        daemon.requestLoop()
        
    except Pyro5.errors.NamingError as e:
        print("\n" + "!"*70)
        print("❌ ERROR: No se puede conectar con el NameServer")
        print("!"*70)
        print("\n📋 SOLUCIÓN:")
        print("1. Inicia el NameServer en otra terminal:")
        print("   python -m Pyro5.nameserver")
        print("\n2. Verifica que esté corriendo:")
        print("   python -m Pyro5.nsc list")
        print("\n3. Vuelve a iniciar este nodo worker")
        print(f"\nError: {e}")
        print("!"*70 + "\n")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown ordenado iniciado...")
        if daemon:
            nodo.detener()
            daemon.shutdown()
        logger.info(f"Nodo {id_nodo} detenido por usuario")
        print("✓ Nodo detenido correctamente\n")
        
    except Exception as e:
        logger.error(f"ERROR CRÍTICO: {e}", exc_info=True)
        print(f"\n❌ ERROR CRÍTICO: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()