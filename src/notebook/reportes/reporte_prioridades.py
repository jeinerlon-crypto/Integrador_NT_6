"""Crea las tres gráficas de la HU G01 de la tabla prioridades y sus conclusiones.

Uso:
    python notebook/reportes/reporte_prioridades.py
    python notebook/reportes/reporte_prioridades.py ruta/a/prioridades_limpio.csv

Sin argumentos lee datos/limpios/prioridades_limpio.csv desde la raíz del
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
RUTA_LIMPIO = CARPETA_PROYECTO / "datos" / "limpios" / "prioridades_limpio.csv"
PRIORIDADES_ESPERADAS = 5
NIVEL_MINIMO, NIVEL_MAXIMO = 1, 5
COLUMNAS_NECESARIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]


def leer_datos(ruta):
    """Lee el CSV limpio con pandas y revisa que tenga las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltantes = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: al archivo le faltan las columnas {faltantes}")
    return df


def guardar_grafica(numero):
    """Ajusta la figura, la guarda con dpi=120, la cierra y devuelve su ruta."""
    ruta = CARPETA_REPORTES / f"prioridades_grafica_{numero}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df):
    """Barras: cuántas filas hay por nivel."""
    por_nivel = df.groupby("nivel")["id"].count()
    plt.figure(figsize=(7, 5))
    por_nivel.plot(kind="bar")
    plt.title("Cantidad de filas por nivel de prioridad")
    plt.xlabel("Nivel (1 = más urgente)")
    plt.ylabel("Cantidad de filas")
    plt.xticks(rotation=0)
    return guardar_grafica(1)


def grafica_2(df):
    """Barras: días promedio de respuesta por prioridad, de la más urgente a la menos."""
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    orden = df.groupby("nombre")["nivel"].min().sort_values().index  # Orden por nivel.
    resumen = resumen.loc[orden]
    plt.figure(figsize=(8, 5))
    resumen["mean"].plot(kind="bar")
    plt.title("Días promedio de respuesta por prioridad")
    plt.xlabel("Prioridad (de la más urgente a la menos urgente)")
    plt.ylabel("Días promedio de respuesta")
    plt.xticks(rotation=0)
    return guardar_grafica(2)


def grafica_3(df):
    """Torta: reparto de las filas entre las prioridades."""
    conteo = df["nombre"].value_counts()
    plt.figure(figsize=(8, 7))
    conteo.plot(kind="pie", autopct="%1.1f%%", radius=0.9)
    plt.title("Reparto de las prioridades")
    plt.xlabel("Porcentaje de filas por prioridad")
    plt.ylabel("Prioridad", labelpad=20)
    return guardar_grafica(3)


def imprimir_conclusiones(df):
    """Imprime las conclusiones que pide la HU G01, calculadas con los datos."""
    reales = df["nombre"].nunique()
    estado = "correcto" if reales == PRIORIDADES_ESPERADAS else f"REVISAR: deberían ser {PRIORIDADES_ESPERADAS}"
    tabla = (
        df.groupby("nivel")
        .agg(prioridad=("nombre", "first"), dias=("dias_max_respuesta", "mean"))
        .sort_index()
    )
    crece = tabla["dias"].is_monotonic_increasing
    correlacion = df["nivel"].corr(df["dias_max_respuesta"])
    plazo_unico = df.groupby("nivel")["dias_max_respuesta"].nunique().max() == 1
    fuera = int((~df["nivel"].between(NIVEL_MINIMO, NIVEL_MAXIMO)).sum())

    print("\n===== CONCLUSIONES =====")
    print(f"1. Prioridades reales al final: {reales} ({estado}).")
    print(f"   {', '.join(tabla['prioridad'])}.")

    print("2. Relación entre el nivel y los días máximos de respuesta:")
    for nivel, fila in tabla.iterrows():
        unidad = "día" if fila["dias"] == 1 else "días"
        print(f"   Nivel {nivel} ({fila['prioridad']}): {fila['dias']:g} {unidad}")
    if crece:
        print("   A mayor nivel (menos urgente), más días de plazo: la relación es directa")
    else:
        print("   OJO: los días no crecen siempre con el nivel; revisa DIAS en la simulación")
    print(f"   (correlación = {correlacion:.2f}).")
    if plazo_unico:
        print("   Cada nivel tiene un solo plazo, así que el nivel define los días:")
        print("   la prioridad más urgente se responde en el menor tiempo.")
    else:
        print("   Algunos niveles tienen plazos distintos; revisa la limpieza de los días.")

    print(f"3. Por qué el back debe validar que `nivel` esté entre {NIVEL_MINIMO} y {NIVEL_MAXIMO}:")
    print(f"   En estos datos hay {fuera} filas fuera de rango porque ya se limpiaron, pero en")
    print("   los sucios llegaron niveles como texto ('3'), como palabra ('tres') y vacíos.")
    print("   Si el back acepta un 0, un 7 o un texto, ese registro no tiene plazo de")
    print("   respuesta definido, se ordena mal entre las urgentes y daña consultas y")
    print("   gráficas. Validar el rango al guardar evita tener que limpiarlo después.")


def main():
    """Lee los datos, crea las tres gráficas e imprime sus rutas y las conclusiones."""
    if len(sys.argv) > 2:
        sys.exit("Uso: python notebook/reportes/reporte_prioridades.py [ruta/a/prioridades_limpio.csv]")

    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_LIMPIO
    if not ruta_entrada.exists():
        sys.exit(f"Error: no se encontró el archivo {ruta_entrada}")

    df = leer_datos(ruta_entrada)
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    print("Gráficas guardadas:")
    for funcion in (grafica_1, grafica_2, grafica_3):
        print(f"  {funcion(df)}")

    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()