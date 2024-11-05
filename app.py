from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

# Carga las variables del archivo .env
load_dotenv()

# Estado de los usuarios almacenado en memoria
client_states = {}

# Configura el token de acceso de la API de WhatsApp
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_API_URL = "https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"  # Reemplaza {PHONE_NUMBER_ID} con el ID de tu número de WhatsApp Business

# Endpoint para recibir mensajes
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    # Verifica si el mensaje es de tipo texto
    if 'messages' in data['entry'][0]['changes'][0]['value']:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_id = message['from']  # ID del remitente (número de WhatsApp)
        text = message['text']['body'] if 'text' in message else None
        
        # Maneja el estado del cliente
        if from_id not in client_states:
            client_states[from_id] = {"estado": "inicio"}
        
        # Procesa el mensaje y genera una respuesta según el estado
        response_text = "Hola, ¿cómo puedo ayudarte?"
        
        # Actualiza el estado del cliente si es necesario
        client_states[from_id]["estado"] = "mensaje_recibido"
        
        # Envía una respuesta al usuario
        send_message(from_id, response_text)
    
    return "Evento recibido", 200

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
