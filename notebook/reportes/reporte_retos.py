import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventanas: el script guarda los PNG y termina
import matplotlib.pyplot as plt
import pandas as pd

# Este archivo vive en src/notebook/reportes/, así que src/ está 2 niveles arriba
RUTA_SRC = Path(__file__).resolve().parents[2]
RUTA_POR_DEFECTO = RUTA_SRC / "datos" / "limpio" / "retos_limpio.csv"
CARPETA_REPORTES = RUTA_SRC / "reportes"

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre",
    11: "noviembre", 12: "diciembre",
}


def cargar_datos(ruta_csv):
    """Lee retos_limpio.csv, convierte las fechas y garantiza duracion_dias."""
    df = pd.read_csv(ruta_csv)

    # Las tres columnas que necesita el reporte deben existir
    faltantes = [c for c in ("estado", "fecha_inicio", "fecha_fin") if c not in df.columns]
    if faltantes:
        raise ValueError(f"Al archivo le faltan las columnas: {', '.join(faltantes)}")

    # Las fechas invalidas quedan como NaT en vez de romper el script
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")

    # Si el CSV ya trae duracion_dias se usa; si no, se calcula
    if "duracion_dias" in df.columns:
        df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")
    else:
        df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    return df


def contar_por_mes(df):
    """Cuenta cuantos retos empiezan cada mes, ordenado de forma cronologica."""
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M")).size()
    return por_mes.sort_index()


def grafica_1_estados(df, ruta):
    """Grafica 1 (barras): cantidad de retos por estado."""
    conteo = df["estado"].value_counts()

    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar", color="steelblue", edgecolor="black")
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado del reto")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_2_meses(df, ruta):
    """Grafica 2 (linea): retos que empiezan cada mes."""
    por_mes = contar_por_mes(df)
    por_mes.index = por_mes.index.astype(str)  # Etiquetas tipo 2025-03

    plt.figure(figsize=(8, 5))
    por_mes.plot(kind="line", marker="o", color="seagreen")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_3_duracion(df, ruta):
    """Grafica 3 (histograma): como se reparte la duracion de los retos."""
    plt.figure(figsize=(8, 5))
    df["duracion_dias"].plot(kind="hist", bins=20, color="darkorange", edgecolor="black")
    plt.title("Distribucion de la duracion de los retos")
    plt.xlabel("Duracion (dias)")
    plt.ylabel("Cantidad de retos")
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def conclusion_mes(df):
    """Imprime en que mes se concentran los retos y por que puede ser."""
    por_mes = contar_por_mes(df)
    print("1. En que mes se concentran los retos")
    if por_mes.empty:
        print("   No hay fechas de inicio validas para calcularlo.\n")
        return

    maximo = por_mes.max()
    top = [p for p, n in por_mes.items() if n == maximo]
    nombres = ", ".join(f"{MESES[p.month]} de {p.year}" for p in top)
    porcentaje = maximo / por_mes.sum() * 100
    print(f"   Se concentran en {nombres}: {maximo} retos "
          f"({porcentaje:.1f}% de los que tienen fecha de inicio).")
    print("   Puede ser porque los retos se lanzan al comienzo de un periodo "
          "(trimestre, semestre o una campana);")
    print("   los datos solos no lo confirman: hay que validarlo con la empresa.\n")


def conclusion_duracion(df):
    """Imprime cuanto dura en promedio un reto segun su estado."""
    print("2. Duracion promedio de un reto segun su estado")
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean"])
    if resumen.empty or resumen["count"].sum() == 0:
        print("   No hay duraciones validas para calcularlo.\n")
        return
    for estado, fila in resumen.iterrows():
        if fila["count"] == 0:
            print(f"   - {estado}: sin duraciones validas")
        else:
            print(f"   - {estado}: {fila['mean']:.1f} dias (sobre {int(fila['count'])} retos)")
    print()


def conclusion_fechas(df):
    """Imprime cuantos retos tienen la fecha de fin antes que la de inicio."""
    incoherentes = df[df["fecha_fin"] < df["fecha_inicio"]]
    print("3. Retos con fecha de fin antes que la de inicio (dato para el back)")
    print(f"   Hay {len(incoherentes)} retos con la fecha de fin anterior a la de inicio.")
    if len(incoherentes) > 0:
        if "id" in df.columns:
            ids = ", ".join(str(i) for i in incoherentes["id"].head(10))
            extra = " ..." if len(incoherentes) > 10 else ""
            print(f"   ids: {ids}{extra}")
        print("   El back deberia validar que fecha_fin >= fecha_inicio al guardar un reto.")
    sin_fecha = int(df["fecha_inicio"].isna().sum() + df["fecha_fin"].isna().sum())
    if sin_fecha > 0:
        print(f"   Ademas hay {sin_fecha} fechas vacias o invalidas.")


def imprimir_conclusiones(df):
    """Imprime las tres conclusiones del reporte."""
    print("\n=== CONCLUSIONES ===")
    conclusion_mes(df)
    conclusion_duracion(df)
    conclusion_fechas(df)


def generar_reporte(ruta_csv=RUTA_POR_DEFECTO, carpeta_salida=CARPETA_REPORTES):
    """Lee el CSV limpio, crea las tres graficas en la carpeta de salida e imprime las conclusiones."""
    ruta_csv = Path(ruta_csv)
    carpeta_salida = Path(carpeta_salida)

    if not ruta_csv.exists():
        raise FileNotFoundError(f"No existe el archivo '{ruta_csv}'.")

    df = cargar_datos(ruta_csv)

    # La carpeta se crea sola
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    print("=== GRAFICAS ===")
    graficas = [
        (grafica_1_estados, "retos_grafica_1.png"),
        (grafica_2_meses, "retos_grafica_2.png"),
        (grafica_3_duracion, "retos_grafica_3.png"),
    ]
    rutas_creadas = []
    for funcion, nombre in graficas:
        ruta = carpeta_salida / nombre
        funcion(df, ruta)
        print(f"Guardada: {ruta}")
        rutas_creadas.append(ruta)

    imprimir_conclusiones(df)
    return rutas_creadas


if __name__ == "__main__":
    # Permite ejecutarlo solo: python reporte_retos.py [ruta_al_csv]
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    try:
        generar_reporte(ruta)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)