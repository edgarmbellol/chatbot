from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from dotenv import load_dotenv
import datetime

# Carga las variables del archivo .env
load_dotenv()

# Función para conectarse a la base de datos
def conectar_base_datos(uri="mongodb://localhost:27017/", db_name="chat_bot"):
    try:
        # Crear una instancia de cliente MongoDB
        client = MongoClient(uri)
        
        # Obtener la base de datos
        db = client[db_name]
        
        # Verificar si la conexión fue exitosa
        print(f"Conexión exitosa a la base de datos: {db_name}")
        
        # Retornar la base de datos para realizar consultas
        return db
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None

# Agregar un n uevo registro a la base de datos
def agregar_record(db,data):
    collection = db["estados_usuarios"]
    record = {
        "id": data.get("id"),
        "Telefono": data.get("Telefono"),
        "Nombre": data.get("Nombre"),
        "Estado": data.get("Estado"),
        "Historial": data.get("Historial", {"fecha": str(datetime.datetime.now()), "mensaje": ""}),
        "UltimoMensaje": data.get("UltimoMensaje")
    }
    result = collection.insert_one(record)
    print(f"Registro agregado con ID: {str(result.inserted_id)}")

# Consulta de registros en la base de datos
def consulta_record(db,numero_telefono):
    estados = db["estado_usuarios"]

    # Consulta en la base de datos a través de un número de teléfono
    filtro = {"Telefono": numero_telefono}

    # Campos que se van a traer de la consulta
    proyeccion = {"Estado": 1}

    # Resultado de la consulta
    resultado = estados.find_one(filtro, proyeccion)

    # Si se encontró un resultado y tiene el campo "Estado", devuelve su valor
    if resultado and "Estado" in resultado:
        return resultado["Estado"]
    
    # Si no se encuentra el resultado, devuelve una lista vacía
    return []


# Actualzia el estado del numero de telefono
def actualizar_estado(db,numero_telefono, nuevo_estado, mensaje=""):
    estados = db["estado_usuarios"]
    # Buscar el documento del teléfono
    documento = estados.find_one({"Telefono": numero_telefono})

    if documento:
        # Si existe, actualizamos el estado y agregamos el nuevo mensaje al historial
        estados.update_one(
            {"Telefono": numero_telefono},
            {
                "$set": {"Estado": nuevo_estado},  # Actualiza el estado
                "$push": {"Historial": {"fecha": "2024-11-11T10:00:00", "mensaje": mensaje}}  # Agrega el mensaje
            }
        )
    else:
        # Si no existe, crear un nuevo documento para el teléfono
        estados.insert_one({
            "Telefono": numero_telefono,
            "Estado": nuevo_estado,
            "UltimoMensaje": mensaje,
            "Historial": [{"fecha": "2024-11-11T10:00:00", "mensaje": mensaje}]
        })



# Datos que deseas insertar
data = {
    "id": 2,
    "Telefono": "12345678789",
    "Nombre": "Juan",
    "Estado": "Activo",
    "Historial": {"fecha": "2024-11-01", "mensaje": "Mensaje inicial"},
    "UltimoMensaje": "Mensaje de prueba"
}

# Llamada a la función para insertar el registro
# agregar_record(data)

# Realizar una consulta
print(consulta_record("12345678789"))
# print(consulta_todos_registros())