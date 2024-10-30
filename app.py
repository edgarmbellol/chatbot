import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Define el token de verificación que configuraste en el panel de WhatsApp
VERIFICATION_TOKEN = "prueba"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Obtiene los parámetros de la solicitud GET
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Verifica que el token recibido coincide con tu token de verificación
        if token == VERIFICATION_TOKEN:
            return challenge, 200  # Responde con el 'challenge' para verificar el webhook
        else:
            return "Token de verificación incorrecto", 403
    
    elif request.method == 'POST':
        data = request.get_json()
        
        print(data)
        # Procesa el mensaje entrante aquí
        if data and 'messages' in data['entry'][0]['changes'][0]['value']:
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            
            print(f'Mensaje recibido de {phone_number}: {message_text}')
            
            return jsonify({"status": "mensaje recibido"}), 200
        else:
            return jsonify({"status": "sin mensajes"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
