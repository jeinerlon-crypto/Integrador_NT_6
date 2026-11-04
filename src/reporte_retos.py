import sys
from pathlib import Path
import pandas as pd

def cargar_archivo(ruta_archivo):
    """
    Lee el archivo de datos basándose en su extensión y devuelve un DataFrame.
    Soporta CSV, XLSX y JSON.
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")

    ext = ruta.suffix.lower()
    if ext == '.csv':
        with open(ruta, encoding="utf-8-sig") as archivo:
            encabezado = archivo.readline()
        separador = ";" if encabezado.count(";") > encabezado.count(",") else ","
        return pd.read_csv(ruta, sep=separador, encoding="utf-8-sig")
    elif ext == '.xlsx':
        return pd.read_excel(ruta)
    elif ext == '.json':
        return pd.read_json(ruta)
    else:
        raise ValueError(f"Extensión no soportada: {ext}. Usa .csv, .xlsx o .json")

def ejecutar_comprobaciones(df):
    """
    Evalúa el DataFrame contra los criterios de aceptación de la HU.
    Retorna una lista de diccionarios con el formato para la tabla Markdown.
    """
    resultados = []
    
    # 1. Comprobación de total de filas
    filas_esperadas = 500
    filas_encontradas = len(df)
    resultados.append({
        "Comprobación": "Total de filas",
        "Esperado": str(filas_esperadas),
        "Encontrado": str(filas_encontradas),
        "Estado": "PASA" if filas_encontradas == filas_esperadas else "FALLA"
    })

    # 2. Comprobación de columnas requeridas
    columnas_esperadas = [
        "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin", 
        "estado", "id_empresa", "id_categoria", "id_prioridad"
    ]
    columnas_encontradas = df.columns.tolist()
    columnas_faltantes = [
        col for col in columnas_esperadas if col not in columnas_encontradas
    ]
    columnas_sobrantes = [
        col for col in columnas_encontradas if col not in columnas_esperadas
    ]
    
    if columnas_faltantes or columnas_sobrantes:
        estado_cols = "FALLA"
        detalles = []
        if columnas_faltantes:
            detalles.append(f"Faltan: {', '.join(columnas_faltantes)}")
        if columnas_sobrantes:
            detalles.append(f"Sobran: {', '.join(columnas_sobrantes)}")
        encontrado_cols = "; ".join(detalles)
    else:
        estado_cols = "PASA"
        encontrado_cols = "Todas presentes"
        
    resultados.append({
        "Comprobación": "Columnas requeridas",
        "Esperado": "9 columnas exactas",
        "Encontrado": encontrado_cols,
        "Estado": estado_cols
    })

    # 3. Comprobación de filas duplicadas (5% de 500 = 25)
    duplicados_esperados = 25
    duplicados_encontrados = df.duplicated().sum()
    resultados.append({
        "Comprobación": "Filas duplicadas (exactas)",
        "Esperado": str(duplicados_esperados),
        "Encontrado": str(duplicados_encontrados),
        "Estado": "PASA" if duplicados_encontrados == duplicados_esperados else "FALLA"
    })

    # 4. Comprobación de nulos por cada columna
    nulos_esperados = {
        "id": 0,
        "nombre": 0,
        "descripcion": 60,  # 12% de 500
        "fecha_inicio": 0,
        "fecha_fin": 40,    # 8% de 500
        "estado": 0,
        "id_empresa": 0,
        "id_categoria": 0,
        "id_prioridad": 0
    }

    for col in columnas_esperadas:
        esperado = nulos_esperados[col]
        if col in df.columns:
            nulos_encontrados = df[col].isna().sum()
            estado_nulos = "PASA" if nulos_encontrados == esperado else "FALLA"
            texto_encontrado = str(nulos_encontrados)
        else:
            estado_nulos = "FALLA"
            texto_encontrado = "Columna no existe"

        resultados.append({
            "Comprobación": f"Nulos en '{col}'",
            "Esperado": str(esperado),
            "Encontrado": texto_encontrado,
            "Estado": estado_nulos
        })

    return resultados

def imprimir_markdown(resultados):
    """
    Toma la lista de resultados y la imprime en consola con formato de tabla Markdown.
    """
    print("| Comprobación | Esperado | Encontrado | Estado |")
    print("|---|---|---|---|")
    for r in resultados:
        print(f"| {r['Comprobación']} | {r['Esperado']} | {r['Encontrado']} | {r['Estado']} |")


def _convertir_fechas(serie):
    """Convierte fechas ISO y dd/mm/aaaa sin invertir el formato ISO."""
    iso = pd.to_datetime(serie, format="%Y-%m-%d", errors="coerce")
    resto = pd.to_datetime(
        serie[iso.isna()], format="mixed", dayfirst=True, errors="coerce"
    )
    return iso.fillna(resto)


def generar_graficas(df):
    """Guarda gráficas de estados, nulos y duración en reportes/."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    carpeta_reportes = Path(__file__).resolve().parent.parent / "reportes"
    carpeta_reportes.mkdir(parents=True, exist_ok=True)
    archivos = []

    if "estado" in df.columns:
        estados = (
            df["estado"].astype("string").str.strip().str.upper()
            .str.replace(r"\s+", "_", regex=True).fillna("SIN_ESTADO")
        )
        conteo_estados = estados.value_counts().sort_index()
        figura, eje = plt.subplots(figsize=(9, 5))
        conteo_estados.plot(kind="bar", ax=eje, color="#4472C4")
        eje.set_title("Cantidad de retos por estado")
        eje.set_xlabel("Estado")
        eje.set_ylabel("Cantidad")
        eje.tick_params(axis="x", labelrotation=30)
        figura.tight_layout()
        ruta = carpeta_reportes / "retos_por_estado.png"
        figura.savefig(ruta, dpi=150)
        plt.close(figura)
        archivos.append(ruta)
    else:
        print("No se genera retos_por_estado.png: falta la columna 'estado'.")

    nulos = df.isna().sum().sort_values(ascending=False)
    figura, eje = plt.subplots(figsize=(10, 5))
    nulos.plot(kind="bar", ax=eje, color="#ED7D31")
    eje.set_title("Valores nulos por columna")
    eje.set_xlabel("Columna")
    eje.set_ylabel("Cantidad de nulos")
    eje.tick_params(axis="x", labelrotation=45)
    figura.tight_layout()
    ruta = carpeta_reportes / "nulos_por_columna.png"
    figura.savefig(ruta, dpi=150)
    plt.close(figura)
    archivos.append(ruta)

    if {"estado", "fecha_inicio", "fecha_fin"}.issubset(df.columns):
        inicio = _convertir_fechas(df["fecha_inicio"])
        fin = _convertir_fechas(df["fecha_fin"])
        duracion = (fin - inicio).dt.days
        validas = duracion[duracion >= 0].dropna()
        if not validas.empty:
            estados = (
                df.loc[validas.index, "estado"].astype("string")
                .str.strip().str.upper()
                .str.replace(r"\s+", "_", regex=True).fillna("SIN_ESTADO")
            )
            promedio = validas.groupby(estados).mean().sort_index()
            figura, eje = plt.subplots(figsize=(9, 5))
            promedio.plot(kind="bar", ax=eje, color="#70AD47")
            eje.set_title("Duración promedio válida por estado")
            eje.set_xlabel("Estado")
            eje.set_ylabel("Duración promedio (días)")
            eje.tick_params(axis="x", labelrotation=30)
            figura.tight_layout()
            ruta = carpeta_reportes / "duracion_por_estado.png"
            figura.savefig(ruta, dpi=150)
            plt.close(figura)
            archivos.append(ruta)
        else:
            print("No se genera duracion_por_estado.png: no hay fechas válidas.")
    else:
        print(
            "No se genera duracion_por_estado.png: faltan columnas de estado "
            "o fechas."
        )

    for archivo in archivos:
        print(f"Gráfica guardada: {archivo}")


def main():
    """
    Valida argumentos, carga datos, imprime las reglas y genera las gráficas.
    """
    if len(sys.argv) != 2:
        print("Uso: python src/reporte_retos.py <ruta_archivo>")
        sys.exit(1)
        
    ruta_archivo = sys.argv[1]
    
    try:
        df = cargar_archivo(ruta_archivo)
        resultados = ejecutar_comprobaciones(df)
        imprimir_markdown(resultados)
        generar_graficas(df)
    except (FileNotFoundError, ValueError, OSError, ImportError) as e:
        print(f"Error durante la ejecución: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()