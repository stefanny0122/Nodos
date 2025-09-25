from enum import Enum

class EstadoNodo(Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    CON_ERROR = "con_error"
    PROCESANDO = "procesando"
    MANTENIMIENTO = "mantenimiento"