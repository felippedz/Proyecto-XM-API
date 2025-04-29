import pandas as pd
import os

#Ruta del archivo
ruta_archivo = os.path.join("","datos","datos_API (1).xlsx")

# Leer el archivo Excel
df = pd.read_excel(ruta_archivo)

# Mostrar las primeras filas del DataFrame
print(df.head())

# Extracción de las métricas
if 'MetricId' in df.columns and 'Entity' in df.columns and 'Type' in df.columns and 'Url' in df.columns:
    metricas = df[['MetricId', 'Entity', 'Type','Url']].drop_duplicates()
    #tipo = df[['Type']]
    #url = df[['Url']]
    print("Métricas disponibles:")
    print(metricas)
else:
    print("Las columnas 'MetricId' y 'Entity' no se encuentran en el DataFrame.")
    metricas = pd.DataFrame()