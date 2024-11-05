from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

app = Flask(__name__)

# Carga las variables del archivo .env
load_dotenv()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Aquí procesas los mensajes entrantes
    handle_message(data)
    return jsonify({"status": "success"}), 200

def handle_message(data):
    # Procesa el mensaje recibido
    if 'messages' in data:
        for message in data['messages']:
            sender_id = message['from']  # ID del remitente
            text = message['text']['body']  # El texto del mensaje
            respond_with_buttons(sender_id)

def respond_with_buttons(sender_id):
    # Aquí construyes la respuesta con botones
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": "consult",
                "title": "Consultar"
            }
        },
        {
            "type": "reply",
            "reply": {
                "id": "schedule",
                "title": "Agendar cita"
            }
        }
    ]
    
    response = {
        "to": sender_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "¡Hola! ¿Qué deseas hacer?"
            },
            "body": {
                "text": "Selecciona una opción:"
            },
            "footer": {
                "text": "Hospital XYZ"
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    
    # Envía la respuesta a la API de WhatsApp
    send_response(response)

def send_response(response):
    # Envía el mensaje a la API de WhatsApp
    # Asegúrate de incluir tu token y URL de la API
    access_token = "hospital"  # Reemplaza esto con tu token
    api_url = "https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    requests.post(api_url, headers=headers, json=response)

if __name__ == '__main__':
    app.run(port=5000)
