"""Limpia la tabla categorias del proyecto integrador (HU L01 de Kaizen).

Uso:
    python notebook/limpieza/limpiar_categorias.py
    python notebook/limpieza/limpiar_categorias.py ruta/a/categorias_crudo.csv

Sin argumentos lee datos/crudos/categorias_crudo.csv desde la raíz del
proyecto. Genera categorias_limpio.csv y categorias_catalogo.csv. Si el
archivo de entrada está en una carpeta crudos/, los resultados se guardan
en la carpeta hermana limpios/; si no, en la misma carpeta de la entrada.
"""

import sys
from pathlib import Path

import pandas as pd

COLUMNAS_OBLIGATORIAS = ["id", "nombre", "descripcion", "area_responsable"]
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_CRUDO = CARPETA_PROYECTO / "datos" / "crudos" / "categorias_crudo.csv"


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico completo: shape, info, nulos y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("Shape:", df.shape)
    print("\nInfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def leer_datos(ruta):
    """Lee el CSV sucio con pandas y revisa que tenga las columnas de la HU."""
    df = pd.read_csv(ruta)
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al archivo le faltan las columnas {faltantes}")
    return df


def limpiar(df):
    """Aplica cada corrección de los criterios y devuelve el DataFrame limpio."""
    # 1. Quitar los duplicados exactos.
    df = df.drop_duplicates()

    # 2. Unificar el nombre: sin espacios sobrantes y en formato Título.
    df["nombre"] = df["nombre"].str.strip().str.title()

    # 3. Quitar las tildes para que "Logística" y "Logistica" queden iguales.
    df["nombre"] = (
        df["nombre"]
        .str.normalize("NFKD")
        .str.encode("ascii", "ignore")
        .str.decode("utf-8")
    )

    # 4. Rellenar los nulos de las columnas de texto.
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")

    # 5. Crear la columna con el largo de la descripción.
    df["largo_desc"] = df["descripcion"].str.len()

    # 6. Volver a quitar duplicados exactos por si la normalización creó nuevos.
    df = df.drop_duplicates()
    return df


def sacar_catalogo(df):
    """Devuelve el catálogo real: una sola fila por categoría."""
    return df.drop_duplicates(subset=["nombre"])


def carpeta_salida(ruta_entrada):
    """Decide dónde guardar: datos/limpios si la entrada viene de datos/crudos."""
    carpeta = ruta_entrada.resolve().parent
    if carpeta.name == "crudos":
        carpeta = carpeta.parent / "limpios"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta

def exportar_limpio(df, carpeta):
    """Exporta el DataFrame limpio en CSV, Excel y JSON."""
    base = carpeta / "categorias_limpio"
    rutas = [base.with_suffix(".csv"), base.with_suffix(".xlsx"), base.with_suffix(".json")]
    df.to_csv(rutas[0], index=False, encoding="utf-8")
    df.to_excel(rutas[1], index=False, sheet_name="categorias")
    df.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    return rutas	

def verificar(df):
    """Comprueba que no queden nulos obligatorios ni duplicados exactos."""
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    estado = "OK" if nulos == 0 and duplicados == 0 else "REVISAR"
    print(f"\nVerificación: nulos obligatorios={nulos}, duplicados exactos={duplicados} -> {estado}")


def main():
    """Ejecuta la limpieza completa desde la línea de comandos."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/limpieza/limpiar_categorias.py [ruta/a/categorias_crudo.csv]")

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
    print(f"Categorías en el catálogo: {len(catalogo)} -> {sorted(catalogo['nombre'])}")
    verificar(df)

    salida = carpeta_salida(ruta_entrada)
    print()
    for ruta in exportar_limpio(df, salida):
        print(f"Guardado: {ruta} {df.shape}")
    ruta_catalogo = salida / "categorias_catalogo.csv"
    catalogo.to_csv(ruta_catalogo, index=False, encoding="utf-8")
    print(f"Guardado: {ruta_catalogo} {catalogo.shape}")


if __name__ == "__main__":
    main()