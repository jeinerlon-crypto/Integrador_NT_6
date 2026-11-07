"""Limpia la tabla prioridades del proyecto integrador (HU L01 de Kaizen).

Uso:
    python notebook/limpieza/limpiar_prioridades.py
    python notebook/limpieza/limpiar_prioridades.py ruta/a/prioridades_crudo.csv

Sin argumentos lee datos/crudos/prioridades_crudo.csv desde la raíz del
proyecto. Genera prioridades_limpio.csv, .xlsx y .json y
prioridades_catalogo.csv. Si el archivo de entrada está en una carpeta
crudos/, los resultados se guardan en la carpeta hermana limpios/; si no,
en la misma carpeta de la entrada.
"""

import csv
import sys
from pathlib import Path

import pandas as pd

COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_CRUDO = CARPETA_PROYECTO / "datos" / "crudos" / "prioridades_crudo.csv"

# Nivel de cada prioridad, con el nombre ya unificado con capitalize().
NIVELES = {"Muy alta": 1, "Alta": 2, "Media": 3, "Baja": 4, "Muy baja": 5}

# Días máximos de respuesta de cada nivel (sirve para verificar el resultado).
DIAS = {1: 1, 2: 3, 3: 5, 4: 8, 5: 15}

# Niveles escritos como palabra. Los criterios piden tres, dos y uno;
# se agregan cuatro y cinco porque también aparecen en los datos.
PALABRAS_NIVEL = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}

LIMITE_ABSURDO = 60


def detectar_separador(ruta):
    """Detecta si el CSV usa coma, punto y coma o tabulador como separador."""
    with open(ruta, encoding="utf-8-sig") as archivo:
        primera_linea = archivo.readline()
    try:
        return csv.Sniffer().sniff(primera_linea, delimiters=",;\t").delimiter
    except csv.Error:
        return ","


def leer_datos(ruta):
    """Lee el CSV crudo con pandas y revisa que tenga las columnas de la HU."""
    # utf-8-sig lee bien el archivo tenga o no BOM.
    df = pd.read_csv(ruta, sep=detectar_separador(ruta), encoding="utf-8-sig")
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al archivo le faltan las columnas {faltantes}")
    return df


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico completo: shape, info, nulos y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("Shape:", df.shape)
    print("\nInfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def limpiar_nombre(df):
    """Quita espacios sobrantes y deja el nombre con solo la primera letra en mayúscula."""
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    desconocidos = sorted(set(df["nombre"].dropna()) - set(NIVELES))
    if desconocidos:
        print(f"\nAviso: nombres que no están en NIVELES: {desconocidos}")
    return df


def limpiar_nivel(df):
    """Convierte nivel a número y rellena los vacíos con el nivel que le toca al nombre."""
    nivel = df["nivel"].astype("string").str.strip().str.lower()
    nivel = nivel.replace(PALABRAS_NIVEL)
    df["nivel"] = pd.to_numeric(nivel, errors="coerce")
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES))
    df["nivel"] = df["nivel"].astype("Int64")
    return df


def limpiar_dias(df):
    """Convierte los días a número, anula los absurdos y rellena con la mediana."""
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    absurdos = int((df["dias_max_respuesta"] > LIMITE_ABSURDO).sum())
    df.loc[df["dias_max_respuesta"] > LIMITE_ABSURDO, "dias_max_respuesta"] = None
    print(f"\nValores absurdos (> {LIMITE_ABSURDO}) marcados como nulo: {absurdos}")

    # Mediana de los días de cada nivel; si un nivel no tiene datos, la mediana general.
    mediana_nivel = df.groupby("nivel")["dias_max_respuesta"].transform("median")
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(mediana_nivel)
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(df["dias_max_respuesta"].median())
    df["dias_max_respuesta"] = df["dias_max_respuesta"].round().astype("Int64")
    return df


def limpiar(df):
    """Aplica cada corrección de los criterios y devuelve el DataFrame limpio."""
    df = df.drop_duplicates().copy()
    df = limpiar_nombre(df)
    df = limpiar_nivel(df)
    df = limpiar_dias(df)
    # Por si la normalización dejó filas idénticas que antes no lo eran.
    return df.drop_duplicates()


def sacar_catalogo(df):
    """Devuelve el catálogo real: una fila por prioridad, ordenado por nivel."""
    catalogo = df.drop_duplicates(subset=["nombre"])
    return catalogo.sort_values("nivel")


def verificar(df, catalogo):
    """Comprueba nulos, duplicados y que nivel y días cuadren con el nombre."""
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    nivel_raro = int((df["nivel"] != df["nombre"].map(NIVELES)).sum())
    dias_raros = int((df["dias_max_respuesta"] != df["nivel"].map(DIAS)).sum())
    print("\nVerificación:")
    print(f"  Nulos en columnas obligatorias: {nulos}")
    print(f"  Duplicados exactos: {duplicados}")
    print(f"  Filas en el catálogo: {len(catalogo)} (deberían ser {len(NIVELES)})")
    print(f"  Filas con nivel que no corresponde al nombre: {nivel_raro}")
    print(f"  Filas con días que no corresponden al nivel: {dias_raros}")
    correcto = nulos == 0 and duplicados == 0 and len(catalogo) == len(NIVELES)
    print(f"  Estado: {'OK' if correcto else 'REVISAR'}")


def exportar_limpio(df, carpeta):
    """Exporta el DataFrame limpio en CSV, Excel y JSON."""
    base = carpeta / "prioridades_limpio"
    rutas = [base.with_suffix(".csv"), base.with_suffix(".xlsx"), base.with_suffix(".json")]
    df.to_csv(rutas[0], index=False, encoding="utf-8")
    df.to_excel(rutas[1], index=False, sheet_name="prioridades")
    df.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    return rutas


def carpeta_salida(ruta_entrada):
    """Decide dónde guardar: datos/limpios si la entrada viene de datos/crudos."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "crudos":
        carpeta = carpeta.parent / "limpios"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def main():
    """Ejecuta la limpieza completa desde la línea de comandos."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/limpieza/limpiar_prioridades.py [ruta/a/prioridades_crudo.csv]")

    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_CRUDO
    if not ruta_entrada.exists():
        sys.exit(f"Error: no se encontró el archivo {ruta_entrada}")

    df = leer_datos(ruta_entrada)
    filas_antes = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = limpiar(df)
    catalogo = sacar_catalogo(df)
    filas_despues = len(df)

    print("\n===== DIAGNÓSTICO DESPUÉS DE LIMPIAR =====")
    print("Shape:", df.shape)
    print("\nNulos por columna:")
    print(df.isna().sum())

    print(f"\nFilas antes: {filas_antes}")
    print(f"Filas después: {filas_despues}")
    print(f"Filas eliminadas: {filas_antes - filas_despues}")
    print("\nCatálogo:")
    print(catalogo[["nombre", "nivel", "dias_max_respuesta"]].to_string(index=False))
    verificar(df, catalogo)

    salida = carpeta_salida(ruta_entrada)
    print()
    for ruta in exportar_limpio(df, salida):
        print(f"Guardado: {ruta} {df.shape}")
    ruta_catalogo = salida / "prioridades_catalogo.csv"
    catalogo.to_csv(ruta_catalogo, index=False, encoding="utf-8")
    print(f"Guardado: {ruta_catalogo} {catalogo.shape}")


if __name__ == "__main__":
    main()