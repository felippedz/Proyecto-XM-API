import os
import json
import mysql.connector
import pandas as pd
from mysql.connector import Error

# Configuración de la DB
db_config = {
    "host": "localhost",
    "port": 3307,
    "user": "xm_user",
    "password": "xm_password",
    "database": "xm_data",
    "ssl_disabled": True
}

def conectar_db():
    return mysql.connector.connect(**db_config)

def obtener_metric_ids(cursor):
    """
    Obtiene todos los metric_id existentes en la base de datos para evitar consultas repetitivas.
    Devuelve un diccionario con metric_id como clave y id como valor.
    """
    cursor.execute("SELECT metric_id, id FROM metrics")
    return {metric_id: id for metric_id, id in cursor.fetchall()}

def insertar_datos(cursor, metric, items, metric_id_map):
    # Comprobar si ya existe el metric_id en el diccionario de metric_id_map
    if metric["Id"] in metric_id_map:
        metric_id_fk = metric_id_map[metric["Id"]]
    else:
        cursor.execute("""
            INSERT INTO metrics (metric_id, name, start_date, end_date)
            VALUES (%s, %s, %s, %s)
        """, (metric["Id"], metric["Name"], metric["StartDate"][:10], metric["EndDate"][:10]))
        metric_id_fk = cursor.lastrowid
        metric_id_map[metric["Id"]] = metric_id_fk  # Guardamos el nuevo id en el mapa


    # Insertar en tabla metric_values
    insert_query = """
        INSERT INTO metric_values (metric_id_fk, date, entity_id, value)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE value=VALUES(value)  # Evita duplicados
    """
    
    for item in items:
        if "Entities" in item:  # Procesar solo las entidades (sin DailyEntities)
            for entity in item["Entities"]:
                entity_id = entity.get("Id", None)
                value = entity.get("Value", None)
                date = item["Date"]

                # Asegúrate de que los valores no sean nulos ni vacíos
                if entity_id is not None and value is not None and date is not None:
                    print(f"Insertando: metric_id_fk={metric_id_fk}, date={date}, entity_id={entity_id}, value={value}")
                    cursor.execute(insert_query, (
                        metric_id_fk,
                        date,
                        entity_id,
                        float(value)  # Convertir el valor a float para asegurar que se inserte correctamente
                    ))
                else:
                    print(f"⚠️ Datos faltantes para la fecha {date}, entidad {entity_id}: value={value}")

def leer_e_insertar():
    base_path = os.path.join("respuestas_json")

    if not os.path.isdir(base_path):
        print("❌ Carpeta 'respuestas_json' no encontrada.")
        return

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Obtener todos los metric_id existentes para evitar consultas repetidas
        metric_id_map = obtener_metric_ids(cursor)

        for carpeta in os.listdir(base_path):
            carpeta_path = os.path.join(base_path, carpeta)

            if os.path.isdir(carpeta_path):
                for subcarpeta in os.listdir(carpeta_path):
                    sub_path = os.path.join(carpeta_path, subcarpeta)
                    if os.path.isdir(sub_path):
                        for archivo in os.listdir(sub_path):
                            if archivo.endswith("_respuesta.json"):
                                ruta_json = os.path.join(sub_path, archivo)
                                with open(ruta_json, "r", encoding="utf-8") as f:
                                    data = json.load(f)

                                if "Metric" in data and "Items" in data:
                                    insertar_datos(cursor, data["Metric"], data["Items"], metric_id_map)
                                    print(f"✅ Insertado: {archivo}")
                                else:
                                    print(f"⚠️ Estructura inválida en: {archivo}")

        conn.commit()

        # Mostrar datos
        df_metrics = pd.read_sql("SELECT * FROM metrics", conn)
        print("\n📊 Tabla 'metrics':\n", df_metrics)

        df_values = pd.read_sql("SELECT * FROM metric_values", conn)
        print("\n📊 Tabla 'metric_values':\n", df_values)

    except Error as e:
        print("❌ Error con la base de datos:", e)

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Conexión cerrada.")
            print("✅ Proceso de inserción completado.")

if __name__ == "__main__":
    leer_e_insertar()
