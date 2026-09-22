import random
import uuid
from faker import Faker
from datetime import timedelta #Random y faker para simular datos semillas#

#1.- Configurar el faker a la region que necesites

fake=Faker("es_CO")

#2.- Sembrar semillas para tener coherencia en los datos simulados

Faker.seed(42)
random.seed(42)

#4.-Identifico los datos que sean un selector

ESTADOS = ['ABIERTO', 'EN PROCESO', 'CERRADO', 'EVALUACION']
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(5)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]

#5.- Defino mi DATASET(Definir con cuantas filas se van a utilizar)
FILAS=500

#6.-Construyo una funcion para generar los n datos pedidos(LIMPIOS)
def generar_datos():
    filas=[]
    for _ in range (FILAS):

        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")

        filas.append({
                "id": str(uuid.uuid4()),
                "nombre":  fake.sentence(nb_words=6).rstrip("."),
                "descripcion": fake.sentence(nb_words=12),
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
                "estado": random.choice(ESTADOS),
                "id_empresa" :random.choice(IDS_EMPRESA),
                "id_categoria": random.choice(IDS_CATEGORIA),
                "id_prioridad": random.choice(IDS_PRIORIDAD)
        })

    return filas

