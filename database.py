from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from dotenv import load_dotenv
import datetime

# Carga las variables del archivo .env
load_dotenv()

# Define la cadena de conexión
connection_string = "mongodb://localhost:27017"

try:
    # Crea una instancia del cliente y se conecta a MongoDB
    client = MongoClient(connection_string)
    
    # Accede a la base de datos para forzar la conexión
    db = client["chat_bot"]
    print(db)

    # Accede a la colección dentro de la base de datos
    collection = db["estados_usuarios"]
    
    # Realiza una operación simple para verificar la conexión
    db.command("ping")
    
    # Si llega aquí, la conexión fue exitosa
    print("Conexión a la base de datos establecida correctamente.")
    
except ConnectionError:
    print("Error: No se pudo conectar a la base de datos.")

def agregar_record(data):
    record = {
        "id": data.get("id"),
        "Telefono_1": data.get("Telefono_1"),
        "Nombre_1": data.get("Nombre_1"),
        "Estado_1": data.get("Estado_1"),
        "Historial_1": data.get("Historial_1", {"fecha": str(datetime.datetime.now()), "mensaje": ""}),
        "UltimoMensaje": data.get("UltimoMensaje")
    }
    result = collection.insert_one(record)
    print(f"Registro agregado con ID: {str(result.inserted_id)}")

# Datos que deseas insertar
data = {
    "id": 2,
    "Telefono_1": "12345678789",
    "Nombre_1": "Juan",
    "Estado_1": "Activo",
    "Historial_1": {"fecha": "2024-11-01", "mensaje": "Mensaje inicial"},
    "UltimoMensaje": "Mensaje de prueba"
}

# Llamada a la función para insertar el registro
agregar_record(data)