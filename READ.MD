# Manual de Uso: Sistema de Consulta y Almacenamiento de Métricas XM

---

## 📂 Descripción General

Este sistema permite generar payloads a partir de un archivo Excel, realizar consultas a la API pública de XM, almacenar las respuestas en formato JSON organizadas por métricas y fechas, y finalmente insertar los resultados en una base de datos relacional MariaDB.

---

## 📁 Estructura del Proyecto

```
tu_proyecto/
│
├── datos/
│   └── datos_API (1).xlsx          ← Archivo Excel con métricas
│
├── respuestas_json/                ← Se crean automáticamente al generar payloads y respuestas
│   └── {MetricId}_{Entity}/
│       └── {StartDate}_{EndDate}/
│           └── response.json       ← Respuesta de la API
│
├── scripts/
│   ├── generar_payloads.py         ← Genera payloads a partir del Excel
│   ├── consultar_api.py            ← Consulta la API con los payloads JSON
│   └── insertar_mariadb.py         ← Inserta datos procesados en la base de datos
│
├── .env / config.py (opcional)     ← Credenciales si deseas separar configuración
└── README.md                       ← Manual de uso
```

---

## 📋 Requisitos

- Python 3.9 o superior
- MariaDB (o MySQL compatible)
- Paquetes Python:
  ```bash
  pip install pandas openpyxl requests mysql-connector-python
  ```

---

## ⚙️ Configuración de la Base de Datos

Crea la base de datos y tabla `metric_results` con esta estructura:

```sql
CREATE DATABASE xm_data;

USE xm_data;

CREATE TABLE metric_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    MetricId VARCHAR(100),
    Entity VARCHAR(100),
    StartDate DATE,
    EndDate DATE,
    Result JSON,
    UNIQUE KEY uniq_metric (MetricId, Entity, StartDate, EndDate)
);
```

Configura el acceso a la base de datos en `insertar_mariadb.py`:

```python
db_config = {
    "host": "localhost",
    "port": 3307,
    "user": "xm_user",
    "password": "xm_password",
    "database": "xm_data",
    "ssl_disabled": True
}
```

---

## 🚀 Ejecución del Programa

### 1. Generar Payloads desde el archivo Excel

```bash
cd scripts/
python generar_payloads.py
```

- Crea archivos `.json` en la carpeta `respuestas_json/`, organizados por métrica y entidad.

---

### 2. Realizar consultas a la API usando los payloads

```bash
python consultar_api.py
```

- Realiza POSTs a la API usando los payloads generados.
- Guarda cada respuesta como `response.json` en subcarpetas por fecha.
- Límite predeterminado: 50 consultas (modificable en el script).

---

### 3. Insertar datos en la base de datos MariaDB

```bash
python insertar_mariadb.py
```

- Lee cada archivo `response.json`.
- Inserta el contenido como JSON en `metric_results` si no existe previamente.

---

## 📌 Observaciones

- Los JSON de entrada deben tener la clave `"Url"` para que `consultar_api.py` funcione.
- Las respuestas deben seguir el formato que contenga `MetricId`, `Entity`, `StartDate`, `EndDate` y `Items`.
- Si deseas hacer análisis más profundos, puedes normalizar los datos en tablas adicionales (`metric_values`, por ejemplo).
- Los scripts imprimen en consola el estado de la ejecución para facilitar el seguimiento.
