#!/usr/bin/env python3
"""Revisa la tabla empresas (HU F01 simulación y HU X01 exportación).

Uso:
    python scripts/revisar_datos.py empresas_sucio.csv
    python scripts/revisar_datos.py empresas_sucio.xlsx
    python scripts/revisar_datos.py empresas_sucio.json

Cuenta las filas, revisa que estén las columnas que pide la HU y cuenta los
nulos y los duplicados de cada columna. Imprime tablas en Markdown con las
columnas: Comprobación | Esperado | Encontrado | Estado (PASA o FALLA).

Solo usa la librería estándar. pandas (con openpyxl) se importa únicamente
si el archivo es .xlsx.
"""

import csv
import json
import math
import os
import re
import sys

# --- Criterios tomados de references/criterios.md --------------------------
COLUMNAS_ESPERADAS = ["id", "nombre", "nit", "sector", "contacto",
                      "correo", "telefono", "activa"]
FILAS_BASE = 300            # "Se generan 300 filas"
FILAS_MAX = 315             # 300 + 5 % de duplicados exactos
DUP_FILAS = (0.03, 0.07)    # alrededor del 5 % de filas repetidas tal cual
NIT_REPETIDO = (0.01, 0.05)  # alrededor del 3 % de NIT repetidos
NULOS_CONTACTO = (0.04, 0.12)  # alrededor del 8 % de contacto en None


def es_nulo(valor):
    """Devuelve True si el valor es None, NaN o un texto vacío o solo espacios."""
    if valor is None:
        return True
    if isinstance(valor, float) and math.isnan(valor):
        return True
    return isinstance(valor, str) and valor.strip() == ""


def leer_csv(ruta):
    """Lee un CSV con la librería estándar y devuelve (columnas, filas)."""
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        filas = list(lector)
        return list(lector.fieldnames or []), filas


def leer_json(ruta):
    """Lee un JSON orientado a registros y devuelve (columnas, filas)."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    if not isinstance(datos, list) or not all(isinstance(d, dict) for d in datos):
        raise ValueError("El JSON debe ser una lista de objetos (orient='records').")
    columnas = []
    for registro in datos:
        for clave in registro:
            if clave not in columnas:
                columnas.append(clave)
    return columnas, datos


def leer_excel(ruta):
    """Lee un .xlsx con pandas (la hoja 'empresas' o, si no está, la primera)."""
    try:
        import pandas as pd
    except ImportError:
        sys.exit("Para leer .xlsx hace falta instalar pandas y openpyxl: "
                 "pip install pandas openpyxl")
    hojas = pd.ExcelFile(ruta).sheet_names
    hoja = "empresas" if "empresas" in hojas else hojas[0]
    # dtype=str y sin NA por defecto: no se altera ningún valor del archivo.
    df = pd.read_excel(ruta, sheet_name=hoja, dtype=str,
                       keep_default_na=False, na_values=[""])
    return list(df.columns), df.to_dict("records")


def leer_archivo(ruta):
    """Elige el lector según la extensión del archivo (.csv, .xlsx o .json)."""
    extension = os.path.splitext(ruta)[1].lower()
    if extension == ".csv":
        return leer_csv(ruta)
    if extension in (".xlsx", ".xls"):
        return leer_excel(ruta)
    if extension == ".json":
        return leer_json(ruta)
    sys.exit(f"Formato no soportado: '{extension}'. Usa .csv, .xlsx o .json.")


def contar_nulos(filas, columna):
    """Cuenta cuántas filas tienen nulo en la columna dada."""
    return sum(1 for fila in filas if es_nulo(fila.get(columna)))


def contar_duplicados_columna(filas, columna):
    """Cuenta los valores no nulos de la columna que ya habían aparecido antes."""
    vistos, repetidos = set(), 0
    for fila in filas:
        valor = fila.get(columna)
        if es_nulo(valor):
            continue
        clave = str(valor)
        if clave in vistos:
            repetidos += 1
        vistos.add(clave)
    return repetidos


def clave_fila(fila, columnas):
    """Convierte una fila en una tupla comparable (los nulos quedan como None)."""
    return tuple(None if es_nulo(fila.get(c)) else str(fila.get(c)) for c in columnas)


def contar_filas_duplicadas(filas, columnas):
    """Cuenta las filas idénticas a otra anterior (duplicados exactos)."""
    vistas, repetidas = set(), 0
    for fila in filas:
        clave = clave_fila(fila, columnas)
        if clave in vistas:
            repetidas += 1
        vistas.add(clave)
    return repetidas


def contar_nit_repetidos(filas, columnas):
    """Cuenta NIT repetidos entre empresas distintas (ignora filas idénticas).

    Se comparan solo los dígitos para que '900.123.456-7' y '9001234567'
    cuenten como el mismo NIT.
    """
    unicas, vistos, repetidos = set(), set(), 0
    for fila in filas:
        clave = clave_fila(fila, columnas)
        if clave in unicas:
            continue  # duplicado exacto: no es "otra empresa"
        unicas.add(clave)
        nit = fila.get("nit")
        if es_nulo(nit):
            continue
        digitos = re.sub(r"\D", "", str(nit))
        if not digitos:
            continue
        if digitos in vistos:
            repetidos += 1
        vistos.add(digitos)
    return repetidos


def porcentaje(parte, total):
    """Devuelve parte/total como fracción (0 si el total es 0)."""
    return parte / total if total else 0.0


def formato_cantidad(cantidad, total):
    """Da formato '15 (5.0 %)' para mostrar una cantidad con su porcentaje."""
    return f"{cantidad} ({porcentaje(cantidad, total) * 100:.1f} %)"


def estado(condicion):
    """Traduce un booleano a 'PASA' o 'FALLA'."""
    return "PASA" if condicion else "FALLA"


def construir_comprobaciones(columnas, filas):
    """Arma la lista de comprobaciones [(nombre, esperado, encontrado, estado)]."""
    total = len(filas)
    resultado = []

    # 1. Número de filas
    resultado.append(("Filas", f"{FILAS_BASE} a {FILAS_MAX} (300 + duplicados)",
                      str(total), estado(FILAS_BASE <= total <= FILAS_MAX)))

    # 2. Columnas que pide la HU
    faltan = [c for c in COLUMNAS_ESPERADAS if c not in columnas]
    sobran = [c for c in columnas if c not in COLUMNAS_ESPERADAS]
    detalle = "las 8 columnas" if not faltan and not sobran else ""
    if faltan:
        detalle += "faltan: " + ", ".join(faltan)
    if sobran:
        detalle += ("; " if faltan else "") + "sobran: " + ", ".join(sobran)
    resultado.append(("Columnas", ", ".join(COLUMNAS_ESPERADAS), detalle,
                      estado(not faltan and not sobran)))

    # 3. Nulos por columna (solo 'contacto' debe tener, alrededor del 8 %)
    for col in COLUMNAS_ESPERADAS:
        if col not in columnas:
            resultado.append((f"Nulos en {col}", "columna presente",
                              "columna ausente", "FALLA"))
            continue
        nulos = contar_nulos(filas, col)
        if col == "contacto":
            bajo, alto = NULOS_CONTACTO
            esperado = "≈8 % (entre 4 % y 12 %)"
            ok = bajo <= porcentaje(nulos, total) <= alto
        else:
            esperado, ok = "0", nulos == 0
        resultado.append((f"Nulos en {col}", esperado,
                          formato_cantidad(nulos, total), estado(ok)))

    # 4. Duplicados
    dup_filas = contar_filas_duplicadas(filas, columnas)
    bajo, alto = DUP_FILAS
    resultado.append(("Filas duplicadas exactas", "≈5 % (entre 3 % y 7 %)",
                      formato_cantidad(dup_filas, total),
                      estado(bajo <= porcentaje(dup_filas, total) <= alto)))

    if "id" in columnas:
        dup_id = contar_duplicados_columna(filas, "id")
        resultado.append(("Duplicados en id", f"{dup_filas} (solo los de filas repetidas)",
                          str(dup_id), estado(dup_id == dup_filas)))
    else:
        resultado.append(("Duplicados en id", "columna presente",
                          "columna ausente", "FALLA"))

    if "nit" in columnas:
        nit_rep = contar_nit_repetidos(filas, columnas)
        bajo, alto = NIT_REPETIDO
        resultado.append(("NIT repetidos entre empresas distintas",
                          "≈3 % (entre 1 % y 5 %)", formato_cantidad(nit_rep, total),
                          estado(bajo <= porcentaje(nit_rep, total) <= alto)))
    else:
        resultado.append(("NIT repetidos entre empresas distintas",
                          "columna presente", "columna ausente", "FALLA"))
    return resultado


def tabla_markdown(encabezados, filas):
    """Devuelve una tabla en Markdown (escapa el carácter '|' dentro de las celdas)."""
    def limpiar(x):
        return str(x).replace("|", "\\|")
    lineas = ["| " + " | ".join(encabezados) + " |",
              "|" + "|".join("---" for _ in encabezados) + "|"]
    for fila in filas:
        lineas.append("| " + " | ".join(limpiar(c) for c in fila) + " |")
    return "\n".join(lineas)


def tabla_por_columna(columnas, filas):
    """Arma la tabla informativa con nulos y duplicados de cada columna."""
    datos = []
    for col in columnas:
        datos.append((col, contar_nulos(filas, col),
                      contar_duplicados_columna(filas, col)))
    return tabla_markdown(["Columna", "Nulos", "Duplicados"], datos)


def main():
    """Punto de entrada: lee el archivo, revisa e imprime las tablas."""
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/revisar_datos.py empresas_sucio.csv")
    ruta = sys.argv[1]
    if not os.path.isfile(ruta):
        sys.exit(f"No encontré el archivo: {ruta}")

    columnas, filas = leer_archivo(ruta)
    comprobaciones = construir_comprobaciones(columnas, filas)

    print(f"## Revisión de {os.path.basename(ruta)}\n")
    print(tabla_markdown(["Comprobación", "Esperado", "Encontrado", "Estado"],
                         comprobaciones))
    print("\n## Nulos y duplicados por columna\n")
    print(tabla_por_columna(columnas, filas))
    pasan = sum(1 for c in comprobaciones if c[3] == "PASA")
    print(f"\n**Resultado:** {pasan} de {len(comprobaciones)} comprobaciones PASAN.")


if __name__ == "__main__":
    main()
