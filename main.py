"""Punto de entrada del proyecto integrador (tabla registros).

Ejecuta todo el flujo, en orden:
    1. HU F01: simula los registros sucios.
    2. HU X01: exporta los registros sucios a CSV, JSON y Excel en data/crudo/.
    3. HU L01: limpia los datos y guarda data/limpio/registros_limpio.csv.
    4. HU Q01: responde las cinco consultas y guarda data/limpio/registros_consulta_N.csv.
    5. HU G01: crea las tres graficas en reportes/ e imprime las conclusiones.

Uso (desde la raiz del proyecto):
    python main.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Los scripts de src/ se importan entre si (exportar_registros importa simular_registros),
# por eso se agrega src/ a la ruta de busqueda de modulos.
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd  # noqa: E402

import consultas_registros  # noqa: E402
import exportar_registros  # noqa: E402
import limpiar_registros  # noqa: E402
import reporte_registros  # noqa: E402
import simular_registros  # noqa: E402

RUTA_CRUDO = RAIZ / "data" / "crudo" / "registros_sucio.csv"
RUTA_LIMPIO = RAIZ / "data" / "limpio" / "registros_limpio.csv"
CARPETA_REPORTES = RAIZ / "reportes"


def paso_simular():
    """HU F01: genera el DataFrame sucio de registros."""
    print("\n########## 1. SIMULAR REGISTROS (HU F01) ##########")
    df_sucio = simular_registros.generar_registros()
    print("shape:", df_sucio.shape)
    return df_sucio


def paso_exportar(df_sucio):
    """HU X01: guarda el DataFrame sucio en CSV, JSON y Excel."""
    print("\n########## 2. EXPORTAR REGISTROS (HU X01) ##########")
    for ruta in exportar_registros.exportar_registros_crudos(df_sucio):
        print(f"{ruta} -> {df_sucio.shape}")


def paso_limpiar():
    """HU L01: lee el CSV sucio, limpia y guarda el CSV limpio."""
    print("\n########## 3. LIMPIAR REGISTROS (HU L01) ##########")
    df = pd.read_csv(RUTA_CRUDO)
    filas_antes = len(df)
    limpiar_registros.imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = limpiar_registros.limpiar(df)

    limpiar_registros.imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")
    print(f"\nFilas antes: {filas_antes} | despues: {len(df)} | eliminadas: {filas_antes - len(df)}")

    RUTA_LIMPIO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_LIMPIO, index=False, encoding="utf-8")
    print(f"Archivo limpio guardado en: {RUTA_LIMPIO}")
    return df


def paso_consultar():
    """HU Q01: responde las cinco consultas sobre el CSV limpio."""
    print("\n########## 4. CONSULTAR REGISTROS (HU Q01) ##########")
    # Se relee el CSV limpio (como texto) para que las consultas trabajen
    # con el mismo archivo que se entrega, no con el DataFrame en memoria.
    df = consultas_registros.cargar_datos(RUTA_LIMPIO)
    carpeta = str(RUTA_LIMPIO.parent)

    consultas_registros.consulta_1(df, carpeta)
    consultas_registros.consulta_2(df, carpeta)
    consultas_registros.consulta_3(df, carpeta)
    consultas_registros.consulta_4(df, carpeta)
    consultas_registros.consulta_5(df, carpeta)


def paso_graficar():
    """HU G01: crea las tres graficas en reportes/ e imprime las conclusiones."""
    print("\n########## 5. GRAFICAR REGISTROS (HU G01) ##########")
    # Se fuerza la carpeta de salida a la raiz del proyecto, sin importar
    # desde donde se ejecute el script.
    reporte_registros.CARPETA_SALIDA = str(CARPETA_REPORTES)
    CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)

    df = reporte_registros.cargar_datos(RUTA_LIMPIO)
    rutas = [
        reporte_registros.grafica_estados(df),
        reporte_registros.grafica_meses(df),
        reporte_registros.grafica_retos(df),
    ]

    print("Graficas generadas:")
    for ruta in rutas:
        print(f"  {ruta}")

    print("\nConclusiones:")
    for linea in reporte_registros.construir_conclusiones(df):
        print(linea)


def main():
    df_sucio = paso_simular()
    paso_exportar(df_sucio)
    paso_limpiar()
    paso_consultar()
    paso_graficar()


if __name__ == "__main__":
    main()