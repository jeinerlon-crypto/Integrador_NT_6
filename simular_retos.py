#El elemento central: la necesidad que publica la empresa. Crea el script `src/simular_retos.py`. Con la libreria **Faker** genera 500 filas falsas de la tabla `retos`, con las MISMAS columnas que usa Backend II. Despues **ensucia los datos a proposito**: nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos. Esos errores son los que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos. Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)` para que el resultado sea SIEMPRE el mismo y tu compañero pueda reproducirlo.#

import random
import uuid
from faker import Faker #Random y faker para simular datos semillas#

#1.- Configurar el faker a la region que necesites

fake=Faker("es_CO")

#2.- Sembrar semillas para tener coherencia en los datos simulados

Faker.seed(42)
random.seed(42)

#3.- Identifico los datos que debo simular
#id (texto (UUID)
#nombre (texto)
# #descripcion (texto)
# #fecha_inicio (fecha)
# #fecha_fin (fecha)
# #estado (texto) :propuesto,listo, en proceso, anulado
# #id_empresa (texto (UUID) 
# #id_categoria (texto (UUID)
# #id_prioridad (texto (UUID) : Alta, baja, media


#4.-Identifico los datos que sean un selector
ESTADOS=["PROPUESTO","EN EJECUCION", "ANULADO","LISTO","POR CONFIRMAR"]

#5.- Defino mi DATASET(Definir con cuantas filas se van a utilizar)
FILAS=500

