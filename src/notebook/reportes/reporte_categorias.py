"""Crea las tres gráficas de la HU G01 de la tabla categorias y sus conclusiones.

Uso:
    python notebook/reportes/reporte_categorias.py
    python notebook/reportes/reporte_categorias.py ruta/a/categorias_limpio.csv

Sin argumentos lee datos/limpios/categorias_limpio.csv desde la raíz del
proyecto. Guarda las gráficas en reportes/ en la raíz del proyecto e imprime
la ruta de cada una y las conclusiones.
"""

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Dibuja sin abrir ventanas, para que el script no se quede esperando.
import matplotlib.pyplot as plt
import pandas as pd

CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_REPORTES = CARPETA_PROYECTO / "reportes"
RUTA_LIMPIO = CARPETA_PROYECTO / "datos" / "limpios" / "categorias_limpio.csv"
FILAS_SIMULADAS = 250  # Filas que genera la HU F01 si no se encuentra el CSV crudo.
COLUMNAS_NECESARIAS = ["id", "nombre", "descripcion", "area_responsable", "largo_desc"]


def leer_datos(ruta):
    """Lee el CSV limpio con pandas y revisa que tenga las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltantes = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al archivo le faltan las columnas {faltantes}")
    return df


def guardar_grafica(numero):
    """Ajusta la figura, la guarda con dpi=120, la cierra y devuelve su ruta."""
    ruta = CARPETA_REPORTES / f"categorias_grafica_{numero}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df):
    """Barras horizontales: cuántas veces aparece cada categoría."""
    conteo = df["nombre"].value_counts().sort_values()
    plt.figure(figsize=(8, 5))
    conteo.plot(kind="barh")
    plt.title("Veces que aparece cada categoría")
    plt.xlabel("Cantidad de filas")
    plt.ylabel("Categoría")
    return guardar_grafica(1)


def grafica_2(df):
    """Torta: reparto de las filas por área responsable."""
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    plt.figure(figsize=(10, 8))
    por_area.plot(kind="pie", autopct="%1.1f%%", radius=0.85, labeldistance=1.08)
    plt.title("Reparto de categorías por área responsable")
    plt.xlabel("Porcentaje de filas por área")
    plt.ylabel("Área responsable", labelpad=60)
    return guardar_grafica(2)


def grafica_3(df):
    """Barras: largo promedio de la descripción por categoría."""
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    plt.figure(figsize=(9, 5))
    largos.plot(kind="bar")
    plt.title("Largo promedio de la descripción por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Largo promedio (caracteres)")
    plt.xticks(rotation=45, ha="right")
    return guardar_grafica(3)


def buscar_crudo(ruta_limpio):
    """Busca categorias_crudo.csv junto al limpio o en datos/crudos/; devuelve la ruta o None."""
    carpeta = ruta_limpio.resolve().parent
    candidatos = [
        carpeta / "categorias_crudo.csv",
        carpeta.parent / "crudos" / "categorias_crudo.csv",
    ]
    for ruta in candidatos:
        if ruta.exists():
            return ruta
    return None


def imprimir_conclusiones(df, ruta_limpio):
    """Imprime las conclusiones que pide la HU G01."""
    filas_limpias = len(df)
    categorias_reales = df["nombre"].nunique()
    ruta_crudo = buscar_crudo(ruta_limpio)

    if ruta_crudo:
        crudo = pd.read_csv(ruta_crudo)
        filas_crudas = len(crudo)
        variantes = crudo["nombre"].nunique()
        origen = f"comparando con {ruta_crudo}"
    else:
        filas_crudas = FILAS_SIMULADAS
        variantes = None
        origen = f"no se encontró categorias_crudo.csv; se usan las {FILAS_SIMULADAS} filas de la HU F01"

    eliminadas = filas_crudas - filas_limpias
    mayor = df["nombre"].value_counts()

    print("\n===== CONCLUSIONES =====")
    print(f"1. Filas eliminadas: {eliminadas} ({filas_crudas} -> {filas_limpias}), {origen}.")
    print("   Esas filas eran duplicados exactos. Las variantes de escritura no se borran:")
    print("   se unifican con strip, title y sin tildes, y así dejan de contar como categorías distintas.")
    if variantes is not None:
        print(f"   En el archivo crudo había {variantes} formas distintas de escribir el nombre.")

    estado = "correcto" if categorias_reales == 10 else "REVISAR: deberían ser 10"
    print(f"2. Categorías reales al final: {categorias_reales} ({estado}).")
    print(f"   La más frecuente es {mayor.index[0]} ({mayor.iloc[0]} filas) y la menos frecuente "
          f"{mayor.index[-1]} ({mayor.iloc[-1]} filas).")

    print("3. Por qué el back debe declarar `nombre` como ÚNICO:")
    print("   Si la base de datos no lo impide, cada vez que alguien escribe 'Logística',")
    print("   'LOGISTICA' o ' logistica ' se crea una categoría nueva y el catálogo vuelve a")
    print("   llegar repetido. Con una restricción UNIQUE (normalizando el nombre antes de")
    print("   guardar), el back rechaza el duplicado en el momento de crearlo y no hace falta")
    print("   limpiar los datos después.")


def main():
    """Lee los datos, crea las tres gráficas e imprime sus rutas y las conclusiones."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/reportes/reporte_categorias.py [ruta/a/categorias_limpio.csv]")

    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_LIMPIO
    if not ruta_entrada.exists():
        sys.exit(f"Error: no se encontró el archivo {ruta_entrada}")

    df = leer_datos(ruta_entrada)
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    print("Gráficas guardadas:")
    for funcion in (grafica_1, grafica_2, grafica_3):
        print(f"  {funcion(df)}")

    imprimir_conclusiones(df, ruta_entrada)


if __name__ == "__main__":
    main()