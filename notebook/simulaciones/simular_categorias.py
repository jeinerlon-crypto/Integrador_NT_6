import random
import uuid
from faker import Faker
import pandas as pd
import unicodedata

fake = Faker('es_CO')

Faker.seed(42)
random.seed(42)

CATEGORIAS = ['Desarrollo web', 'Desarrollo móvil', 'Ciencia de datos', 'Inteligencia artificial', 'Ciberseguridad', 'Infraestructura y nube', 'Diseño ux/ui', 'Marketing digital', 'Gestión administrativa', 'Soporte técnico']
AREAS = ['Tecnología', 'Analítica', 'Seguridad informática', 'Infraestructura', 'Diseño', 'Mercadeo', 'Administración', 'Mesa de ayuda']
FILAS = 250

def generar_categorias(numero_datos = FILAS):
	filas = []
	for _ in range(numero_datos):
		filas.append({
			'id': str(uuid.uuid4()),
			'nombre': random.choice(CATEGORIAS),
			'descripcion': fake.sentence(nb_words = 8),
			'area_responsable': random.choice(AREAS)
		})
	return filas

datos_limpios = pd.DataFrame(generar_categorias())

def quitar_tildes(texto):
  normalizado = unicodedata.normalize("NFD", texto)
  sin_tildes = "".join([c for c in normalizado if unicodedata.category(c) != "Mn"])
  return sin_tildes

def generar_muestra(datos, porcentaje):
	return datos.sample(frac = porcentaje, random_state = random.randint(0, 999)).index

def escribir_mal(texto):
	variantes = [quitar_tildes(texto.capitalize()), quitar_tildes(texto.upper()), quitar_tildes(f' {texto.lower()} '), texto.lower()]
	return random.choice(variantes)

def ensuciar(datos_df):
	datos_df = datos_df.copy()

	filas_elegidas = generar_muestra(datos_df, random.uniform(0.01, 0.2))
	datos_df.loc[filas_elegidas, 'nombre'] = datos_df.loc[filas_elegidas, 'nombre'].map(escribir_mal)

	filas_elegidas = generar_muestra(datos_df, 0.15)
	datos_df.loc[filas_elegidas, 'descripcion'] = None

	filas_elegidas = generar_muestra(datos_df, 0.1)
	datos_df.loc[filas_elegidas, 'area_responsable'] = None

	print(datos_df)

ensuciar(datos_limpios)