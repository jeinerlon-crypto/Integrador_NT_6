"""HU G01 - Reporte gráfico de la tabla empresas.

Uso: python scripts/reporte_empresas.py empresas_limpio.csv
"""
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

CARPETA = "reportes"
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def cargar_datos(ruta):
    """Lee el CSV limpio y normaliza la columna 'activa' a texto Activa/Inactiva."""
    df = pd.read_csv(ruta)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ("sector", "activa"):
        if col not in df.columns:
            sys.exit(f"Error: el archivo no tiene la columna '{col}'. "
                     f"Columnas encontradas: {list(df.columns)}")
    verdaderos = {"true", "1", "si", "sí", "activa", "activo", "s", "y", "yes"}
    es_activa = df["activa"].astype(str).str.strip().str.lower().isin(verdaderos)
    df["activa"] = es_activa.map({True: "Activa", False: "Inactiva"})
    return df


def grafica_1(df):
    """Barras: cantidad de empresas por sector. Devuelve la ruta guardada."""
    por_sector = df["sector"].value_counts()
    plt.figure(figsize=(9, 6))
    por_sector.plot(kind="bar")
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "empresas_grafica_1.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_2(df):
    """Torta: empresas activas vs inactivas. Devuelve la ruta guardada."""
    plt.figure(figsize=(6, 6))
    df["activa"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Proporción de empresas")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "empresas_grafica_2.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_3(df):
    """Barras apiladas: activas e inactivas por sector. Devuelve la ruta."""
    tabla = pd.crosstab(df["sector"], df["activa"])
    plt.figure(figsize=(9, 6))
    tabla.plot(kind="bar", stacked=True, ax=plt.gca())
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "empresas_grafica_3.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def contar_correos_invalidos(df):
    """Cuenta correos vacíos o con formato inválido. Devuelve None si no hay columna de correo."""
    col = next((c for c in df.columns if "correo" in c or "email" in c or "mail" in c), None)
    if col is None:
        return None
    correos = df[col].fillna("").astype(str).str.strip()
    invalidos = [c for c in correos if not PATRON_CORREO.match(c)]
    return len(invalidos)


def conclusiones(df):
    """Arma la lista de conclusiones a partir de los datos."""
    total = len(df)
    por_sector = df["sector"].value_counts()
    top, cant_top = por_sector.index[0], int(por_sector.iloc[0])
    inactivas = int((df["activa"] == "Inactiva").sum())
    pct_inactivas = inactivas / total * 100 if total else 0
    invalidos = contar_correos_invalidos(df)

    lineas = [
        f"1. El sector con más empresas registradas es '{top}' con {cant_top} "
        f"de {total} ({cant_top / total * 100:.1f}%).",
        f"2. El {pct_inactivas:.1f}% de las empresas está inactivo ({inactivas} de {total}). "
        "Significa que una parte de la base no genera actividad en la plataforma: "
        "hay que entender por qué se retiran y no contarlas como clientes vigentes.",
    ]
    if invalidos is None:
        lineas.append("3. No se encontró una columna de correo en el archivo, "
                      "así que no se pudieron contar correos inválidos.")
    else:
        lineas.append(
            f"3. Aparecieron {invalidos} correos inválidos. Hay que validarlos en el back "
            "porque el front se puede saltar (o manipular) y el back es la única barrera "
            "que garantiza que los datos guardados sean confiables."
        )
    return lineas


def main():
    """Punto de entrada: genera las gráficas e imprime rutas y conclusiones."""
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/reporte_empresas.py empresas_limpio.csv")
    df = cargar_datos(sys.argv[1])
    os.makedirs(CARPETA, exist_ok=True)
    print("Gráficas generadas:")
    for funcion in (grafica_1, grafica_2, grafica_3):
        print(" -", funcion(df))
    print("\nConclusiones:")
    for linea in conclusiones(df):
        print(linea)


if __name__ == "__main__":
    main()
