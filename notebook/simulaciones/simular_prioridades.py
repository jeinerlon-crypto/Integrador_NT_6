import random
import uuid
from faker import Faker
import pandas as pd

fake = Faker('es_CO')

Faker.seed(42)
random.seed(42)

NIVELES = {'Muy alta': 1, 'Alta': 2, 'Media': 3, 'Baja': 4, 'Muy baja': 5}
DIAS = {1: 1, 2: 3, 3: 5, 4: 8, 5: 15}
FILAS = 200

def generar_prioridades(numero_datos = FILAS):
	filas = []
	for _ in range(numero_datos):
		nombre = random.choice(list(NIVELES.keys()))
		nivel = NIVELES[nombre]
		dias_max_respuesta = DIAS[nivel]

		filas.append({
			'id': str(uuid.uuid4()),
			'nombre': nombre,
			'nivel': nivel,
			'dias_max_respuesta': dias_max_respuesta
		})
	return filas

datos_limpios = pd.DataFrame(generar_prioridades())

def generar_muestra(datos, porcentaje):
	return datos.sample(frac = porcentaje, random_state = random.randint(0, 999)).index

def escribir_mal(texto):
	variantes = [texto.upper(), f' {texto.lower()} ', texto.capitalize()]
	return random.choice(variantes)

def ensuciar(datos_df):
	datos_df = datos_df.copy()

	filas_elegidas = generar_muestra(datos_df, random.uniform(0.01, 0.2))
	datos_df.loc[filas_elegidas, 'nombre'] = datos_df.loc[filas_elegidas, 'nombre'].map(escribir_mal)

	filas_elegidas = generar_muestra(datos_df, random.uniform(0.01, 0.2))
	datos_df['nivel'] = datos_df['nivel'].astype(object)

	for indice in filas_elegidas:
		valor = datos_df.at[indice, 'nivel']
		match valor:
			case 1:
				datos_df.loc[indice, 'nivel'] = random.choice(['uno', '1'])
			case 2:
				datos_df.loc[indice, 'nivel'] = random.choice(['dos', '2'])
			case 3:
				datos_df.loc[indice, 'nivel'] = random.choice(['tres', '3'])
			case 4:
				datos_df.loc[indice, 'nivel'] = random.choice(['cuatro', '4'])
			case 5:
				datos_df.loc[indice, 'nivel'] = random.choice(['cinco', '5'])
			case _:
				pass

	filas_elegidas = generar_muestra(datos_df, 0.07)
	datos_df.loc[filas_elegidas, 'nivel'] = None

	filas_elegidas = generar_muestra(datos_df, 0.05)
	datos_df.loc[filas_elegidas, 'dias_max_respuesta'] = None

	filas_elegidas = generar_muestra(datos_df, 0.05)
	datos_df.loc[filas_elegidas, 'dias_max_respuesta'] = random.randint(100, 999)

	print(datos_df)

ensuciar(datos_limpios)