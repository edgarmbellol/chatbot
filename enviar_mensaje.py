import requests
import json

# Reemplaza con tus credenciales y configuración
ACCESS_TOKEN = "EAAPCuwU6mgQBO1kwv0xsm61Y6bE0o8q4mWP9AW9QYnvRQlHuD2ZBAOJJ1ZCfvBnZBdG78xGsATwrK2pDvZBjmFX8ipTctUDbwalOesKZAleYxaEy4ekJUCfSy80gQdAcsx9K6GBoqFwTazif1pR2nXTFeRV5GDaUz4awDlvWNNujqYlx8S7BxhZCwY0xZBEYUkuZAO1ueqJyWvhZCcPl24HgR9NkDsD5ymEWfMA7x2UTu46cghZAHBupeU"  # Tu token de acceso de WhatsApp Business API
PHONE_NUMBER_ID = "418920651309807"  # El ID del número de teléfono de tu cuenta de WhatsApp Business
RECIPIENT_PHONE_NUMBER = "whatsapp:+573057499964"  # Número de teléfono del destinatario (formato E.164)

def send_message_with_buttons():
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Estructura del mensaje con botones
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "¡Hola! ¿Cómo te puedo ayudar?"
            },
            "body": {
                "text": "Selecciona una opción:"
            },
            "footer": {
                "text": "Hospital XYZ"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "consult",
                            "title": "Consulta"
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
            }
        }
    }

    # Enviar la solicitud a la API de WhatsApp
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Comprobar la respuesta
    if response.status_code == 200:
        print("Mensaje enviado con éxito.")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}")
        print(response.json())

# Ejecuta la función para enviar el mensaje
send_message_with_buttons()
