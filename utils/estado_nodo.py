from enum import Enum

class EstadoNodo(Enum):
    ACTIVO = "activo"
    PROCESANDO = "procesando"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"