import os
import json
import requests

# Función para leer el JSON y realizar la consulta a la API
def consultar_api_desde_json(ruta_json):
    # Leer el archivo JSON
    with open(ruta_json, 'r', encoding='utf-8') as file:
        datos = json.load(file)
    
    # Extraer la URL y los parámetros necesarios
    url = datos['Url']
    payload = {
        "MetricId": datos['MetricId'],
        "StartDate": datos['StartDate'],
        "EndDate": datos['EndDate'],
        "Entity": datos['Entity'],
        "Filter": datos['Filter']
    }
    
    # Realizar la solicitud POST a la API
    try:
        print(f"Realizando consulta a: {url}")
        response = requests.post(url, json=payload)

        # Verificar si la consulta fue exitosa
        if response.status_code == 200:
            print(f"✅ Consulta exitosa a {url}!")
            # Obtener la ruta de la carpeta donde se encuentra el archivo JSON
            carpeta_respuesta = os.path.dirname(ruta_json)
            
            # Crear subcarpeta para las fechas (StartDate - EndDate)
            fecha_subcarpeta = f"{datos['StartDate']}_{datos['EndDate']}"
            carpeta_fecha = os.path.join(carpeta_respuesta, fecha_subcarpeta)
            os.makedirs(carpeta_fecha, exist_ok=True)

            # Guardar la respuesta en un archivo JSON dentro de la subcarpeta de fechas
            ruta_respuesta = os.path.join(carpeta_fecha, f"{datos['MetricId']}_{datos['Entity']}_{datos['StartDate']}_{datos['EndDate']}_respuesta.json")
            with open(ruta_respuesta, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=4)
            print(f"Respuesta guardada en: {ruta_respuesta}")
        else:
            print(f"❌ Error al consultar la API. Código de estado: {response.status_code} para {url}")
    
    except Exception as e:
        print(f"⚠️ Excepción al realizar la consulta: {e}")

if __name__ == "__main__":
    # Establecer un límite de 5 consultas para probar
    contador = 0
    max_consultas = 505
    
    # Ruta del archivo JSON que contiene la consulta
    carpeta_respuestas = "respuestas_json"
    
    # Recorrer las subcarpetas dentro de respuestas_json y limitar a 5 consultas
    for subcarpeta in os.listdir(carpeta_respuestas):
        if contador >= max_consultas:
            break
        
        subcarpeta_path = os.path.join(carpeta_respuestas, subcarpeta)
        
        if os.path.isdir(subcarpeta_path):
            for archivo in os.listdir(subcarpeta_path):
                if archivo.endswith(".json"):
                    ruta_json = os.path.join(subcarpeta_path, archivo)
                    print(f"\nConsultando: {ruta_json}")
                    consultar_api_desde_json(ruta_json)
                    contador += 1
                    if contador >= max_consultas:
                        break
