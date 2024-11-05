import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Carga las variables del archivo .env
load_dotenv()

# Define tu token de verificación
VERIFY_TOKEN = "Sopo2024*"  # Cambia esto por tu token de verificación
ACCESS_TOKEN = "{VERIFICATION_TOKEN}"  # Reemplaza esto con tu token de acceso
PHONE_NUMBER_ID = "{PHONE_NUMBER_ID}"  # Reemplaza con tu número de teléfono ID

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
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
        if 'messages' in data:
            for message in data['messages']:
                sender_id = message['from']  # ID del remitente
                respond_with_buttons(sender_id)  # Responder con botones
        return jsonify({"status": "success"}), 200

def respond_with_buttons(sender_id):
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

    send_response(response)

def send_response(response):
    api_url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    requests.post(api_url, headers=headers, json=response)

if __name__ == '__main__':
    app.run(port=5000)
