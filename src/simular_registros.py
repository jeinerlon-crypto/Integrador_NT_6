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
ESTADOS = [  "Inscrito",  "En proceso",   "Finalizado"]

IDS_USUARIO = [ str(uuid.uuid4()) for _ in range(5)]

IDS_RETO = [  str(uuid.uuid4()) for _ in range(5)]

# 5 Defino mi DATASET
FILAS = 800

# 6 Funcion para generar los registros
def generar_registros(n=FILAS):

    filas = []

    for _ in range(n):

        filas.append({
            "id": str(uuid.uuid4()),

            "fecha_registro": fake.date_time_between(start_date="-1y",end_date="now"),

            "observacion": fake.sentence(nb_words=10),

            "estado": random.choice(ESTADOS),

            "id_usuario": random.choice(IDS_USUARIO),

            "id_reto": random.choice(IDS_RETO)
        })

    return(filas)

datos_limpios=pd.DataFrame(generar_registros())

# ENSUCIAR LOS DATOS
# Funcion para definir porcentajes de error
def generar_muestra(datos_df, porcentaje):
    return datos_df.sample(  frac=porcentaje,  random_state=random.randint(1, 999)).index

# Funcion para escribir mal un texto
def escribir_mal_texto(texto):
    variantes = [   texto.lower(),  f"{texto.title()} ", texto.upper() ]

    return random.choice(variantes)

def ensuciar(datos_df):
    # 1 20% de observacion en None
    filas_elegidas = generar_muestra( datos_df, 0.20)

    datos_df.loc[  filas_elegidas, "observacion"] = None


    # 2 10% de observacion con espacios sobrantes
    filas_elegidas = generar_muestra(datos_df,0.10)

    datos_df.loc[filas_elegidas,"observacion"] = ( " " + datos_df.loc[filas_elegidas,"observacion"].fillna("")+ " ")


    # 3 10% de estados con diferentes formas de escritura
    filas_elegidas = generar_muestra(
        datos_df,
        0.10
    )

    datos_df.loc[filas_elegidas, "estado"] = datos_df.loc[filas_elegidas,"estado"].map(escribir_mal_texto)


    # 4 Mezclar dos formatos de fecha
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")

    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")

    datos_df["fecha_registro"] = iso

    filas_elegidas = generar_muestra(datos_df,0.50)

    datos_df.loc[filas_elegidas,"fecha_registro"] = latino.loc[filas_elegidas]


    # 5 10% de pares usuario + reto repetidos
    filas_elegidas = generar_muestra(datos_df,0.10)

    for indice in filas_elegidas:

        fila_origen = random.randint(0,len(datos_df) - 1)

        datos_df.loc[indice,"id_usuario"] = datos_df.loc[fila_origen,"id_usuario"]

        datos_df.loc[indice,"id_reto"] = datos_df.loc[fila_origen,"id_reto"]


    # 6 5% de filas como duplicados exactos
    filas_duplicadas = generar_muestra(datos_df,0.05)

    filas_origen = datos_df.drop(index=filas_duplicadas).sample(n=len(filas_duplicadas),random_state=random.randint(1, 999)).index

    datos_df.loc[filas_duplicadas] = datos_df.loc[filas_origen].to_numpy()

    print(datos_df)

ensuciar(datos_limpios)