# Rutina para convertir el DataFrame de registros en multiples fuentes de informacion
import os
from pathlib import Path

from simular_registros import generar_registros

# 1. Configuracion (cambiar segun su tabla)
NOMBRE_ENTIDAD = "registros"
# Este archivo vive en src/, asi que la raiz del proyecto es parents[1]
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
CARPETA_CRUDOS = CARPETA_PROYECTO / "data" / "crudo"

# 2. Funciones genericas para elaborar los archivos

# 2.1 CREAR LA CARPETA SI NO EXISTE
def preparar_carpeta(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


# 2.2 EXPORTAR A CSV
def exportar_csv(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.csv"
    datos_df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


# 2.3 EXPORTAR A JSON
def exportar_json(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.json"
    datos_df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


# 2.4 EXPORTAR A EXCEL
def exportar_excel(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.xlsx"
    datos_df.to_excel(ruta, index=False, sheet_name="registros")
    return ruta


# 3. Genero los archivos en mi proyecto

def exportar_registros_crudos(datos_sucios_df):
    return [
        exportar_csv(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_sucio"),

        exportar_json(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_sucio"),

        exportar_excel(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_sucio"),
    ]


if __name__ == "__main__":
    df = generar_registros()

    for ruta in exportar_registros_crudos(df):
        print(f"{ruta} -> {df.shape}")