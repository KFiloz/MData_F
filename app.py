import os
import boto3
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()

# Leer las credenciales de las variables de entorno
aws_access_key_id = os.getenv('ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('SECRET_ACCESS_KEY')

# Configurar la conexión a DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'  # Cambia si tu región es diferente
)
table = dynamodb.Table('bd-lorawan')

# Mapeo de EUIs a nombres de dispositivos
DEVICE_MAP = {
    "2cf7f1c062700219": "Dispositivo 1",
    "2cf7f1c06270023c": "Dispositivo 2"
}

# Lista de dispositivos que queremos filtrar
TARGET_DEVICES = list(DEVICE_MAP.keys())

# Función para obtener los últimos datos de los dispositivos específicos
def get_latest_data_by_device(devices):
    try:
        # Consultar todos los datos de la tabla DynamoDB
        response = table.scan()
        data = response['Items']

        # Filtrar los datos por dispositivo y obtener el último dato basado en timestamp_unix_ms
        filtered_data = {}
        for item in data:
            device_eui = item.get("device_id")
            timestamp = item.get("timestamp_unix_ms")
            
            # Validar si el dato corresponde al dispositivo que estamos monitoreando
            if device_eui in devices:
                if device_eui not in filtered_data or (timestamp and timestamp > filtered_data[device_eui].get("timestamp_unix_ms", 0)):
                    filtered_data[device_eui] = item

        # Retornar los datos más recientes de cada dispositivo
        return list(filtered_data.values())
    except Exception as e:
        st.error(f"Error al obtener datos de AWS: {e}")
        return []

# Función para crear un mapa interactivo
def create_map(data):
    # Ubicación inicial del mapa
    m = folium.Map(location=[10.987103, -74.790072], zoom_start=10)

    for item in data:
        lat = float(item.get('latitud', 0))
        lon = float(item.get('longitud', 0))
        temp = item.get('temperatura', 'N/A')
        batt = item.get('bateria', 'N/A')
        eui = item.get('device_id', 'Desconocido')

        # Obtener el nombre del dispositivo a partir del mapeo
        device_name = DEVICE_MAP.get(eui, "Desconocido")

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(f"""
                <b>Dispositivo:</b> {device_name}<br>
                <b>Temperatura:</b> {temp}°C<br>
                <b>Batería:</b> {batt}%<br>
            """, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    return m

# Interfaz de Streamlit
st.title("Mapa de Dispositivos IoT - Card Tracker")
st.write("Recarga la página para actualizar los datos más recientes.")

# Obtener y mostrar los últimos datos de los dispositivos específicos
st.subheader("Datos de los Dispositivos")
latest_data = get_latest_data_by_device(TARGET_DEVICES)
st.write(latest_data)

# Crear y mostrar el mapa interactivo
st.subheader("Mapa Interactivo")
mapa = create_map(latest_data)
st_folium(mapa, width=700, height=500)
