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


# Agrega un nuevo registro si no encuentra el numero de telefono si no lo actualiza
def agregar_record_telefono(db,data):
    collection = db["estado_usuarios"]
    filtro = {"Telefono": data.get("Telefono")}  # Buscar por Telefono
    nuevo_valor = {
        "$set": {
            "Nombre": data.get("Nombre"),
            "Estado": data.get("Estado"),
        }
    }

    result = collection.update_one(filtro, nuevo_valor, upsert=True)

    if result.matched_count > 0:
        print("Estado actualizado para el teléfono existente.")
    else:
        print("Registro agregado como nuevo.")

def ingresar_dato_criterio(db,telefono,criterio,cedula):
        # Actualizar el campo 'cedula' en el documento que coincide con el teléfono
        resultado = db["estado_usuarios"].update_one(
            {"Telefono": telefono},
            {"$set": {criterio: cedula}}
    )

def tomar_registro(db, telefono, criterio):
    # Buscar el documento que coincide con el número de teléfono y obtener solo el campo especificado
    dato = db["estado_usuarios"].find_one({"Telefono": telefono}, {criterio: 1})
    
    # Verificar si se encontró el documento y si el criterio está presente
    if dato and criterio in dato:
        return dato[criterio]
    else:
        return f"No se encontró el criterio '{criterio}' para el teléfono dado" if dato else "Usuario no encontrado"


# Consulta de registros en la base de datos
def consulta_estado_usuario(db,numero_telefono):
    estados = db["estado_usuarios"]

    # Consulta en la base de datos a través de un número de teléfono
    filtro = {"Telefono": numero_telefono}

    # Campos que se van a traer de la consulta
    proyeccion = {"Estado": 1}

    # Resultado de la consulta
    resultado = estados.find_one(filtro, proyeccion)
    print(resultado)

    # Si se encontró un resultado y tiene el campo "Estado", devuelve su valor
    if resultado and "Estado" in resultado:
        return resultado["Estado"]
    
    # Si no se encuentra el resultado, devuelve una lista vacía
    return []

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
# print(consulta_estado_usuario("12345678789"))
# print(consulta_todos_registros())