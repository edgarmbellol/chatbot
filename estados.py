from database import *
from enviar_mensaje import * 
import json
# from interfaz_citisalud import database_citi as hospital
from interfaz_CNT import database_citi as hospital

# Cargar el archivo JSON con la lista de EPS
with open('eps_lista.json', 'r') as file:
    eps_data = json.load(file)


# Cargar el archivo JSON con la lista de EPS
with open('especialidad_lista.json', 'r') as file:
    especialidad_data = json.load(file)

def bienvenida(db,telefono,nombre):
    estado = "bienvenido"
    datos = {
                "Telefono": telefono,
                "Nombre": nombre,
                "Estado": estado
            }
    agregar_record_telefono(db,datos)
    enviar_mensaje_botones(telefono,"En qué te puedo ayudar?", "bienvenida")
    return

def cedula_citas(db,telefono):
    estado = "cedula citas"
    captura_error = actualizar_estado(db,telefono,estado)

    # Enviar mensaje
    mensaje = "Seleccionaste citas medicas. Por favor ingresa tu numero de cedula:"
    enviar_mensaje_texto(telefono,mensaje)
    return


def eps_citas(db,telefono,cedula):
    ingresar_dato_criterio(db,telefono,"Cedula",cedula)
    estado = "eps citas"
    captura_error = actualizar_estado(db,telefono,estado)

    # Crear la lista numerada de EPS
    mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
    for index, eps in enumerate(eps_data["eps"], start=1):
        mensaje += f"{index}. {eps['nombre']}\n"
    enviar_mensaje_texto(telefono,mensaje)
    return

def confirmacion_informacion(db,telefono,nombre,mensaje):

    # Verificar EPS seleccionada
    eps_seleccionada = verificar_eps_seleccionada(mensaje)

    if eps_seleccionada == "error":
        # Actualice el estado y vuelva a enviar el mensaje
        enviar_mensaje_texto(telefono,"Error al seleccionar EPS vuelve a intentarlo.")
        estado = "cedula citas"
        # Crear la lista numerada de EPS
        mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
        for index, eps in enumerate(eps_data["eps"], start=1):
            mensaje += f"{index}. {eps['nombre']}\n"
        enviar_mensaje_texto(telefono,mensaje)
    else:
        ingresar_dato_criterio(db,telefono,"EPS",eps_seleccionada)
        mensaje = f"Los datos ingresados fueron. Cedula: *{tomar_registro(db,telefono,"Cedula")}* con EPS: *{eps_seleccionada}* . Por favor selecciona si la información es correcta."
        enviar_mensaje_botones(telefono,"Verificacion","confirmacion",cuerpo=mensaje)
        estado = "confirmacion informacion"
    actualizar_estado(db,telefono,estado)

    return

def datos_incorrectos(db,telefono):
    estado = "bienvenido"
    captura_error = actualizar_estado(db,telefono,estado)
    # Enviar mensaje
    enviar_mensaje_botones(telefono,"En qué te puedo ayudar?", "bienvenida") 

    
def verificar_paciente(db,telefono):
    # Verificacion de datos en base de datos
    cedula = tomar_registro(db,telefono,"Cedula")
    usuario = hospital.paciente_por_cedula(cedula)
    if not usuario:
        # Entra si la lista esta vacia
        mensaje = f"Disculpa no encontramos el numero de cedula: *{cedula}* en nuestro sistema, por favor acercate a las instalaciones para poder registrar tus datos"
        enviar_mensaje_texto(telefono,mensaje)
        actualizar_estado(db,telefono,"bienvenido")
        return "lista vacia"
    else:
        # Encontro usuario en la base de datos
        nombre = hospital.tomar_nombre_usuario(usuario)
        # guarda el nombre en mongoDB
        ingresar_dato_criterio(db,telefono,"Nombre",nombre)
        mensaje = f"El numero de cedula: *{tomar_registro(db,telefono,"Cedula")}* corresponde al usuario con nombre: *{nombre}*. Indicanos si es verdadero"
        enviar_mensaje_botones(telefono,"Verificacion","confirmacion",cuerpo=mensaje)
        estado = "verificar usuario citas"
        actualizar_estado(db,telefono,estado)

def seleccionar_especialidad(db,telefono):
    estado = "seleccionar especialidad"
    actualizar_estado(db,telefono,estado)
    mensaje = "Selecciona la especialidad en la que deseas agendar la cita por favor:\n"
    for index, especialidad in enumerate(especialidad_data["especialidades"], start=1):
        mensaje += f"{index}. {especialidad['nombre']}\n"
    enviar_mensaje_texto(telefono,mensaje)

def confirmar_especialidad(db,telefono,mensaje):
    especialidad = verificar_especialidad(mensaje)
    if especialidad == "error":
        # Actualice el estado y vuelva a enviar el mensaje
        enviar_mensaje_texto(telefono,"Error al seleccionar especidalidad vuelve a intentarlo.")
        estado = "verificar usuario citas"
        # Crear la lista numerada de especialidades
        mensaje = "Selecciona la especialidad en la que deseas agendar la cita por favor:\n"
        for index, especialidad in enumerate(especialidad_data["especialidades"], start=1):
            mensaje += f"{index}. {especialidad['nombre']}\n"
        enviar_mensaje_texto(telefono,mensaje)
    else:
        ingresar_dato_criterio(db,telefono,"Especialidad",especialidad)
        mensaje = f"La especialidad seleccionada fue *{especialidad}*.Por favor has clic en el siguiente enlace para verificar agenda"
        enviar_mensaje_texto(telefono,mensaje)
        estado="pagina web"
        # Se envia link para abrir pagina web con datos ingresados

    actualizar_estado(db,telefono,estado)
    


# FUNCIONES QUE SE USAN DENTRO DEL PROGRAMA
# -----------------------------------------------------------
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
    
# verificar que eps selecciono el usuario
def verificar_especialidad(mensaje):
# Verifica si el mensaje es un número y corresponde a una EPS
    try:
        seleccion = int(mensaje)
        if 1 <= seleccion <= len(especialidad_data["especialidades"]):
            especialidad = especialidad_data["especialidades"][seleccion - 1]["nombre"]
            print(f"El usuario seleccionó la Especialidad: {especialidad}")

            # Aquí puedes responder al usuario o procesar la selección
            return especialidad
        else:
            return "error"
    except ValueError:
        print("Mensaje no válido. No es un número.")
        return "error"
