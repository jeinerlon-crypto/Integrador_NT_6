"""Responde las cinco consultas de la HU Q01 sobre la tabla categorias.

Uso:
    python notebook/consultas/consultas_categorias.py
    python notebook/consultas/consultas_categorias.py ruta/a/categorias_limpio.csv

Sin argumentos lee datos/limpios/categorias_limpio.csv desde la raíz del
proyecto. Imprime el título y el resultado de cada consulta, en orden, y
guarda cada resultado como categorias_consulta_N.csv, .xlsx y .json en la
misma carpeta del archivo de entrada.
"""

import sys
from pathlib import Path

import pandas as pd

COLUMNAS_NECESARIAS = ["id", "nombre", "descripcion", "area_responsable", "largo_desc"]
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_LIMPIO = CARPETA_PROYECTO / "datos" / "limpios" / "categorias_limpio.csv"


def leer_datos(ruta):
    """Lee el CSV limpio con pandas y revisa que tenga las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltantes = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al archivo le faltan las columnas {faltantes}")
    return df


def mostrar_titulo(numero, titulo):
    """Imprime el encabezado con el número y el título de la consulta."""
    print(f"\n===== Consulta {numero}: {titulo} =====")


def guardar(resultado, carpeta, numero, con_indice):
    """Guarda el resultado como categorias_consulta_N en CSV, Excel y JSON."""
    tabla = resultado.reset_index() if con_indice else resultado
    tabla.columns.name = None
    base = carpeta / f"categorias_consulta_{numero}"
    rutas = [base.with_suffix(".csv"), base.with_suffix(".xlsx"), base.with_suffix(".json")]
    tabla.to_csv(rutas[0], index=False, encoding="utf-8")
    tabla.to_excel(rutas[1], index=False, sheet_name=f"consulta_{numero}")
    tabla.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    return rutas


def consulta_1(df):
    """Cuenta cuántas veces aparece cada categoría (detecta variantes)."""
    print("Pregunta: ¿Cuántas veces aparece cada categoría?")
    conteo = df["nombre"].value_counts()
    return conteo


def consulta_2(df):
    """Filtra las filas cuya descripción quedó como 'Sin descripcion'."""
    print("Pregunta: ¿Qué categorías no tienen descripción?")
    sin_desc = df[df["descripcion"] == "Sin descripcion"]
    return sin_desc


def consulta_3(df):
    """GROUPBY: largo promedio de la descripción por categoría."""
    print("Pregunta: ¿Cuál es el largo promedio de la descripción de cada categoría?")
    largos = (
        df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    )
    return largos


def consulta_4(df):
    """GROUPBY: cuántas categorías maneja cada área responsable."""
    print("Pregunta: ¿Cuántas categorías maneja cada área?")
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    return por_area


def consulta_5(df):
    """GROUPBY doble: tabla cruzada de categorías por área."""
    print("Pregunta: ¿Cuántas filas de cada categoría tiene cada área?")
    tabla = (
        df.groupby(["area_responsable", "nombre"])["id"].count().unstack(fill_value=0)
    )
    return tabla


def main():
    """Ejecuta las cinco consultas en orden, las imprime y las guarda."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/consultas/consultas_categorias.py [ruta/a/categorias_limpio.csv]")

    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_LIMPIO
    if not ruta_entrada.exists():
        sys.exit(f"Error: no se encontró el archivo {ruta_entrada}")

    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.max_columns", 20)

    df = leer_datos(ruta_entrada)
    carpeta = ruta_entrada.resolve().parent

    # (número, título, función, guardar con índice)
    consultas = [
        (1, "Veces que aparece cada categoría", consulta_1, True),
        (2, "Categorías sin descripción", consulta_2, False),
        (3, "Largo promedio de la descripción por categoría (groupby)", consulta_3, True),
        (4, "Categorías que maneja cada área (groupby)", consulta_4, True),
        (5, "Categorías por área, tabla cruzada (groupby doble)", consulta_5, True),
    ]

    rutas = []
    for numero, titulo, funcion, con_indice in consultas:
        mostrar_titulo(numero, titulo)
        resultado = funcion(df)
        print(resultado)
        rutas.extend(guardar(resultado, carpeta, numero, con_indice))

    print("\nArchivos guardados:")
    for ruta in rutas:
        print(f"  {ruta}")


if __name__ == "__main__":
    main()