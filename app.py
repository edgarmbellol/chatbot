from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
import json
from database import *

app = Flask(__name__)

# Carga las variables del archivo .env
load_dotenv()

# Cargar la configuración de botones desde el archivo JSON
with open("botones.json", "r") as file:
    botones = json.load(file)

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
# Endpoint para recibir mensajes
@app.route('/webhook', methods=['POST'])
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
        print("Mensaje recibido:", data)  # Imprime el mensaje completo para depuración

        # Verifica si el campo 'messages' está presente en los datos recibidos
        try:
            # OBTENER DATOS DEL USUARIO

            tipo_mensaje = "texto"
            telefono = ""
            nombre = ""
            # Verificar le tipo de mensaje entrante
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                # Este es un mensaje enviado por el usuario
                for mensaje in data['entry'][0]['changes'][0]['value']['messages']:
                    if mensaje.get('type') == 'text':
                        # Procesa el mensaje de texto del usuario
                        mensaje_texto = mensaje['text']['body']

                        # Número de teléfono del contacto
                        telefono = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                        # Obtener el nombre del contacto o "Usuario" si no existe
                        contacto = data['entry'][0]['changes'][0]['value']['contacts'][0]
                        nombre = contacto['profile'].get('name', 'Usuario')

            elif 'statuses' in data['entry'][0]['changes'][0]['value']:
                # Este es un mensaje de confirmación de estado
                for status in data['entry'][0]['changes'][0]['value']['statuses']:
                    if status.get('status') in ['delivered', 'read', 'sent']:
                        # Procesa el estado del mensaje
                        print("Estado del mensaje:", status['status'])


            # Verificar si el mensaje es interactivo (de botón) o de texto
            mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]
            if mensaje['type'] == 'interactive' and mensaje['interactive']['type'] == 'button_reply':
                # Extraer el título del botón
                title = mensaje['interactive']['button_reply']['title']
                print("Título del botón:", title)

            elif mensaje['type'] == 'text':
                # Obtener el texto del mensaje
                mensaje_texto = mensaje['text']['body']
                
                print("Mensaje de texto:", mensaje_texto)

            # Establecer conexión con la base de datos
            db = conectar_base_datos()
            
            # Revisa en qué estado se encuentra el usuario que está escribiendo
            estado = consulta_estado_usuario(db, telefono)
            print(estado)

            # Si está vacío entra aquí; es decir, no hay estado con ese número de teléfono
            if not estado:
                # Ingresar datos para poner un estado al nuevo número
                datos = {
                    "Telefono": telefono,
                    "Nombre": nombre,
                    "Estado": "Bienvenido",
                }
                # agregar_record(db, datos)
                # Enviar mensaje de bienvenida
                enviar_mensaje("En qué te puedo ayudar?", "bienvenida")

        except KeyError as e:
            print(f"Clave faltante en el JSON recibido: {e}")
            # Puedes agregar una respuesta o manejo adicional aquí si lo deseas

        return jsonify({"status": "success"}), 200



# Funciones para enviar mensajes    
# Usar los botones en la función
def enviar_mensaje(encabezado,botones_llave):
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
                "text": "Selecciona una opción:"
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


# Endpoint para enviar mensajes desde el servidor
@app.route('/send', methods=['POST'])
def send_custom_message():
    data = request.json
    to = data.get("to")
    message = data.get("message")
    if to and message:
        response = send_message(to, message)
        return jsonify(response)
    return jsonify({"error": "Datos faltantes"}), 400

if __name__ == '__main__':
    app.run(debug=True)
