"""Limpieza de la tabla empresas (HU L01 - Kaizen).

Uso:
    python scripts/limpiar_empresas.py empresas_sucio.csv [ruta_salida]

Por defecto guarda el resultado en data/limpio/empresas_limpio.csv.
"""
import sys
from pathlib import Path

import pandas as pd

# Columnas que no pueden quedar con nulos despues de limpiar
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nit", "sector", "telefono", "activa"]
RUTA_SALIDA_DEFECTO = Path("data") / "limpio" / "empresas_limpio.csv"


def leer_datos(ruta):
    """Lee el CSV con pandas; todo como texto para no perder ceros del nit."""
    return pd.read_csv(ruta, dtype=str)


def diagnostico(df, titulo, completo=True):
    """Imprime shape, info, nulos y duplicados exactos del DataFrame."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    if completo:
        print("\ninfo:")
        df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Elimina las filas que son duplicados exactos."""
    return df.drop_duplicates()


def limpiar_texto(df):
    """Quita espacios sobrantes del nombre y unifica el sector (Title Case)."""
    df["nombre"] = df["nombre"].str.strip()
    df["sector"] = df["sector"].str.strip().str.title()
    return df


def limpiar_nit(df):
    """Deja el nit en un solo formato: sin puntos ni guiones."""
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)
    return df


def limpiar_telefono(df):
    """Deja el telefono solo con digitos."""
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    return df


def convertir_activa(df):
    """Convierte 'activa' (texto True/SI/1/False/NO/0) a booleano real."""
    mapa = {"TRUE": True, "SI": True, "1": True,
            "FALSE": False, "NO": False, "0": False}
    df["activa"] = (df["activa"].astype(str).str.strip().str.upper().map(mapa)
                    .astype("boolean"))
    return df


def rellenar_contacto(df):
    """Rellena los contactos vacios con 'Sin contacto'."""
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    return df


def marcar_correos(df):
    """Crea la columna correo_valido: True si el correo contiene '@'."""
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    return df


def limpiar(df):
    """Aplica todas las correcciones de los criterios, en orden."""
    df = quitar_duplicados(df).copy()
    df = limpiar_texto(df)
    df = limpiar_nit(df)
    df = limpiar_telefono(df)
    df = convertir_activa(df)
    df = rellenar_contacto(df)
    df = marcar_correos(df)
    # Tras normalizar pueden aparecer duplicados que antes diferian por espacios
    return quitar_duplicados(df)


def guardar(df, ruta):
    """Crea la carpeta de salida si hace falta y guarda el CSV limpio."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def main():
    """Flujo completo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/limpiar_empresas.py empresas_sucio.csv")
        sys.exit(1)
    ruta_entrada = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else RUTA_SALIDA_DEFECTO

    df = leer_datos(ruta_entrada)
    filas_antes = len(df)
    diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = limpiar(df)
    diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR", completo=False)

    print(f"\nFilas eliminadas: {filas_antes - len(df)} "
          f"({filas_antes} -> {len(df)})")

    nulos = df[COLUMNAS_OBLIGATORIAS].isna().sum().sum()
    print("Nulos en columnas obligatorias:", nulos)
    print("Duplicados exactos restantes:", df.duplicated().sum())

    print("Archivo guardado en:", guardar(df, ruta_salida))


if __name__ == "__main__":
    main()
