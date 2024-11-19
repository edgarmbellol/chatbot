from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import requests
import os
import json
from database import *
from estados import *
from enviar_mensaje import *

app = Flask(__name__)
app.secret_key = 'Sopo2024*'  # Cambia esto a algo más seguro en producción

VERIFY_TOKEN = "Sopo"  # Cambia esto por tu token de verificación

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
            
                telefono = datos_mensaje['telefono']
                nombre = datos_mensaje['nombre']
                mensaje = datos_mensaje["mensaje_texto"]

                # Revisa en qué estado se encuentra el usuario que está escribiendo
                estado = consulta_estado_usuario(db, telefono)
                
                # Estado inicial cuando se empieza la conversacion no tiene el telefono guardado en la base de datos
                if datos_mensaje['tipo_mensaje'] == "texto" and not estado:
                    # Actualiza el estado a bienvenida y envia mensaje de bienvenida
                    bienvenida(db,telefono,nombre)

                # Entra cuando se presiona el boton de AGENGAR CITA
                elif estado == "bienvenido" and datos_mensaje['mensaje_texto'] == "Agendar cita":
                    # Actualiza estado a cedula citas y envia mensaje pidiendo cedula
                    cedula_citas(db,telefono)
                
                # Entra cuando se ingresa el numero de cedula de la persona luego de presionar el boton agendar cita
                elif estado == "cedula citas":
                    # Agregar cedula a la base de datos
                    cedula = mensaje
                    eps_citas(db,telefono,cedula)
                
                # Entra cuando se selecciono eps a la que el usuario pertenece
                elif estado == "eps citas":

                    confirmacion_informacion(db,telefono,nombre,mensaje)

                # Entra cuando se selecciona una opcion de si o no a confirmacion citas
                elif estado == "confirmacion informacion":
                    if mensaje == "Si":
                        # Los datos ingresados por el usuario son correctos
                        # BUSCAR EN LA BASE DE DATOS SI EXISTE COINCIDENCIA CON LA CEDULA
                        verificar_paciente(db,telefono)
                    else:
                        # Cambia el estado a bienvenido y redirije a la primera instancia
                        datos_incorrectos(db,telefono)

                elif estado == "verificar usuario citas":
                    # Verifica que el usuario verifique sus datos
                    if mensaje == "Si":
                        # El usuario procede a seleccionar especialidad
                        seleccionar_especialidad(db,telefono)
                    else:
                        # Se redirije a la seccion bienvenido
                        datos_incorrectos(db,telefono)
                        
                elif estado == "seleccionar especialidad":
                    confirmar_especialidad(db,telefono,mensaje)
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
