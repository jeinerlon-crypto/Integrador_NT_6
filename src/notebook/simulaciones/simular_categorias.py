import random
import uuid
import unicodedata

import pandas as pd
from faker import Faker

CATEGORIAS = ['DESARROLLO WEB', 'DESARROLLO MÓVIL', 'CIENCIA DE DATOS', 'INTELIGENCIA ARTIFICIAL', 'CIBERSEGURIDAD', 'INFRAESTRUCTURA Y NUBE', 'DISEÑO UX/UI', 'MARKETING DIGITAL', 'GESTIÓN ADMINISTRATIVA', 'SOPORTE TÉCNICO']
AREAS = ['TECNOLOGÍA', 'ANALÍTICA', 'SEGURIDAD INFORMÁTICA', 'INFRAESTRUCTURA', 'DISEÑO', 'MERCADEO', 'ADMINISTRACIÓN', 'MESA DE AYUDA']
FILAS = 250
PORCENTAJE_DUPLICADOS = 0.08

fake = Faker('es_CO')
Faker.seed(42)
random.seed(42)


def quitar_tildes(texto):
	normalizado = unicodedata.normalize('NFD', texto)
	return ''.join(c for c in normalizado if unicodedata.category(c) != 'Mn')


def generar_muestra(datos, porcentaje):
	return datos.sample(frac = porcentaje, random_state = random.randint(0, 999)).index


def escribir_mal(texto):
	variantes = [quitar_tildes(texto.capitalize()), quitar_tildes(texto.upper()), quitar_tildes(f' {texto.lower()} '), texto.lower()]
	return random.choice(variantes)


def ensuciar(datos_df):
	datos_df = datos_df.copy()

	filas_elegidas = generar_muestra(datos_df, 0.05)
	datos_df.loc[filas_elegidas, 'nombre'] = datos_df.loc[filas_elegidas, 'nombre'].map(escribir_mal)

	filas_elegidas = generar_muestra(datos_df, 0.15)
	datos_df.loc[filas_elegidas, 'descripcion'] = None

	filas_elegidas = generar_muestra(datos_df, 0.1)
	datos_df.loc[filas_elegidas, 'area_responsable'] = None

	return datos_df


def agregar_duplicados(datos_df, cantidad):
	copias = datos_df.sample(n = cantidad, random_state = random.randint(0, 999))
	datos_df = pd.concat([datos_df, copias], ignore_index = True)
	return datos_df.sample(frac = 1, random_state = random.randint(0, 999)).reset_index(drop = True)


def generar_categorias(n = FILAS):
	duplicados = round(n * PORCENTAJE_DUPLICADOS)
	filas = []
	for _ in range(n - duplicados):
		filas.append({
			'id': str(uuid.uuid4()),
			'nombre': random.choice(CATEGORIAS),
			'descripcion': fake.sentence(nb_words = 8),
			'area_responsable': random.choice(AREAS)
		})
	df = ensuciar(pd.DataFrame(filas))
	df = agregar_duplicados(df, duplicados)
	return df


if __name__ == '__main__':
	df = generar_categorias()
	print(df.shape)
	print(df.head())
	print(df.isna().sum())