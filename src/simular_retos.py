import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

#1.- Configurar el faker a la region que necesites
fake = Faker("es_CO")

#2.- Sembrar semillas para tener coherencia en los datos simulados
Faker.seed(42)
random.seed(42)

#3.- Identifico los datos que debo simular
#id (texto (UUID)
#nombre (texto)
#descripcion (texto)
#fecha_inicio (fecha)
#fecha_fin (fecha)
#estado (texto): propuesto, listo, en proceso, anulado
#id_empresa (texto (UUID)
#id_categoria (texto (UUID)
#id_prioridad (texto (UUID)): Alta, baja, media

#4.- Identifico los datos que sean un selector
ESTADOS = ["ABIERTO", "EN PROCESO", "CERRADO", "EVALUACION"]
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(5)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]

#5.- Defino mi DATASET (definir con cuantas filas se van a utilizar)
FILAS = 500


def generar_datos(numero_datos=FILAS):
    filas = []
    for _ in range(numero_datos):
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

    return filas


####Ensuciar datos####

#1. Crear una funcion para definir porcentajes de error (procesos estocasticos)
def generar_muestra(datos_df, porcentaje):
    return datos_df.sample(
        frac=porcentaje,
        random_state=random.randint(1, 999),
    ).index


#2. Crear una funcion para escribir mal un texto
def escribir_mal_texto(texto):
    variantes = [texto.lower(), f"{texto.title()} ", texto.capitalize()]
    return random.choice(variantes)


#3. Crear una funcion para convertir booleanos a texto
def convertir_booleano_texto(valor):
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["NO", "0"])


#4.- Ensuciar los datos para la etapa de limpieza
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # nombre: 10% con espacios sobrantes y 8% en mayusculas
    filas_elegidas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = (
        " " + datos_df.loc[filas_elegidas, "nombre"] + " "
    )

    # descripcion: 12% en None (nulos)
    filas_elegidas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "descripcion"] = None

    # fecha_fin: 8% en None y 5% anterior a fecha_inicio
    filas_elegidas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "fecha_fin"] = None

    filas_fecha_fin = datos_df.index[datos_df["fecha_fin"].notna()]
    filas_elegidas = datos_df.loc[filas_fecha_fin].sample(
        n=round(len(datos_df) * 0.05),
        random_state=random.randint(1, 999),
    ).index
    datos_df.loc[filas_elegidas, "fecha_fin"] = [
        fecha_inicio - timedelta(days=random.randint(1, 30))
        for fecha_inicio in datos_df.loc[filas_elegidas, "fecha_inicio"]
    ]

    # fecha_inicio: mezclar formatos ISO y latino en el 40% de las filas
    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas_elegidas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas_elegidas, "fecha_inicio"] = latino.loc[
        filas_elegidas
    ]

    # estado: introducir variantes de escritura
    filas_elegidas = generar_muestra(datos_df, 0.07)
    variantes_estado = ["en_curso", "EN CURSO", "Cerrado "]
    datos_df.loc[filas_elegidas, "estado"] = [
        random.choice(variantes_estado) for _ in filas_elegidas
    ]

    # filas: duplicar exactamente el 5% de las filas
    filas_duplicadas = generar_muestra(datos_df, 0.05)
    filas_origen = datos_df.drop(index=filas_duplicadas).sample(
        n=len(filas_duplicadas),
        random_state=random.randint(1, 999),
    ).index
    datos_df.loc[filas_duplicadas] = datos_df.loc[filas_origen].to_numpy()