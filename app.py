from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
from database import *

app = Flask(__name__)

# Carga las variables del archivo .env
load_dotenv()

# Estado de los usuarios almacenado en memoria
client_states = {}

# Configura el token de acceso de la API de WhatsApp
VERIFY_TOKEN = "Sopo2024*"  # Cambia esto por tu token de verificación
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_API_URL = "https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"  # Reemplaza {PHONE_NUMBER_ID} con el ID de tu número de WhatsApp Business

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
        print("Mensaje recibido:", data)  # Imprime el mensaje en la terminal
        print(data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'])
        # INICIO OFICIAL DEL CHAT BOT 

        # OBTENER DATOS DEL USUARIO
        # Numero de telefono del contacto
        telefono = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

        # Obtener el nombre del contacto o "Usuario" si no existe
        contacto = data['entry'][0]['changes'][0]['value']['contacts'][0]
        nombre = contacto['profile'].get('name', 'Usuario')

        # Obtener mensaje escrito por el usuario
        mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

        # Revisa en que estado se encuentra el usuario que esta escribiendo
        estado_usuario(telefono)


        return jsonify({"status": "success"}), 200

# Revisar en que estado se encuentra el usuario
def estado_usuario(telefono):


# Función para enviar mensajes usando la API de WhatsApp
def send_message(to, message_text):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

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
