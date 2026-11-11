import random
import uuid

import pandas as pd
from faker import Faker

NIVELES = {'MUY ALTA': 1, 'ALTA': 2, 'MEDIA': 3, 'BAJA': 4, 'MUY BAJA': 5}
DIAS = {1: 1, 2: 3, 3: 5, 4: 8, 5: 15}
PALABRAS = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco'}
FILAS = 200
PORCENTAJE_DUPLICADOS = 0.08
VALOR_ABSURDO = 999

fake = Faker('es_CO')
Faker.seed(42)
random.seed(42)


def generar_muestra(datos, porcentaje):
	return datos.sample(frac = porcentaje, random_state = random.randint(0, 999)).index


def escribir_mal(texto):
	variantes = [texto.upper(), f' {texto.lower()} ', texto.capitalize()]
	return random.choice(variantes)


def nivel_como_texto(nivel):
	return random.choice([PALABRAS[nivel], str(nivel)])


def ensuciar(datos_df):
	datos_df = datos_df.copy()

	filas_elegidas = generar_muestra(datos_df, 0.10)
	datos_df.loc[filas_elegidas, 'nombre'] = datos_df.loc[filas_elegidas, 'nombre'].map(escribir_mal)

	datos_df['nivel'] = datos_df['nivel'].astype(object)
	filas_texto = generar_muestra(datos_df, 0.08)
	datos_df.loc[filas_texto, 'nivel'] = datos_df.loc[filas_texto, 'nivel'].map(nivel_como_texto)

	filas_elegidas = generar_muestra(datos_df.drop(filas_texto), 0.07)
	datos_df.loc[filas_elegidas, 'nivel'] = None

	datos_df['dias_max_respuesta'] = datos_df['dias_max_respuesta'].astype('Int64')
	filas_elegidas = generar_muestra(datos_df, 0.05)
	datos_df.loc[filas_elegidas, 'dias_max_respuesta'] = None

	con_dias = datos_df[datos_df['dias_max_respuesta'].notna()]
	filas_elegidas = generar_muestra(con_dias, 0.03)
	datos_df.loc[filas_elegidas, 'dias_max_respuesta'] = VALOR_ABSURDO

	return datos_df


def agregar_duplicados(datos_df, cantidad):
	copias = datos_df.sample(n = cantidad, random_state = random.randint(0, 999))
	datos_df = pd.concat([datos_df, copias], ignore_index = True)
	return datos_df.sample(frac = 1, random_state = random.randint(0, 999)).reset_index(drop = True)


def generar_prioridades(n = FILAS):
	duplicados = round(n * PORCENTAJE_DUPLICADOS)
	filas = []
	for _ in range(n - duplicados):
		nombre = random.choice(list(NIVELES.keys()))
		nivel = NIVELES[nombre]
		filas.append({
			'id': str(uuid.uuid4()),
			'nombre': nombre,
			'nivel': nivel,
			'dias_max_respuesta': DIAS[nivel]
		})
	df = ensuciar(pd.DataFrame(filas))
	df = agregar_duplicados(df, duplicados)
	return df


if __name__ == '__main__':
	df = generar_prioridades()
	print(df.shape)
	print(df.head())
	print(df.isna().sum())