"""HU X01: exporta la tabla empresas sucia a CSV, Excel y JSON.

Uso (desde la raíz del proyecto):
    python src/exportar_empresas.py
"""

import os
import sys
from importlib import import_module

# Agrega la carpeta src/simulaciones para poder importar simular_empresas.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "simulaciones"))

# Se importa la función del script anterior; no se copia su código.
generar_empresas = import_module("simular_empresas").generar_empresas

def main():
    """Genera los datos y los guarda en data/crudo/ en tres formatos."""
    df = generar_empresas()

    # La carpeta se crea sola si no existe.
    os.makedirs("data/crudo", exist_ok=True)

    ruta_csv = "data/crudo/empresas_sucio.csv"
    ruta_xlsx = "data/crudo/empresas_sucio.xlsx"
    ruta_json = "data/crudo/empresas_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    # Ruta y tamaño de cada archivo generado.
    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    main()
