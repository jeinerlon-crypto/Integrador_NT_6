"""Consultas de la HU Q01 sobre la tabla registros (proyecto integrador).

Uso (desde la raiz del proyecto):
    python src/consultas_registros.py
    python src/consultas_registros.py data/limpio/registros_limpio.csv

Si no se pasa ninguna ruta, lee data/limpio/registros_limpio.csv (el archivo
LIMPIO). Responde cinco consultas con pandas, imprime el titulo y el
resultado de cada una y guarda registros_consulta_N.csv en la misma carpeta
del archivo de entrada.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# Si no se pasa ninguna ruta, se usa el CSV limpio del proyecto
# (src/ esta un nivel dentro de la raiz, por eso se sube con .parent.parent).
RUTA_POR_DEFECTO = (
    Path(__file__).resolve().parent.parent / "data" / "limpio" / "registros_limpio.csv"
)


def cargar_datos(ruta):
    """Lee el CSV limpio y devuelve un DataFrame (todo como texto)."""
    return pd.read_csv(ruta, dtype=str)


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de la consulta N como registros_consulta_N.csv."""
    destino = os.path.join(carpeta, f"registros_consulta_{numero}.csv")
    resultado.to_csv(destino, index=False, encoding="utf-8")


def consulta_1(df, carpeta):
    """Consulta 1: participaciones ya finalizadas (estado == FINALIZADO)."""
    print("Consulta 1 - ¿Qué participaciones ya están finalizadas?")
    finalizados = df[df["estado"] == "FINALIZADO"]
    print(finalizados.to_string(index=False))
    print(f"Total: {len(finalizados)}\n")
    guardar(finalizados, carpeta, 1)
    return finalizados


def consulta_2(df, carpeta):
    """Consulta 2: participaciones repetidas (mismo usuario en el mismo reto)."""
    print("Consulta 2 - ¿Qué participaciones están repetidas (mismo usuario en el mismo reto)?")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    repetidos = repetidos.sort_values(["id_usuario", "id_reto"])
    if repetidos.empty:
        print("No hay participaciones repetidas.")
    else:
        print(repetidos.to_string(index=False))
    print(f"Total: {len(repetidos)}\n")
    guardar(repetidos, carpeta, 2)
    return repetidos


def consulta_3(df, carpeta):
    """Consulta 3: cuántas participaciones hay por estado."""
    print("Consulta 3 - ¿Cuántas participaciones hay por estado?")
    conteo = df["estado"].value_counts()
    # Se convierte a tabla de dos columnas para guardarla como CSV.
    conteo = conteo.rename_axis("estado").reset_index(name="participaciones")
    print(conteo.to_string(index=False))
    print()
    guardar(conteo, carpeta, 3)
    return conteo


def consulta_4(df, carpeta):
    """Consulta 4 (groupby): los 10 retos con más participantes."""
    print("Consulta 4 - ¿Cuáles son los 10 retos con más participantes?")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    top_retos = top_retos.rename("participaciones").reset_index()
    print(top_retos.to_string(index=False))
    print()
    guardar(top_retos, carpeta, 4)
    return top_retos


def consulta_5(df, carpeta):
    """Consulta 5 (groupby): cuántas participaciones hubo cada mes."""
    print("Consulta 5 - ¿Cuántas participaciones hubo cada mes?")
    por_mes = df.groupby("mes")["id"].count()
    por_mes = por_mes.rename("participaciones").reset_index()
    print(por_mes.to_string(index=False))
    print()
    guardar(por_mes, carpeta, 5)
    return por_mes


def main():
    """Lee el CSV limpio (por consola o el de por defecto) y ejecuta las cinco consultas en orden."""
    if len(sys.argv) > 2:
        print("Uso: python src/consultas_registros.py [ruta/a/registros_limpio.csv]")
        sys.exit(1)

    ruta = sys.argv[1] if len(sys.argv) == 2 else str(RUTA_POR_DEFECTO)
    if not os.path.isfile(ruta):
        print(f"No se encontró el archivo: {ruta}")
        sys.exit(1)

    carpeta = os.path.dirname(os.path.abspath(ruta))
    df = cargar_datos(ruta)

    consulta_1(df, carpeta)
    consulta_2(df, carpeta)
    consulta_3(df, carpeta)
    consulta_4(df, carpeta)
    consulta_5(df, carpeta)


if __name__ == "__main__":
    main()