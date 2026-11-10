"""Consultas de la HU Q01 sobre la tabla empresas del proyecto integrador.

Uso:
    python scripts/consultas_empresas.py empresas_limpio.csv

Lee el archivo LIMPIO, resuelve cinco consultas con pandas (cada una en su
propia funcion), imprime el titulo y el resultado de cada una, y guarda
empresas_consulta_N.csv en la misma carpeta del archivo de entrada.
"""

import sys
from pathlib import Path

import pandas as pd

# Cuantas filas se muestran en consola cuando el resultado es largo.
# El resultado completo siempre queda en el CSV.
FILAS_VISTA = 10


def cargar_datos(ruta):
    """Lee empresas_limpio.csv y devuelve el DataFrame con 'activa' como booleano."""
    df = pd.read_csv(ruta)
    # Si 'activa' llegara como texto, se convierte a True/False.
    if df["activa"].dtype == object or str(df["activa"].dtype).startswith("str"):
        df["activa"] = df["activa"].astype(str).str.strip().str.lower() == "true"
    return df


def mostrar(titulo, resultado, numero, carpeta, indice=False):
    """Imprime el titulo y el resultado, y guarda empresas_consulta_N.csv."""
    print(f"\n=== Consulta {numero}: {titulo} ===")
    if isinstance(resultado, pd.DataFrame) and len(resultado) > FILAS_VISTA:
        print(f"Total: {len(resultado)} empresas (se muestran las primeras {FILAS_VISTA})")
        print(resultado[["nombre", "sector", "activa"]].head(FILAS_VISTA).to_string())
    else:
        print(resultado.to_string())
    destino = carpeta / f"empresas_consulta_{numero}.csv"
    resultado.to_csv(destino, index=indice, encoding="utf-8")
    print(f"-> guardado en {destino}")


def consulta_1_activas(df, carpeta):
    """Consulta 1: ¿Cuales son las empresas activas?"""
    activas = df[df["activa"] == True]  # noqa: E712
    mostrar("¿Cuales son las empresas activas?", activas, 1, carpeta)
    return activas


def consulta_2_logistica(df, carpeta):
    """Consulta 2: ¿Cuales son las empresas del sector Logistica, ordenadas por nombre?"""
    logistica = df[df["sector"] == "Logistica"].sort_values("nombre")
    mostrar("¿Cuales son las empresas del sector Logistica, ordenadas por nombre?",
            logistica, 2, carpeta)
    return logistica


def consulta_3_conteo_por_sector(df, carpeta):
    """Consulta 3: ¿Cuantas empresas hay por sector? (conteo rapido con value_counts)."""
    conteo = df["sector"].value_counts()
    mostrar("¿Cuantas empresas hay por sector? (conteo rapido)", conteo, 3,
            carpeta, indice=True)
    return conteo


def consulta_4_groupby_sector(df, carpeta):
    """Consulta 4 (GROUPBY): ¿Cuantas empresas hay por sector, de mayor a menor?"""
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    mostrar("GROUPBY: ¿Cuantas empresas hay por sector, de mayor a menor?",
            por_sector, 4, carpeta, indice=True)
    return por_sector


def consulta_5_groupby_sector_activa(df, carpeta):
    """Consulta 5 (GROUPBY doble): ¿Cuantas empresas activas e inactivas hay por sector?"""
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    mostrar("GROUPBY doble: ¿Cuantas empresas activas e inactivas hay por sector?",
            tabla, 5, carpeta, indice=True)
    return tabla


def main():
    """Punto de entrada: valida el argumento, carga los datos y corre las cinco consultas."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/consultas_empresas.py empresas_limpio.csv")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"No se encontro el archivo: {ruta}")
        sys.exit(1)

    df = cargar_datos(ruta)
    carpeta = ruta.parent  # los resultados se guardan junto al archivo de entrada

    consulta_1_activas(df, carpeta)
    consulta_2_logistica(df, carpeta)
    consulta_3_conteo_por_sector(df, carpeta)
    consulta_4_groupby_sector(df, carpeta)
    consulta_5_groupby_sector_activa(df, carpeta)


if __name__ == "__main__":
    main()
