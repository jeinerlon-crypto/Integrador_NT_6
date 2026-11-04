import sys
from pathlib import Path

RUTA_SRC = Path(__file__).resolve().parent / "src"
if str(RUTA_SRC) not in sys.path:
    sys.path.insert(0, str(RUTA_SRC))

from exportar_retos import exportar_retos_sucio
from simular_retos import generar_retos


def main():
    """Genera retos de prueba y exporta sus versiones CSV, XLSX y JSON."""
    retos = generar_retos()
    rutas = exportar_retos_sucio(retos)

    print(f"Retos generados: {len(retos)} filas, {len(retos.columns)} columnas.")
    for ruta in rutas:
        print(f"Archivo creado: {ruta}")


if __name__ == "__main__":
    main()