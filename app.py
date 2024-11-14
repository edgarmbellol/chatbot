from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import requests
import os
import json
from database import *

app = Flask(__name__)
app.secret_key = 'Sopo2024*'  # Cambia esto a algo más seguro en producción

# Carga las variables del archivo .env
load_dotenv()

# Cargar la configuración de botones desde el archivo JSON
with open("botones.json", "r") as file:
    botones = json.load(file)

# Cargar el archivo JSON con la lista de EPS
with open('eps_lista.json', 'r') as file:
    eps_data = json.load(file)

# Estado de los usuarios almacenado en memoria
client_states = {}

# Configura el token de acceso de la API de WhatsApp
VERIFY_TOKEN = "Sopo"  # Cambia esto por tu token de verificación
WHATSAPP_TOKEN = os.getenv("VERIFICATION_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/418920651309807/messages"  # Reemplaza {PHONE_NUMBER_ID} con el ID de tu número de WhatsApp Business
RECIPIENT_PHONE_NUMBER = "whatsapp:+573057499964"  # Número de teléfono del destinatario (formato E.164)

# Endpoint para recibir mensajes
@app.route('/webhook', methods=['POST','GET'])
def receive_message():
    if request.method == 'GET':
        # Verificación del webhook
        token = request.args.get('hub.verify_token')
        if token == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        else:
            return "Unauthorized", 403
    elif request.method == 'POST':
        # Mensaje recibido
        data = request.json
        # print("Mensaje recibido:", data)  # Imprime el mensaje completo para depuración

        # Verifica si el campo 'messages' está presente en los datos recibidos
        try:
            # OBTENER DATOS DEL USUARIO
            # Verificar tipo de mensaje
            datos_mensaje = verificar_tipo_mensaje(data)
            # Verificar en que estado se encuentra el numero qeu escribio
            if datos_mensaje['tipo_mensaje'] != "notificacion":
                # Establecer conexión con la base de datos
                db = conectar_base_datos()
            
                # Revisa en qué estado se encuentra el usuario que está escribiendo
                estado = consulta_estado_usuario(db, datos_mensaje['telefono'])
                
                # Estado inicial cuando se empieza la conversacion no tiene el telefono guardado en la base de datos
                if datos_mensaje['tipo_mensaje'] == "texto" and not estado:
                    # Ingresar datos para poner un estado al nuevo número
                    datos = {
                        "Telefono": datos_mensaje['telefono'],
                        "Nombre": datos_mensaje['nombre'],
                        "Estado": "bienvenido",
                    }
                    agregar_record_telefono(db, datos)
                    # Enviar mensaje de bienvenida
                    enviar_mensaje_botones("En qué te puedo ayudar?", "bienvenida")

                # Entra cuando se presiona el boton de AGENGAR CITA
                elif estado == "bienvenido" and datos_mensaje['mensaje_texto'] == "Agendar cita":
                    # Cambio de estado del usuario
                    datos = {
                        "Telefono": datos_mensaje['telefono'],
                        "Nombre": datos_mensaje['nombre'],
                        "Estado": "cedula citas",
                    }
                    agregar_record_telefono(db,datos)
                    # Enviar mensaje
                    mensaje = "Seleccionaste citas medicas. Por favor ingresa tu numero de cedula:"
                    enviar_mensaje_texto(mensaje)
                
                # Entra cuando se ingresa el numero de cedula de la persona luego de presionar el boton agendar cita
                elif estado == "cedula citas":
                    # Cambio de estado del usuario
                    # Agregar cedula a la base de datos
                    cedula = datos_mensaje["mensaje_texto"]
                    ingresar_dato_criterio(db,datos_mensaje['telefono'],"Cedula",cedula)
                    datos = {
                        "Telefono": datos_mensaje['telefono'],
                        "Nombre": datos_mensaje['nombre'],
                        "Estado": "eps citas"
                    }
                    agregar_record_telefono(db,datos)
                    # Enviar mensaje
                    # Crear la lista numerada de EPS
                    mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
                    for index, eps in enumerate(eps_data["eps"], start=1):
                        mensaje += f"{index}. {eps['nombre']}\n"
                    enviar_mensaje_texto(mensaje)
                
                # Entra cuando se selecciono eps a la que el usuario pertenece
                elif estado == "eps citas":
                    eps_seleccionada = verificar_eps_seleccionada(datos_mensaje["mensaje_texto"])
                    if eps_seleccionada == "error":
                        datos = {
                            "Telefono": datos_mensaje['telefono'],
                            "Nombre": datos_mensaje['nombre'],
                            "Estado": "cedula citas"
                        }
                        # Crear la lista numerada de EPS
                        enviar_mensaje_texto("Error al seleccionar EPS vuelve a intentarlo.")
                        mensaje = "Selecciona numero correspondiente a EPS por favor:\n"
                        for index, eps in enumerate(eps_data["eps"], start=1):
                            mensaje += f"{index}. {eps['nombre']}\n"
                        enviar_mensaje_texto(mensaje)
                    elif eps_seleccionada == "Otra":
                        # Seleccionar otra eps
                        enviar_mensaje_texto("Por favor escribe la EPS a la que perteneces")
                        datos = {
                            "Telefono": datos_mensaje['telefono'],
                            "Nombre": datos_mensaje['nombre'],
                            "Estado": "confirmacion citas"
                        }
                    else:
                        ingresar_dato_criterio(db,datos_mensaje['telefono'],"EPS",eps_seleccionada)
                        # Cambio de estado del usuario
                        datos = {
                            "Telefono": datos_mensaje['telefono'],
                            "Nombre": datos_mensaje['nombre'],
                            "Estado": "confirmacion citas"
                        }
                        # Enviar mensaje
                        mensaje = f"Los datos ingresados fueron. Cedula: *{tomar_registro(db,datos_mensaje['telefono'],"Cedula")}* con EPS: *{eps_seleccionada}* . Por favor selecciona si la información es correcta."
                        enviar_mensaje_botones("Verificacion","confirmacion",cuerpo=mensaje)
                    agregar_record_telefono(db,datos)

                # Entra cuando se selecciona una opcion de si o no a confirmacion citas
                elif estado == "confirmacion citas":
                    if datos_mensaje["mensaje_texto"] == "Si":
                        # Los datos ingresados por el usuario son correctos
                        # Proceso de verificacion de datos en la base de datos
                        pass
                    else:
                        # Los datos ingresados por el usuario son incorrectos
                        # Cambiar el estado para volver a pedir los datos
                        datos = {
                            "Telefono": datos_mensaje['telefono'],
                            "Nombre": datos_mensaje['nombre'],
                            "Estado": "bienvenido"
                        }
                        agregar_record_telefono(db, datos)
                        # Enviar mensaje de bienvenida
                        enviar_mensaje_botones("En qué te puedo ayudar?", "bienvenida")
 
                else: 
                    # Si ingresa aqui se selecciona una opcion no valida
                    datos = {
                            "Telefono": datos_mensaje['telefono'],
                            "Nombre": datos_mensaje['nombre'],
                            "Estado": "bienvenido"
                    }
                    agregar_record_telefono(db, datos)
                    # Enviar mensaje de bienvenida
                    enviar_mensaje_botones("Algo salio mal vuelve a intentar", "bienvenida")
                    

        except KeyError as e:
            print(f"Clave faltante en el JSON recibido: {e}")
            # Puedes agregar una respuesta o manejo adicional aquí si lo deseas

        return jsonify({"status": "success"}), 200


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
        


# Enviar mensaje con botones interactivos
def enviar_mensaje_botones(encabezado,botones_llave,cuerpo="Selecciona una opción:"):
    botones_seleccionados = botones.get(botones_llave, [])
    url = WHATSAPP_API_URL
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": encabezado
            },
            "body": {
                "text": cuerpo
            },
            "footer": {
                "text": "Hospital de Sesquile"
            },
            "action": {
                "buttons": botones_seleccionados
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Mensaje enviado con éxito.")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}")
        print(response.json())

# Enviar mensaje con texto plano
def enviar_mensaje_texto(encabezado):
    url = WHATSAPP_API_URL
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE_NUMBER,
        "type": "text",
        "text": {
            "body": encabezado
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Mensaje enviado con éxito.")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}")
        print(response.json())


# Función para definir el tipo de mensaje que llega
def verificar_tipo_mensaje(data):
    # Inicialización de variables
    tipo_mensaje = ""
    nombre = ""
    telefono = ""
    mensaje_texto = ""
    
    # Verificar si es un mensaje enviado por el usuario
    if 'messages' in data['entry'][0]['changes'][0]['value']:
        for mensaje in data['entry'][0]['changes'][0]['value']['messages']:
            # Mensaje de texto
            if mensaje.get('type') == 'text':
                mensaje_texto = mensaje['text']['body']
                telefono = mensaje['from']
                
                # Obtener el nombre del contacto o "Usuario" si no existe
                contacto = data['entry'][0]['changes'][0]['value']['contacts'][0]
                nombre = contacto['profile'].get('name', 'Usuario')
                
                tipo_mensaje = "texto"
            
            # Mensaje interactivo (botón seleccionado)
            elif mensaje.get('type') == 'interactive' and mensaje['interactive'].get('type') == 'button_reply':
                # Extraer el título del botón seleccionado
                mensaje_texto = mensaje['interactive']['button_reply']['title']
                telefono = mensaje['from']
                
                # Obtener el nombre del contacto o "Usuario" si no existe
                contacto = data['entry'][0]['changes'][0]['value']['contacts'][0]
                nombre = contacto['profile'].get('name', 'Usuario')
                
                tipo_mensaje = "interactivo"
                
    # Verificar si es una notificación de estado
    elif 'statuses' in data['entry'][0]['changes'][0]['value']:
        for status in data['entry'][0]['changes'][0]['value']['statuses']:
            if status.get('status') in ['delivered', 'read', 'sent']:
                tipo_mensaje = "notificacion"
                # Nombre, teléfono y mensaje_texto quedan vacíos

    return {
        "tipo_mensaje": tipo_mensaje,
        "nombre": nombre,
        "telefono": telefono,
        "mensaje_texto": mensaje_texto
    }



if __name__ == '__main__':
    app.run(debug=True)
