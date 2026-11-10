"""Limpieza de la tabla registros del proyecto integrador (HU L01 de Kaizen).

Uso (desde cualquier carpeta, incluido el boton Run de VS Code):
    python src/limpiar_registros.py
    python src/limpiar_registros.py otra_entrada.csv [ruta_salida]

Sin argumentos lee data/crudo/registros_sucio.csv y guarda data/limpio/registros_limpio.csv.
"""
import io
import os
import sys
from pathlib import Path

import pandas as pd

# Este archivo vive en src/, asi que la raiz del proyecto es parents[1]
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_ENTRADA_DEFECTO = str(CARPETA_PROYECTO / "data" / "crudo" / "registros_sucio.csv")
RUTA_SALIDA_DEFECTO = str(CARPETA_PROYECTO / "data" / "limpio" / "registros_limpio.csv")
COLUMNAS_OBLIGATORIAS = ["id", "fecha_registro", "estado", "id_usuario", "id_reto"]


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico: shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    buffer = io.StringIO()
    df.info(buf=buffer)
    print(buffer.getvalue())
    print("Nulos por columna:")
    print(df.isna().sum())
    print("Duplicados exactos:", df.duplicated().sum())


def convertir_fechas(serie):
    """Convierte fechas en dos formatos (ISO 'AAAA-MM-DD HH:MM:SS' y 'DD/MM/AAAA HH:MM').

    Se parsea cada formato por separado: usar dayfirst=True sobre fechas ISO
    intercambia el día y el mes, así que solo se aplica a las fechas con barras.
    Lo que no se pueda convertir queda como NaT (errors="coerce").
    """
    texto = serie.astype("string").str.strip()
    es_iso = texto.str.match(r"^\d{4}-\d{2}-\d{2}")
    resultado = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")
    resultado[es_iso] = pd.to_datetime(
        texto[es_iso], format="mixed", dayfirst=False, errors="coerce"
    )
    resultado[~es_iso] = pd.to_datetime(
        texto[~es_iso], format="mixed", dayfirst=True, errors="coerce"
    )
    return resultado


def unificar_estado(serie):
    """Quita espacios, pasa a mayúsculas y cambia espacios internos por guion bajo."""
    return serie.str.strip().str.upper().str.replace(" ", "_")


def limpiar(df):
    """Aplica todas las correcciones de la HU L01 y devuelve el DataFrame limpio."""
    # 1. Quitar duplicados exactos
    df = df.drop_duplicates()

    # 2. Convertir la fecha (dos formatos)
    df["fecha_registro"] = convertir_fechas(df["fecha_registro"])

    # 3. Unificar el estado
    df["estado"] = unificar_estado(df["estado"])

    # 4. Rellenar observaciones vacías
    df["observacion"] = df["observacion"].fillna("Sin observacion")

    # 5. Detectar participaciones repetidas (mismo usuario y mismo reto)
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"\nFilas con participaciones repetidas (usuario + reto): {len(repetidos)}")

    # 6. Dejar solo la primera participación de cada par
    df = df.drop_duplicates(subset=["id_usuario", "id_reto"], keep="first")

    # 7. Crear la columna mes para agrupar después
    df["mes"] = df["fecha_registro"].dt.to_period("M")

    return df


def main():
    """Lee el CSV, muestra diagnóstico, limpia, vuelve a diagnosticar y guarda."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA_DEFECTO
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else RUTA_SALIDA_DEFECTO

    df = pd.read_csv(ruta_entrada)
    filas_antes = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print(f"\nFilas antes: {filas_antes} | después: {len(df)} | eliminadas: {filas_antes - len(df)}")

    # Verificación de los criterios finales
    nulos_obligatorias = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    print(f"Nulos en columnas obligatorias: {nulos_obligatorias}")
    print(f"Duplicados exactos: {df.duplicated().sum()}")

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Archivo limpio guardado en: {ruta_salida}")


if __name__ == "__main__":
    main()