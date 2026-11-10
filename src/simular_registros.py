import random
import uuid
import pandas as pd
from faker import Faker


# 1 Configurar el faker a la region que necesites
fake = Faker("es_CO")


# 2 Sembrar semillas para tener coherencia en los datos simulados
Faker.seed(42)
random.seed(42)


# 3 Identifico los datos que debo simular
# id (texto UUID)
# fecha_registro (fecha y hora)
# observacion (texto)
# estado (texto)
# id_usuario (texto UUID)
# id_reto (texto UUID)


# 4 Identifico los datos que sean un selector
ESTADOS = ["Inscrito", "En proceso", "Finalizado"]

# Con pocos ids (5 x 5 = 25 pares) casi todas las filas repetian el par usuario + reto
# por azar (92%). Con 200 x 200 = 40.000 pares solo se repiten los que ensuciamos a proposito.
IDS_USUARIO = [str(uuid.uuid4()) for _ in range(200)]

IDS_RETO = [str(uuid.uuid4()) for _ in range(200)]

# 5 Defino mi DATASET
FILAS = 800


# 6 ENSUCIAR LOS DATOS
# Funcion para definir porcentajes de error
def generar_muestra(datos_df, porcentaje):
    return datos_df.sample(frac=porcentaje, random_state=random.randint(1, 999)).index


# Funcion para escribir mal un texto
def escribir_mal_texto(texto):
    variantes = [texto.lower(), f" {texto.title()} ", texto.upper()]

    return random.choice(variantes)


def ensuciar(datos_df):
    # 1 20% de observacion en None
    filas_elegidas = generar_muestra(datos_df, 0.20)

    datos_df.loc[filas_elegidas, "observacion"] = None

    # 2 10% de observacion con espacios sobrantes (solo donde hay texto,
    #   para no convertir los None en espacios y perder nulos)
    filas_elegidas = generar_muestra(datos_df, 0.10)
    filas_con_texto = filas_elegidas[datos_df.loc[filas_elegidas, "observacion"].notna().to_numpy()]

    datos_df.loc[filas_con_texto, "observacion"] = " " + datos_df.loc[filas_con_texto, "observacion"] + " "

    # 3 10% de estados con diferentes formas de escritura
    filas_elegidas = generar_muestra(datos_df, 0.10)

    datos_df.loc[filas_elegidas, "estado"] = datos_df.loc[filas_elegidas, "estado"].map(escribir_mal_texto)

    # 4 Mezclar dos formatos de fecha
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")

    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")

    datos_df["fecha_registro"] = iso

    filas_elegidas = generar_muestra(datos_df, 0.50)

    datos_df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]

    # 5 10% de pares usuario + reto repetidos
    filas_elegidas = generar_muestra(datos_df, 0.10)

    for indice in filas_elegidas:

        fila_origen = random.randint(0, len(datos_df) - 1)

        datos_df.loc[indice, "id_usuario"] = datos_df.loc[fila_origen, "id_usuario"]

        datos_df.loc[indice, "id_reto"] = datos_df.loc[fila_origen, "id_reto"]

    # 6 5% de filas como duplicados exactos
    filas_duplicadas = generar_muestra(datos_df, 0.05)

    filas_origen = datos_df.drop(index=filas_duplicadas).sample(
        n=len(filas_duplicadas), random_state=random.randint(1, 999)
    ).index

    datos_df.loc[filas_duplicadas] = datos_df.loc[filas_origen].to_numpy()

    return datos_df


# 7 Funcion para generar los registros: devuelve el DataFrame sucio
def generar_registros(n=FILAS):

    filas = []

    for _ in range(n):

        filas.append({
            "id": str(uuid.uuid4()),

            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),

            "observacion": fake.sentence(nb_words=10),

            "estado": random.choice(ESTADOS),

            "id_usuario": random.choice(IDS_USUARIO),

            "id_reto": random.choice(IDS_RETO)
        })

    df = pd.DataFrame(filas)

    ensuciar(df)

    return df


if __name__ == "__main__":
    df = generar_registros()

    print(df.shape)
    print(df.head())
    print(df.isna().sum())