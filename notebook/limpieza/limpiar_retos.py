import pandas as pd
from datetime import datetime
from ..exportaciones.exportar_retos import CARPETA_CRUDOS, NOMBRE_ENTIDAD


# Recomendaciones generales para limpiar un archivo con pandas

# 1. Variables para identificar valores correctos
ESTADOS_VALIDOS = ["ABIERTO", "EN PROCESO", "CERRADO", "EVALUACION"]
# Aceptamos el formato ISO y el formato Latino que mezclaste en la simulación
FORMATOS_FECHA = ["%Y-%m-%d", "%d/%m/%Y"] 

# Función auxiliar para evitar errores

def verificar_valor_vacio(valor):
    return pd.isna(valor) or str(valor).strip() == "" or valor is None

def leer_datos_crudos():
    ruta = CARPETA_CRUDOS / f"{NOMBRE_ENTIDAD}_crudo.csv"
    return pd.read_csv(ruta)

def limpiar_texto(texto):
    if verificar_valor_vacio(texto):
        return None 
    # Quitamos los espacios sobrantes que se agregaron en la simulación del 10%
    return str(texto).strip().capitalize()

def limpiar_estado(estado):
    if verificar_valor_vacio(estado):
        return "EVALUACION" # Valor por defecto si falta
    
    # Limpiamos espacios y pasamos a mayúsculas para arreglar "en_curso" o "Cerrado "
    estado_limpio = str(estado).strip().upper()
    
    # Homologamos variantes conocidas
    if estado_limpio == "EN_CURSO":
        estado_limpio = "EN PROCESO"
        
    if estado_limpio not in ESTADOS_VALIDOS:
        return "EVALUACION" # Si es un estado desconocido, lo mandamos a revisión
    return estado_limpio

def limpiar_fecha(fecha):
    if verificar_valor_vacio(fecha):
        return None
    
    fecha = str(fecha).strip()
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(fecha, formato)
        except ValueError:
            print(ValueError)
    return None
