import os
import json
import pandas as pd
from datetime import datetime, timedelta

def generar_payloads():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_archivo = os.path.join(BASE_DIR, "datos", "datos_API (1).xlsx")

    # Leer Excel
    df = pd.read_excel(ruta_archivo)

    if not {'MetricId', 'Entity', 'Type', 'Url'}.issubset(df.columns):
        raise Exception("Faltan columnas en el archivo de métricas.")

    metricas = df[['MetricId', 'Entity', 'Type', 'Url']].drop_duplicates()

    # Fecha de inicio dinámica
    fecha_inicio = datetime(2023, 1, 1)
    fecha_fin = datetime.now()

    payloads = []

    while fecha_inicio < fecha_fin:
        # Determinar el siguiente rango (máximo 31 días)
        next_fecha = fecha_inicio + timedelta(days=30)
        if next_fecha > fecha_fin:
            next_fecha = fecha_fin

        for _, fila in metricas.iterrows():
            payload = {
                "MetricId": fila['MetricId'],
                "StartDate": fecha_inicio.strftime('%Y-%m-%d'),
                "EndDate": next_fecha.strftime('%Y-%m-%d'),
                "Entity": fila['Entity'],
                "Filter": [],
                "Url": fila['Url']  # Incluir la URL en el payload
            }
            payloads.append({
                "payload": payload,
                "url": fila['Url']  # url separada
            })

        fecha_inicio = next_fecha + timedelta(days=1)  # comenzar el siguiente día

    # Crear carpeta para guardar respuestas
    carpeta_respuestas = os.path.join(BASE_DIR, "respuestas_json")
    os.makedirs(carpeta_respuestas, exist_ok=True)

    # Guardar los payloads generados en subcarpetas
    for idx, item in enumerate(payloads):
        payload = item['payload']  # Acceder al diccionario de payload
        # Crear nombre de archivo basado en MetricId, Entity y fechas
        nombre_archivo = f"{payload['MetricId']}_{payload['Entity']}_{payload['StartDate']}_{payload['EndDate']}.json"
        # Limpiar el nombre del archivo (quitar caracteres raros)
        nombre_archivo = nombre_archivo.replace("/", "-")

        # Crear una subcarpeta para cada consulta, basada en MetricId y Entity
        subcarpeta = os.path.join(carpeta_respuestas, f"{payload['MetricId']}_{payload['Entity']}")
        os.makedirs(subcarpeta, exist_ok=True)

        # Asegurarse de que el archivo no sobrescriba uno existente
        ruta_archivo = os.path.join(subcarpeta, nombre_archivo)
        contador = 1
        while os.path.exists(ruta_archivo):
            nombre_archivo = f"{payload['MetricId']}_{payload['Entity']}_{payload['StartDate']}_{payload['EndDate']}_{contador}.json"
            ruta_archivo = os.path.join(subcarpeta, nombre_archivo)
            contador += 1

        # Guardar el payload en un archivo JSON
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)

        print(f"[{idx + 1}/{len(payloads)}] Guardado: {nombre_archivo}")

    return payloads

if __name__ == "__main__":
    payloads = generar_payloads()
    print(f"Se generaron {len(payloads)} payloads.")
