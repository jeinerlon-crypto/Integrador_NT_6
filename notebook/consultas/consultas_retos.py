"""HU Q01 - Consultas sobre la tabla retos con pandas.

Uso:
    python scripts/consultas_retos.py retos_limpio.csv

Lee el CSV limpio, resuelve las cinco consultas (cada una en su propia
funcion), imprime el titulo y el resultado de cada una y guarda
retos_consulta_N.csv en la misma carpeta del archivo de entrada.
"""
import sys
from pathlib import Path

import pandas as pd

# Columnas que necesitan las consultas
COLUMNAS = ["id", "nombre", "estado", "duracion_dias", "fecha_inicio"]


def leer_retos(ruta):
    """Lee retos_limpio.csv, valida las columnas y ajusta los tipos de dato."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en el archivo: {', '.join(faltan)}")
    df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    return df


def mostrar_y_guardar(titulo, resultado, carpeta, numero):
    """Imprime el titulo y el resultado de una consulta y lo guarda en CSV."""
    print(f"\n=== Consulta {numero}: {titulo} ===")
    if resultado.empty:
        print("(sin resultados)")
    else:
        print(resultado.to_string(index=False))
    resultado.to_csv(carpeta / f"retos_consulta_{numero}.csv", index=False)


def consulta_1(df, carpeta):
    """Consulta 1: retos que estan en curso o en proceso."""
    en_curso = df[df["estado"].isin(["EN_CURSO", "EN_PROCESO"])]
    mostrar_y_guardar("¿Qué retos están en curso?", en_curso, carpeta, 1)
    return en_curso


def consulta_2(df, carpeta):
    """Consulta 2: los 10 retos mas largos segun duracion_dias."""
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    mostrar_y_guardar("¿Cuáles son los 10 retos más largos?", largos, carpeta, 2)
    return largos


def consulta_3(df, carpeta):
    """Consulta 3: cuantos retos hay por estado (value_counts)."""
    conteo = (
        df["estado"].value_counts()
        .rename_axis("estado")
        .reset_index(name="cantidad")
    )
    mostrar_y_guardar("¿Cuántos retos hay por estado?", conteo, carpeta, 3)
    return conteo


def consulta_4(df, carpeta):
    """Consulta 4 (groupby): cantidad, promedio, minimo y maximo de duracion por estado."""
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(2)
    resumen = resumen.reset_index()
    mostrar_y_guardar(
        "¿Cuál es la duración promedio, mínima y máxima por estado?",
        resumen, carpeta, 4,
    )
    return resumen


def consulta_5(df, carpeta):
    """Consulta 5 (groupby): cuantos retos empiezan cada mes segun fecha_inicio."""
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    por_mes = por_mes.rename("cantidad").reset_index()
    por_mes["fecha_inicio"] = por_mes["fecha_inicio"].astype(str)
    por_mes = por_mes.rename(columns={"fecha_inicio": "mes"})
    mostrar_y_guardar("¿Cuántos retos empiezan cada mes?", por_mes, carpeta, 5)
    return por_mes


def main():
    """Lee el archivo recibido por consola y ejecuta las cinco consultas en orden."""
    if len(sys.argv) != 2:
        print("Uso: python src/consultas/consultas_retos.py retos_limpio.csv")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"No se encontró el archivo: {ruta}")
        sys.exit(1)
    try:
        df = leer_retos(ruta)
    except ValueError as error:
        print(error)
        sys.exit(1)

    RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
    carpeta = RAIZ_PROYECTO / "datos" / "consultas"
    carpeta.mkdir(parents=True, exist_ok=True)
    
    print(f"Archivo leído: {ruta} ({len(df)} filas)")
    for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5):
        consulta(df, carpeta)

if __name__ == "__main__":
    main()