"""HU F01: simula la tabla empresas con datos sucios.

Uso:
    python src/simular_empresas.py
"""

import random
import uuid

import pandas as pd
from faker import Faker

# --- Constantes -------------------------------------------------------------
SECTORES = ["Logistica", "Tecnologia", "Salud", "Educacion", "Comercio",
            "Construccion", "Agroindustria", "Finanzas"]


def generar_empresas(n=300):
    """Genera n empresas con datos sucios y devuelve el DataFrame."""
    # Semilla fija: el archivo sale igual cada vez que se ejecuta.
    Faker.seed(42)
    random.seed(42)
    fake = Faker("es_CO")

    # --- 1. Datos limpios ---------------------------------------------------
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })

    # --- 2. Ensuciar los datos ---------------------------------------------
    indices = list(range(n))

    # nombre: 10 % con espacios sobrantes y 15 % en MAYUSCULAS
    for i in random.sample(indices, int(n * 0.10)):
        filas[i]["nombre"] = f"  {filas[i]['nombre']}  "
    for i in random.sample(indices, int(n * 0.15)):
        filas[i]["nombre"] = filas[i]["nombre"].upper()

    # nit: la mitad con puntos y guion (900.123.456-7), la otra mitad solo dígitos
    mezclados = random.sample(indices, n)
    for i in mezclados[: n // 2]:
        d = filas[i]["nit"].replace("-", "")
        filas[i]["nit"] = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9]}"
    for i in mezclados[n // 2:]:
        filas[i]["nit"] = filas[i]["nit"].replace("-", "")

    # sector: variantes del mismo sector ('Logistica', 'LOGISTICA', ' logistica ')
    for fila in filas:
        s = fila["sector"]
        fila["sector"] = random.choice([s, s.upper(), f" {s.lower()} "])

    # contacto: 8 % nulos (None)
    for i in random.sample(indices, int(n * 0.08)):
        filas[i]["contacto"] = None

    # correo: 6 % sin arroba (correo inválido)
    for i in random.sample(indices, int(n * 0.06)):
        filas[i]["correo"] = filas[i]["correo"].replace("@", "")

    # telefono: tres formatos mezclados
    for fila in filas:
        t = fila["telefono"]
        fila["telefono"] = random.choice([
            t,                                    # 3001234567
            f"{t[:3]} {t[3:6]} {t[6:]}",          # 300 123 4567
            f"+57 {t[:3]}-{t[3:6]}-{t[6:]}",      # +57 300-123-4567
        ])

    # activa: a veces como texto ('SI', 'No', '1', '0')
    for i in random.sample(indices, int(n * 0.25)):
        filas[i]["activa"] = random.choice(["SI", "No", "1", "0"])

    # nit: 3 % repetidos entre empresas distintas (el NIT debería ser único)
    elegidos = random.sample(indices, int(n * 0.03) * 2)
    mitad = len(elegidos) // 2
    for destino, origen in zip(elegidos[:mitad], elegidos[mitad:]):
        filas[destino]["nit"] = filas[origen]["nit"]

    # 5 % de filas repetidas tal cual (duplicados exactos). Se reemplazan filas
    # existentes por copias de otras, así la tabla queda en exactamente n filas
    # y no se tocan las filas del NIT repetido.
    n_dup = int(n * 0.05)
    libres = [i for i in indices if i not in elegidos]
    seleccion = random.sample(libres, n_dup * 2)
    for destino, origen in zip(seleccion[:n_dup], seleccion[n_dup:]):
        filas[destino] = dict(filas[origen])

    df = pd.DataFrame(filas)
    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
