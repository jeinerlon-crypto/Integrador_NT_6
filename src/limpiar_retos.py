"""Limpia la tabla retos (HU L01) con pandas.

Estructura del proyecto (este archivo vive en src/):
    proyecto/
    |-- src/limpiar_retos.py
    |-- data/crudo/retos_sucio.csv
    `-- data/limpio/retos_limpio.csv

Uso (desde la raiz del proyecto o desde cualquier otra carpeta):
    python src/limpiar_retos.py [ruta_entrada] [ruta_salida]

Sin argumentos lee data/crudo/retos_sucio.csv y guarda en
data/limpio/retos_limpio.csv, dentro de la carpeta del proyecto, sin
importar desde donde se ejecute.
"""
import os
import sys
from pathlib import Path

import pandas as pd

# Columnas que no pueden quedar con nulos despues de limpiar.
# fecha_fin no es obligatoria: un reto puede no tener fecha de cierre todavia.
COLUMNAS_OBLIGATORIAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]
COLUMNAS_ESPERADAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]
# Raiz del proyecto: la carpeta que contiene a src/ (este archivo esta en src/).
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_ENTRADA_POR_DEFECTO = str(RAIZ_PROYECTO / "data" / "crudo" / "retos_sucio.csv")
RUTA_SALIDA_POR_DEFECTO = str(RAIZ_PROYECTO / "data" / "limpio" / "retos_limpio.csv")


def leer_datos(ruta):
    """Lee el CSV sucio con pd.read_csv y devuelve el DataFrame.

    Detecta el separador (coma o punto y coma, como los guarda Excel) mirando
    el encabezado, y usa utf-8-sig para ignorar el BOM al inicio del archivo."""
    with open(ruta, encoding="utf-8-sig") as archivo:
        encabezado = archivo.readline()
    separador = ";" if encabezado.count(";") > encabezado.count(",") else ","
    df = pd.read_csv(ruta, sep=separador, encoding="utf-8-sig")
    faltan = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
    if faltan:
        print(f"Error: faltan las columnas {faltan}. Encontradas: {list(df.columns)}")
        sys.exit(1)
    return df


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Quita los duplicados exactos y devuelve el DataFrame sin ellos."""
    return df.drop_duplicates()


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime aunque vengan en dos
    formatos (2026-03-02 y 02/03/2026). Lo que no se pueda leer queda NaT.

    Ojo: con dayfirst=True pandas invierte dia y mes en las fechas ISO
    (2026-03-02 -> 3 de febrero). Por eso se leen primero las ISO tal cual y
    el resto (dd/mm/aaaa) con format="mixed" y dayfirst=True."""
    for columna in ["fecha_inicio", "fecha_fin"]:
        serie = df[columna]
        iso = pd.to_datetime(serie, format="%Y-%m-%d", errors="coerce")
        resto = pd.to_datetime(
            serie[iso.isna()], format="mixed", dayfirst=True, errors="coerce"
        )
        df[columna] = iso.fillna(resto)
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios en los bordes, en mayusculas y con
    guion bajo en lugar de espacios (' en curso ' -> 'EN_CURSO')."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def limpiar_nombre(df):
    """Quita los espacios sobrantes del nombre (ensuciado en la HU F01)."""
    df["nombre"] = df["nombre"].str.strip()
    return df


def rellenar_descripciones(df):
    """Rellena las descripciones vacias con 'Sin descripcion'."""
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def crear_duracion(df):
    """Crea duracion_dias = fecha_fin - fecha_inicio, en dias."""
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    return df


def marcar_fechas_incoherentes(df):
    """Crea fecha_valida (True si duracion_dias >= 0) y reporta cuantas filas
    tienen el fin antes que el inicio y cuantas no tienen fecha_fin."""
    df["fecha_valida"] = df["duracion_dias"] >= 0
    incoherentes = int((df["duracion_dias"] < 0).sum())
    sin_fin = int(df["fecha_fin"].isna().sum())
    print(f"\nFechas incoherentes (fin antes que inicio): {incoherentes}")
    print(f"Filas sin fecha_fin (fecha_valida = False): {sin_fin}")
    print(f"Filas con fecha_valida = True: {int(df['fecha_valida'].sum())}")
    return df


def quitar_nulos_obligatorios(df):
    """Elimina las filas con nulos en columnas obligatorias (por ejemplo una
    fecha_inicio que no se pudo leer) para cumplir el criterio final."""
    return df.dropna(subset=COLUMNAS_OBLIGATORIAS)


def guardar_resultado(df, ruta):
    """Crea la carpeta de salida si hace falta y guarda el CSV limpio."""
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")


def limpiar(ruta_entrada=RUTA_ENTRADA_POR_DEFECTO, ruta_salida=RUTA_SALIDA_POR_DEFECTO):
    """Ejecuta todo el flujo: diagnostico, limpieza, diagnostico y guardado.

    Devuelve el DataFrame limpio para poder usarlo desde main.py."""
    if not os.path.isfile(ruta_entrada):
        print(f"Error: no existe el archivo {ruta_entrada}")
        sys.exit(1)

    df = leer_datos(ruta_entrada)
    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")
    filas_antes = len(df)

    df = quitar_duplicados(df)
    # Nulos de referencia: despues de quitar duplicados, para que la
    # comparacion mida solo los nulos realmente corregidos.
    nulos_antes = df.isna().sum()
    df = limpiar_nombre(df)
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripciones(df)
    df = crear_duracion(df)
    df = marcar_fechas_incoherentes(df)
    df = quitar_nulos_obligatorios(df)
    df = quitar_duplicados(df)  # por si limpiar espacios creo duplicados nuevos

    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

    # Comparacion de nulos antes y despues (columnas nuevas no cuentan).
    nulos_despues = df.isna().sum().reindex(nulos_antes.index)
    comparacion = pd.DataFrame(
        {"antes": nulos_antes, "despues": nulos_despues,
         "corregidos": nulos_antes - nulos_despues}
    )
    print("\nNulos antes vs despues (sin contar filas duplicadas):")
    print(comparacion)
    print("Total de nulos corregidos:", int(comparacion["corregidos"].sum()))
    print(f"\nFilas antes: {filas_antes} | despues: {len(df)} | "
          f"eliminadas: {filas_antes - len(df)}")

    guardar_resultado(df, ruta_salida)
    print(f"Archivo limpio guardado en: {ruta_salida}")
    return df


def main():
    """Lee los argumentos de la terminal (opcionales) y llama a limpiar()."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA_POR_DEFECTO
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else RUTA_SALIDA_POR_DEFECTO
    limpiar(ruta_entrada, ruta_salida)


if __name__ == "__main__":
    main()