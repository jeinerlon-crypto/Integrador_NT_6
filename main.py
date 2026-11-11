from src.notebook.simulaciones.simular_categorias import generar_categorias
from src.notebook.exportaciones.exportar_categorias import exportar_categorias_crudos
from src.notebook.limpieza import limpiar_categorias
from src.notebook.consultas import consultas_categorias
from src.notebook.reportes import reporte_categorias

from src.notebook.simulaciones.simular_prioridades import generar_prioridades
from src.notebook.exportaciones.exportar_prioridades import exportar_prioridades_crudos
from src.notebook.limpieza import limpiar_prioridades
from src.notebook.consultas import consultas_prioridades
from src.notebook.reportes import reporte_prioridades


def main():
	print('===== CATEGORIAS =====')
	df = generar_categorias()
	for ruta in exportar_categorias_crudos(df):
		print(ruta, df.shape)
	limpiar_categorias.main()
	consultas_categorias.main()
	reporte_categorias.main()

	print('\n===== PRIORIDADES =====')
	df = generar_prioridades()
	for ruta in exportar_prioridades_crudos(df):
		print(ruta, df.shape)
	limpiar_prioridades.main()
	consultas_prioridades.main()
	reporte_prioridades.main()


if __name__ == '__main__':
	main()