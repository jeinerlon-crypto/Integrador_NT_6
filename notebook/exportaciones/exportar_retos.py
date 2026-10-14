import json
from pathlib import Path

#1 Configuracion(Segun su tabla)
NOMBRE_ENTIDAD="retos"

CARPETA_PROYECTO=Path(__file__).resolve().parents[2]

CARPETA_CRUDOS=CARPETA_PROYECTO/"datos"/"crudos"

CARPETA_LIMPIOS=CARPETA_PROYECTO/"datos"/"limpios"

CARPETA_REPORTES=CARPETA_PROYECTO/"datos"/"reportes"

#2 Funciones genericas para elaborar los archivos

#2.1 CREAR LA CARPETA SI NO EXISTE

def preparar_carpetas(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta

#2.2 Exportar a csv

def exportar_csv(datos_df, carpeta, nombre_archivo):
    ruta=preparar_carpetas(carpeta)/f"(nombre_archivo).csv"
    datos_df.to_csv(ruta, index=False, sep=";", encoding="utf-8-sig")
    return ruta

#2.3 Exportar a json

def exportar_json(datos_df,carpeta, nombre_archivo):
    ruta=preparar_carpetas(carpeta)/f"(nombre_archivo).json"
    datos_df.to_json(ruta, orient="records", date_format="iso", ident=2)
    return ruta

#2.4 Exportar a Excel

def exportar_excel(datos_df, carpeta, nombre_archivo):
    ruta=preparar_carpetas(carpeta)/f"(nombre_archivo).xlsx"
    datos_df.to_excel(ruta, index=False, engine="openpyxl")
    return ruta


#3 Genero los archivos 

def exportar_usuarios_crudos(datos_sucios_df):
    return[
        exportar_csv(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudo"),
        exportar_json(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudo"),
        exportar_excel (datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudo")
    ]
