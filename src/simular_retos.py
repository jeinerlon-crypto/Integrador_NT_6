import random
import uuid
from datetime import timedelta
import pandas as pd
from faker import Faker

# 1. Configurar el faker a la región requerida
fake = Faker("es_CO")

# 2. Sembrar semillas para garantizar reproducibilidad
Faker.seed(42)
random.seed(42)

# 3. Constantes de selectores
ESTADOS = ["ABIERTO", "EN PROCESO", "CERRADO", "EVALUACION"]
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(5)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]

FILAS = 500


# Función auxiliar para ensuciar
def generar_muestra(datos_df, porcentaje):
    return datos_df.sample(
        frac=porcentaje,
        random_state=random.randint(1, 999),
    ).index


# 4. Función para generar datos limpios
def generar_datos_limpios(n=FILAS):
    filas = []
    for _ in range(n):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return pd.DataFrame(filas)


# 5. Función para ensuciar los datos respetando la lógica de fechas
def ensuciar(datos_df):
    datos_df = datos_df.copy()
    datos_df["fecha_inicio"] = pd.to_datetime(datos_df["fecha_inicio"], errors="coerce")
    datos_df["fecha_fin"] = pd.to_datetime(datos_df["fecha_fin"], errors="coerce")

    # nombre: 10% con espacios sobrantes
    filas_elegidas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = " " + datos_df.loc[filas_elegidas, "nombre"] + " "

    # descripcion: 12% nulos (None)
    filas_elegidas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "descripcion"] = None

    # fecha_fin: 8% nulos
    filas_elegidas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "fecha_fin"] = None

    # fecha_fin: 5% anterior a fecha_inicio (error lógico a detectar)
    filas_con_fecha_fin = datos_df.index[datos_df["fecha_fin"].notna()]
    n_muestras = min(round(len(datos_df) * 0.05), len(filas_con_fecha_fin))
    if n_muestras > 0:
        filas_elegidas = datos_df.loc[filas_con_fecha_fin].sample(
            n=n_muestras, random_state=random.randint(1, 999)
        ).index
        datos_df.loc[filas_elegidas, "fecha_fin"] = [
            f_inicio - pd.Timedelta(days=random.randint(1, 30))
            for f_inicio in datos_df.loc[filas_elegidas, "fecha_inicio"]
        ]

    # fecha_inicio: mezclar formato ISO "2026-03-02" y latino "02/03/2026" (40% latino)
    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas_elegidas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas_elegidas, "fecha_inicio"] = latino.loc[filas_elegidas]

    # estado: variantes de la HU ('en_curso', 'EN CURSO', ' Cerrado ') en el 10% de las filas
    filas_elegidas = generar_muestra(datos_df, 0.10)
    variantes_estado = ["en_curso", "EN CURSO", " Cerrado "]
    datos_df.loc[filas_elegidas, "estado"] = [random.choice(variantes_estado) for _ in filas_elegidas]

    # 5% de filas duplicadas exactas (se copian filas completas sobre otras)
    filas_duplicadas = generar_muestra(datos_df, 0.05)
    if len(filas_duplicadas) > 0:
        filas_origen = datos_df.drop(index=filas_duplicadas).sample(
            n=len(filas_duplicadas), random_state=random.randint(1, 999)
        ).index
        datos_df.loc[filas_duplicadas] = datos_df.loc[filas_origen].to_numpy()

    return datos_df


# 6. Función principal que retorna el DataFrame
def generar_retos(n=FILAS):
    df = ensuciar(generar_datos_limpios(n))
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())