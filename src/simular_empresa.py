'''
Organizacion que registra o propone retos. Crea el script `src/simular_empresas.py`. 
Con la libreria **Faker** genera 300 filas falsas de la tabla `empresas`, con las MISMAS columnas que usa Backend II. 
Despues **ensucia los datos a proposito**: 
nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos. 
Esos errores son los que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)` 
para que el resultado sea SIEMPRE el mismo y tu compañero pueda reproducirlo.

'''

import random
import uuid
import pandas as pd
from faker import Faker

#1. Configurar el faker a la region que necesito
fake= Faker("es_CO")

#2. Sembrar semillas para tener coherencia en los datos simulados
Faker.seed(42)
random.seed(42)

#3.Identifica los datos que debo simular
#Se generan 300 filas con estas columnas: 
# id (texto (UUID)), 
# nombre (texto), 
# nit (texto), 
# sector (texto), (selector)
# contacto (texto), 
# correo (texto), 
# telefono (texto), 
# activa (booleano).

#4. Identifico  los datos o el dato qUe sea un selector
SECTORES = ["TRANSPORTE", "SERVICIOS", "CONSTRUCCION", "ALIMENTOS"]

#5. Defino mi DATASET 
FILAS = 300

#6. Construyo una funcion para generar los n datos pedidos (limpio)
def generar_datos_limpios(numero_datos=FILAS):
    filas = []
    for _ in range(numero_datos):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify(text="#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify(text="3#########"),
            "activa": random.choice([True, False])
        })
    return filas

variable_noche=pd.DataFrame(generar_datos_limpios())

#Ensuciar los datos

#1. Crear una funcion para definir porcetajes de error (procesos estocasticos)
def generar_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(1, 999)).index
#2. Crear uan funcion para escribir mal un texto
def escribir_mal_texto(texto):
    variantes = [texto.lower(), f"{texto.title()} ", texto.capitalize()]
    return random.choice(variantes)

def cambiar_telefono_formato(telefono):
    formatos = [
        telefono,  # Formato original
        f"{telefono[:3]} {telefono[3:6]} {telefono[6:]}",  # Formato con espacios
        f"+57 {telefono[:3]}-{telefono[3:6]}-{telefono[6:]}"  # Formato internacional
    ]
    return random.choice(formatos)

#3. Crear una funcion para convertir booleanos a texto
def convertir_booleano_texto(valor):
    if valor:
        return random.choice(["SI", "1"])
    else:
        return random.choice(["NO", "0"])
#4.Funcion para ensucuiar los datos
def ensuciar(datos_df):
    datos_df=datos_df.copy()

    #nombre: 10% con espacios sobrantes, el 15% con mayusculas
    filas_elegidas=generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"]=" " + datos_df.loc[filas_elegidas, "nombre"] + " "
    filas_elegidas=generar_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "nombre"]=datos_df.loc[filas_elegidas, "nombre"].str.upper()

    #nit: 50% con puntos y guiones, 50% sin nada
    filas_elegidas=generar_muestra(datos_df, 0.50)
    datos_df.loc[filas_elegidas, "nit"]=datos_df.loc[filas_elegidas, "nit"].str.replace("-", "", regex=False)
    datos_df.loc[filas_elegidas, "nit"]=datos_df.loc[filas_elegidas, "nit"].str.replace(".", "", regex=False)

    #sector: variantes de escritura (Logistica, LOGISTICA, logistica)
    filas_elegidas=generar_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "sector"]=datos_df.loc[filas_elegidas, "sector"].map(escribir_mal_texto)

    #contacto: 8% en none
    filas_elegidas=generar_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "contacto"]=None

    #correo: 6% sin arroba (correo invalido)
    filas_elegidos=generar_muestra(datos_df, 0.06)
    datos_df.loc[filas_elegidos, "correo"]=datos_df.loc[filas_elegidos, "correo"].str.replace("@", "", regex=False)

    #telefono: tres formatos mezclados ('3001234567', '300 123 4567', '+57 300-123-4567')
    filas_elegidas=generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "telefono"]=datos_df.loc[filas_elegidas, "telefono"].map(cambiar_telefono_formato)

    #activa en ocaciones llega SI NO 1 o 0
    datos_df["activa"]=datos_df["activa"].astype(str)
    filas_elegidas=generar_muestra(datos_df, 0.30)
    datos_df.loc[filas_elegidas, "activa"]=datos_df.loc[filas_elegidas, "activa"].map(convertir_booleano_texto)

    #filas repetidas(duplicados exactos)
    filas_elegidas=generar_muestra(datos_df, 0.05)
    datos_df=pd.concat([datos_df, datos_df.loc[filas_elegidas]], ignore_index=True)

    #nit repetidos entre empresas distintas(nit unico) 3%
    filas_elegidas=generar_muestra(datos_df, 0.03)
    nit_repetido=datos_df.loc[filas_elegidas, "nit"].values[0]
    datos_df.loc[filas_elegidas, "nit"]=nit_repetido

    print(datos_df)
    return datos_df

#Generar empresas con datos sucios
def generar_empresas(n=300):
    df= pd.DataFrame(generar_datos_limpios(n))
    df=ensuciar(df)
    return df 

#Bloque principal para ejecutar el script
if __name__ == "__main__":
    df=generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
