import os
from pathlib import Path

from simular_retos import generar_retos

# 1. Rutas: la carpeta data/crudo queda en la raíz del proyecto (un nivel arriba de src/)
RAIZ = Path(__file__).resolve().parents[1]
CARPETA_CRUDO = RAIZ / "data" / "crudo"


def exportar_retos_sucio(df):
    # La carpeta se crea sola si no existe
    os.makedirs(CARPETA_CRUDO, exist_ok=True)

    ruta_csv = CARPETA_CRUDO / "retos_sucio.csv"
    ruta_xlsx = CARPETA_CRUDO / "retos_sucio.xlsx"
    ruta_json = CARPETA_CRUDO / "retos_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="retos")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2, date_format="iso")

    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    df = generar_retos()
    for ruta in exportar_retos_sucio(df):
        print(f"{ruta} -> {df.shape}")