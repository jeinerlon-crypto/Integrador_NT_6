"""Reporte de graficas de la tabla registros (HU G01).

Uso:
    python src/reporte_registros.py [ruta_csv]

Si no se indica ruta, lee data/limpio/registros_limpio.csv. Crea tres
graficas en la carpeta reportes/ e imprime la ruta de cada una junto con
las conclusiones.
"""

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Backend sin ventana: el script no se queda esperando.
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_SALIDA = str(RAIZ / "reportes")
RUTA_POR_DEFECTO = RAIZ / "data" / "limpio" / "registros_limpio.csv"
DPI = 120


def cargar_datos(ruta_csv):
    """Lee el CSV limpio y devuelve un DataFrame con la fecha convertida."""
    df = pd.read_csv(ruta_csv)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    return df


def guardar_grafica(ruta, eje_conteo="y"):
    """Fuerza enteros en el eje de conteos, ajusta el diseno, guarda con dpi=120 y cierra."""
    eje = plt.gca().yaxis if eje_conteo == "y" else plt.gca().xaxis
    eje.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(ruta, dpi=DPI)
    plt.close()


def grafica_estados(df):
    """Grafica 1: barras con las participaciones por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de participaciones")
    plt.xticks(rotation=0)
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_1.png")
    guardar_grafica(ruta)
    return ruta


def grafica_meses(df):
    """Grafica 2: linea con las participaciones por mes."""
    por_mes = df["mes"].value_counts().sort_index()
    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Cantidad de participaciones")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_2.png")
    guardar_grafica(ruta)
    return ruta


def calcular_top_retos(df):
    """Devuelve los 10 retos con mas participantes (usuarios distintos)."""
    participantes = df.groupby("id_reto")["id_usuario"].nunique()
    return participantes.sort_values(ascending=False).head(10)


def grafica_retos(df):
    """Grafica 3: barras horizontales con los 10 retos con mas participantes."""
    top_retos = calcular_top_retos(df)
    # Se invierte el orden para que el reto mas popular quede arriba.
    top_retos = top_retos.sort_values(ascending=True)
    # Se acorta el id para que quepa en el eje.
    top_retos.index = [i[:8] for i in top_retos.index]
    plt.figure(figsize=(8, 5))
    top_retos.plot(kind="barh")
    plt.title("Los 10 retos con mas participantes")
    plt.xlabel("Participantes (usuarios distintos)")
    plt.ylabel("Reto (primeros 8 caracteres del id)")
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_3.png")
    guardar_grafica(ruta, eje_conteo="x")
    return ruta


def contar_duplicados(df):
    """Cuenta las inscripciones repetidas (mismo usuario en el mismo reto)."""
    return int(df.duplicated(subset=["id_usuario", "id_reto"]).sum())


def construir_conclusiones(df):
    """Arma la lista de conclusiones a partir de los datos (maneja empates)."""
    top_retos = calcular_top_retos(df)
    max_part = int(top_retos.iloc[0])
    retos_top = list(top_retos[top_retos == max_part].index)

    por_mes = df["mes"].value_counts().sort_index()
    max_mes = int(por_mes.max())
    meses_top = list(por_mes[por_mes == max_mes].index)

    duplicados = contar_duplicados(df)

    if len(retos_top) == 1:
        c1 = (f"1. El reto mas popular es {retos_top[0]} con {max_part} "
              f"participantes.")
    else:
        c1 = (f"1. Hay {len(retos_top)} retos empatados como los mas populares, "
              f"cada uno con {max_part} participantes: {', '.join(retos_top)}.")

    if len(meses_top) == 1:
        c2 = (f"2. El mes con mas inscripciones fue {meses_top[0]} con "
              f"{max_mes} participaciones.")
    else:
        c2 = (f"2. Los meses con mas inscripciones fueron {', '.join(meses_top)} "
              f"(empate, {max_mes} participaciones cada uno).")

    c3 = (f"3. Se encontraron {duplicados} inscripciones duplicadas "
          f"(mismo usuario en el mismo reto). El back debe bloquearlas con "
          f"409 (Conflict) porque el recurso ya existe: asi se evita contar "
          f"dos veces al mismo participante y se mantienen correctas las "
          f"estadisticas.")
    return [c1, c2, c3]


def main():
    """Punto de entrada: genera las graficas e imprime el resumen."""
    if len(sys.argv) > 2:
        print("Uso: python src/reporte_registros.py [ruta_csv]")
        sys.exit(1)

    ruta_csv = sys.argv[1] if len(sys.argv) == 2 else RUTA_POR_DEFECTO
    df = cargar_datos(ruta_csv)
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    rutas = [grafica_estados(df), grafica_meses(df), grafica_retos(df)]

    print("Graficas generadas:")
    for ruta in rutas:
        print(f"  {ruta}")

    print("\nConclusiones:")
    for linea in construir_conclusiones(df):
        print(linea)


if __name__ == "__main__":
    main()