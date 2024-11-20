import requests
import json
import os
from dotenv import load_dotenv


# Carga las variables del archivo .env
load_dotenv()

# Cargar la configuración de botones desde el archivo JSON
with open("botones.json", "r") as file:
    botones = json.load(file)


# Configura el token de acceso de la API de WhatsApp
VERIFY_TOKEN = "Sopo"  # Cambia esto por tu token de verificación
WHATSAPP_TOKEN = os.getenv("VERIFICATION_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/418920651309807/messages"  # Reemplaza {PHONE_NUMBER_ID} con el ID de tu número de WhatsApp Business
# RECIPIENT_PHONE_NUMBER = "whatsapp:+573057499964"  # Número de teléfono del destinatario (formato E.164)



# Enviar mensaje con botones interactivos
def enviar_mensaje_botones(telefono,encabezado,botones_llave,cuerpo="Selecciona una opción:"):
    RECIPIENT_PHONE_NUMBER = "whatsapp:+"+telefono
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
def enviar_mensaje_texto(telefono,encabezado):
    RECIPIENT_PHONE_NUMBER = "whatsapp:+"+telefono
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