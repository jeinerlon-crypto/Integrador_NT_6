import pandas as pd

from notebook.simulaciones.simular_retos import generar_datos_limpios, ensuciar
from notebook.exportaciones.exportar_retos import exportar_retos_crudos, exportar_retos_limpios

print("***********SIMULACION DE RETOS************")
retos_df = pd.DataFrame(generar_datos_limpios())
retos_sucios_df = ensuciar(retos_df)
print(retos_sucios_df)

print("********EXPORTACION DE RETOS CRUDOS***************")
rutas_crudas = exportar_retos_crudos(retos_sucios_df)
for ruta in rutas_crudas:
    print("Archivo Creado")