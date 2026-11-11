import os
import sys
from importlib import import_module
from pathlib import Path

NOMBRE_ENTIDAD = 'categorias'
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_CRUDOS = CARPETA_PROYECTO / 'datos' / 'crudos'

sys.path.append(str(CARPETA_PROYECTO / 'notebook' / 'simulaciones'))
generar_categorias = import_module('simular_categorias').generar_categorias


def exportar_csv(df, ruta):
	df.to_csv(ruta, index = False, encoding = 'utf-8')
	return ruta


def exportar_excel(df, ruta):
	df.to_excel(ruta, index = False, sheet_name = 'categorias')
	return ruta


def exportar_json(df, ruta):
	df.to_json(ruta, orient = 'records', force_ascii = False, indent = 2)
	return ruta


def exportar_categorias_crudos(df):
	os.makedirs(CARPETA_CRUDOS, exist_ok = True)
	base = CARPETA_CRUDOS / f'{NOMBRE_ENTIDAD}_crudo'
	return [
		exportar_csv(df, base.with_suffix('.csv')),
		exportar_excel(df, base.with_suffix('.xlsx')),
		exportar_json(df, base.with_suffix('.json'))
	]


if __name__ == '__main__':
	df = generar_categorias()
	for ruta in exportar_categorias_crudos(df):
		print(ruta, df.shape)