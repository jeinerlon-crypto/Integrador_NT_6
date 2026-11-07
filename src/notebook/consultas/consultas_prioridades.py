"""Responde las cinco consultas de la HU Q01 sobre la tabla prioridades.

Uso:
    python notebook/consultas/consultas_prioridades.py
    python notebook/consultas/consultas_prioridades.py ruta/a/prioridades_limpio.csv

Sin argumentos lee datos/limpios/prioridades_limpio.csv desde la raíz del
proyecto. Imprime el título y el resultado de cada consulta, en orden, y
guarda cada resultado como prioridades_consulta_N.csv, .xlsx y .json en la
misma carpeta del archivo de entrada.
"""

import sys
from pathlib import Path

import pandas as pd

COLUMNAS_NECESARIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_LIMPIO = CARPETA_PROYECTO / "datos" / "limpios" / "prioridades_limpio.csv"


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
    """Guarda el resultado como prioridades_consulta_N en CSV, Excel y JSON."""
    tabla = resultado.reset_index() if con_indice else resultado
    tabla.columns.name = None
    base = carpeta / f"prioridades_consulta_{numero}"
    rutas = [base.with_suffix(".csv"), base.with_suffix(".xlsx"), base.with_suffix(".json")]
    tabla.to_csv(rutas[0], index=False, encoding="utf-8")
    tabla.to_excel(rutas[1], index=False, sheet_name=f"consulta_{numero}")
    tabla.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    return rutas


def consulta_1(df):
    """Ordena las prioridades de la más urgente (nivel 1) a la menos urgente."""
    print("Pregunta: ¿Cuáles son las prioridades, de la más urgente a la menos urgente?")
    ordenadas = df.sort_values("nivel")
    return ordenadas


def consulta_2(df):
    """Filtra solo las prioridades urgentes: nivel 1 y 2."""
    print("Pregunta: ¿Qué prioridades son urgentes (nivel 1 y 2)?")
    urgentes = df[df["nivel"] <= 2]
    return urgentes


def consulta_3(df):
    """Cuenta cuántas veces aparece cada nombre (detecta variantes)."""
    print("Pregunta: ¿Cuántas veces aparece cada nombre?")
    conteo = df["nombre"].value_counts()
    return conteo


def consulta_4(df):
    """GROUPBY: cuenta cuántas filas hay de cada nivel."""
    print("Pregunta: ¿Cuántas filas hay por nivel?")
    por_nivel = df.groupby("nivel")["id"].count()
    return por_nivel


def consulta_5(df):
    """GROUPBY: días de respuesta mínimo, promedio y máximo por prioridad."""
    print("Pregunta: ¿Cuál es el mínimo, el promedio y el máximo de días de respuesta por prioridad?")
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    return resumen


def main():
    """Ejecuta las cinco consultas en orden, las imprime y las guarda."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/consultas/consultas_prioridades.py [ruta/a/prioridades_limpio.csv]")

    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_LIMPIO
    if not ruta_entrada.exists():
        sys.exit(f"Error: no se encontró el archivo {ruta_entrada}")

    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.max_columns", 20)

    df = leer_datos(ruta_entrada)
    carpeta = ruta_entrada.resolve().parent

    # (número, título, función, guardar con índice)
    consultas = [
        (1, "Prioridades de la más urgente a la menos urgente", consulta_1, False),
        (2, "Prioridades urgentes (nivel 1 y 2)", consulta_2, False),
        (3, "Veces que aparece cada nombre", consulta_3, True),
        (4, "Filas por nivel (groupby)", consulta_4, True),
        (5, "Días de respuesta mínimo, promedio y máximo por prioridad (groupby)", consulta_5, True),
    ]

    rutas = []
    for numero, titulo, funcion, con_indice in consultas:
        mostrar_titulo(numero, titulo)
        resultado = funcion(df)
        print(resultado)
        if isinstance(resultado, pd.DataFrame) and not con_indice:
            print(f"Total: {len(resultado)} filas (los archivos las traen todas)")
        rutas.extend(guardar(resultado, carpeta, numero, con_indice))

    print("\nArchivos guardados:")
    for ruta in rutas:
        print(f"  {ruta}")


if __name__ == "__main__":
    main()