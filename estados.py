from database import *
from enviar_mensaje import * 
import json
from interfaz_citisalud import database_citi as hospital

# Cargar el archivo JSON con la lista de EPS
with open('eps_lista.json', 'r') as file:
    eps_data = json.load(file)

def bienvenida(db,telefono,nombre):
    estado = "bienvenido"
    datos = {
                "Telefono": telefono,
                "Nombre": nombre,
                "Estado": estado
            }
    agregar_record_telefono(db,datos)
    enviar_mensaje_botones("En qué te puedo ayudar?", "bienvenida")
    return

def cedula_citas(db,telefono):
    estado = "cedula citas"
    captura_error = actualizar_estado(db,telefono,estado)

    # Enviar mensaje
    mensaje = "Seleccionaste citas medicas. Por favor ingresa tu numero de cedula:"
    enviar_mensaje_texto(mensaje)
    return

def eps_citas(db,telefono,cedula):
    ingresar_dato_criterio(db,telefono,"Cedula",cedula)
    estado = "eps citas"
    captura_error = actualizar_estado(db,telefono,estado)

    # Crear la lista numerada de EPS
    mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
    for index, eps in enumerate(eps_data["eps"], start=1):
        mensaje += f"{index}. {eps['nombre']}\n"
    enviar_mensaje_texto(mensaje)
    return

def confirmacion_informacion(db,telefono,nombre,mensaje):

    # Verificar EPS seleccionada
    eps_seleccionada = verificar_eps_seleccionada(mensaje)

    if eps_seleccionada == "error":
        # Actualice el estado y vuelva a enviar el mensaje
        enviar_mensaje_texto("Error al seleccionar EPS vuelve a intentarlo.")
        estado = "cedula citas"
        # Crear la lista numerada de EPS
        mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
        for index, eps in enumerate(eps_data["eps"], start=1):
            mensaje += f"{index}. {eps['nombre']}\n"
        enviar_mensaje_texto(mensaje)
    else:
        ingresar_dato_criterio(db,telefono,"EPS",eps_seleccionada)
        mensaje = f"Los datos ingresados fueron. Cedula: *{tomar_registro(db,telefono,"Cedula")}* con EPS: *{eps_seleccionada}* . Por favor selecciona si la información es correcta."
        enviar_mensaje_botones("Verificacion","confirmacion",cuerpo=mensaje)
        estado = "confirmacion informacion"
    actualizar_estado(db,telefono,estado)

    return

def datos_incorrectos(db,telefono):
    estado = "bienvenido"
    captura_error = actualizar_estado(db,telefono,estado)
    # Enviar mensaje
    enviar_mensaje_botones("En qué te puedo ayudar?", "bienvenida") 


# verificar que eps selecciono el usuario
def verificar_eps_seleccionada(mensaje):
# Verifica si el mensaje es un número y corresponde a una EPS
    try:
        seleccion = int(mensaje)
        if 1 <= seleccion <= len(eps_data["eps"]):
            eps_seleccionada = eps_data["eps"][seleccion - 1]["nombre"]
            print(f"El usuario seleccionó la EPS: {eps_seleccionada}")

            # Aquí puedes responder al usuario o procesar la selección
            return eps_seleccionada
        else:
            return "error"
    except ValueError:
        print("Mensaje no válido. No es un número.")
        return "error"
    
def verificar_paciente(db,telefono):
    # Verificacion de datos en base de datos
    cedula = tomar_registro(db,telefono,"Cedula")
    usuario = hospital.paciente_por_cedula(cedula)
    if not usuario:
        # Entra si la lista esta vacia
        return "lista vacia"
    else:
        # Encontro usuario en la base de datos
        nombre = hospital.tomar_nombre_usuario(usuario)
        # guarda el nombre en mongoDB
        ingresar_dato_criterio(db,telefono,"Nombre",nombre)
        mensaje = f"El numero de cedula: *{tomar_registro(db,telefono,"Cedula")}* corresponde al usuario con nombre: *{nombre}*. Indicanos si es verdadero"
        enviar_mensaje_botones("Verificacion","confirmacion",cuerpo=mensaje)
        estado = "verificar usuario citas"
        actualizar_estado(db,telefono,estado)

