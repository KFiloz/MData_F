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

# Función para obtener los últimos 4 datos de DynamoDB
def get_latest_data(limit=4):
    try:
        response = table.scan()
        data = response['Items']

        for item in data:
            if 'timestamp' in item:
                try:
                    item['timestamp'] = int(item['timestamp'])
                except ValueError:
                    item['timestamp'] = 0

        data = sorted(data, key=lambda x: x.get('timestamp', 0), reverse=True)
        return data[:limit]
    except Exception as e:
        st.error(f"Error al obtener datos de AWS: {e}")
        return []

# Función para crear un mapa interactivo
def create_map(data):
    m = folium.Map(location=[10.987103, -74.790072], zoom_start=10)

    for item in data:
        lat = float(item.get('Latitud', 0))
        lon = float(item.get('Longitud', 0))
        temp = item.get('Temperatura', 'N/A')
        batt = item.get('Bateria', 'N/A')
        status = item.get('Status', 'Desconocido')

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(f"""
                <b>Temperatura:</b> {temp}°C<br>
                <b>Batería:</b> {batt}%<br>
                <b>Status:</b> {status}
            """, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    return m

# Interfaz de Streamlit
st.title("Mapa de Dispositivos IoT - Card Tracker")
st.write("Recarga la página para actualizar los datos más recientes.")

# Mostrar los últimos datos y el mapa
st.subheader("Últimos 4 Datos recibidos")
latest_data = get_latest_data(limit=4)
st.write(latest_data)

st.subheader("Mapa Interactivo")
mapa = create_map(latest_data)
st_folium(mapa, width=700, height=500)

