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
        # Escanear la tabla
        response = table.scan()
        data = response['Items']

        # Convertir todos los valores de "timestamp" a un tipo consistente (int)
        for item in data:
            if 'timestamp' in item:
                # Intentar convertir el valor a int, si no es posible, usar un valor por defecto
                try:
                    item['timestamp'] = int(item['timestamp'])
                except ValueError:
                    item['timestamp'] = 0  # Asignar 0 si no se puede convertir

        # Ordenar los datos por el campo "timestamp"
        data = sorted(data, key=lambda x: x.get('timestamp', 0), reverse=True)

        # Tomar solo los últimos "limit" elementos
        return data[:limit]
    except Exception as e:
        st.error(f"Error al obtener datos de DynamoDB: {e}")
        return []

# Función para crear un mapa interactivo
def create_map(data):
    # Crear un mapa centrado en una ubicación inicial
    m = folium.Map(location=[10.987103, -74.790072], zoom_start=10)

    # Agregar marcadores al mapa
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
st.title("Mapa de Dispositivos IoT - DynamoDB")
st.write("Esta aplicación muestra los últimos datos de los dispositivos conectados.")

# Obtener y mostrar los últimos datos
st.subheader("Últimos 4 Datos de DynamoDB")
latest_data = get_latest_data(limit=4)
st.write(latest_data)  # Mostrar datos en tabla

# Crear y mostrar el mapa con los últimos datos
st.subheader("Mapa Interactivo")
mapa = create_map(latest_data)
st_folium(mapa, width=700, height=500)
