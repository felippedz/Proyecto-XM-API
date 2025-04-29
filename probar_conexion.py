import mysql.connector
from mysql.connector import Error

try:
    conexion = mysql.connector.connect(
        host='localhost',    # Nos conectamos a nuestra máquina
        port=3307,           # Puerto que mapeaste en docker-compose
        user='xm_user',      # Usuario definido en tu docker-compose
        password='xm_password',  # Contraseña definida
        database='xm_data',      # Base de datos definida
        ssl_disabled=True        # No usar SSL
    )

    if conexion.is_connected():
        print('✅ Conexión exitosa a la base de datos xm_data')
        print('Información del servidor:', conexion.get_server_info())

except Error as e:
    print('❌ Error de conexión:', e)

finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        print('🔌 Conexión cerrada.')
