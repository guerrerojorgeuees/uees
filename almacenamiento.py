import json
import os
from flask import Flask, request, jsonify
from threading import Thread
import socket
import threading
import time

app = Flask(__name__)
storage_folder = 'storage_data'
duplicates_folder = 'duplicates'
replica_nodes = [
    ('127.0.0.1', 5015, True),  # Líder
    ('127.0.0.1', 5016, False),  # Seguidora 1
    ('127.0.0.1', 5017, False),  # Seguidora 2
    ('127.0.0.1', 5018, False)   # Seguidora 3
]

# Variables para simular el estado de liderazgo y la detección de fallos
es_lider = False
detectando_fallo = False

def convertirse_en_lider():
    global es_lider
    es_lider = True
    print("¡Ahora eres el líder!")

def detectar_fallo():
    global es_lider, detectando_fallo
    while True:
        time.sleep(10)  # Simular la detección de fallos cada 10 segundos
        if es_lider and not detectando_fallo:
            detectando_fallo = True
            # Lógica de detección de fallos aquí (puedes implementar un algoritmo específico)
            # En este ejemplo, se asume que el líder falla y se inicia la elección de un nuevo líder
            print("¡Fallo detectado! Iniciando elección de líder...")
            es_lider = False
            detectando_fallo = False
            convertirse_en_lider()

# Ruta para convertirse en líder
@app.route('/convertirse_en_lider', methods=['POST'])
def convertirse_en_lider_endpoint():
    convertirse_en_lider()
    return jsonify({'message': '¡Ahora eres el líder!'}), 200

def replicate_to_other_nodes(form_data, sender_address):
    for node_address in replica_nodes:
        if node_address != sender_address:  # Evitar enviar de vuelta al remitente
            Thread(target=send_replication_request, args=(node_address, form_data)).start()

def send_replication_request(node_address, form_data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(node_address)
            s.sendall(json.dumps(form_data).encode('utf-8'))
    except Exception as e:
        print(f"Error replicando a {node_address}: {e}")

def replicate_locally(form_data):
    form_id = form_data.get('id')
    try:
        os.makedirs(storage_folder, exist_ok=True)
        with open(os.path.join(storage_folder, f'{form_id}.json'), 'w') as form_file:
            json.dump(form_data, form_file)
    except Exception as e:
        print(f"Error al guardar localmente: {e}")

# Ruta para verificar la existencia de una persona por su cédula
def verificar_existencia_persona(cedula):
    # Generar el nombre del archivo con la convención "formulario_numerocedula.json"
    form_id = f'formulario_{cedula}.json'

    # Verificar si existe el archivo en la carpeta de almacenamiento
    return os.path.exists(os.path.join(storage_folder, form_id))

@app.route('/form/existe_persona/<cedula>', methods=['GET'])
def existe_persona(cedula):
    try:
        # Lógica para verificar la existencia de la persona con la cédula proporcionada
        if verificar_existencia_persona(cedula):
            return jsonify({'message': 'Persona encontrada'}), 200
        else:
            return jsonify({'message': 'Persona no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/form', methods=['GET', 'POST'])
def save_form():
    try:
        if request.method == 'POST':
            form_data = request.get_json()
            form_id = form_data.get('id')

            # Obtener información del remitente desde los encabezados
            sender_ip = request.headers.get('X-Real-Ip')
            sender_port = request.headers.get('X-Real-Port')

            # Verificar duplicados localmente
            if os.path.exists(os.path.join(storage_folder, f'{form_id}.json')):
                # Almacenar en carpeta de duplicados
                os.makedirs(duplicates_folder, exist_ok=True)
                with open(os.path.join(duplicates_folder, f'{form_id}.json'), 'w') as duplicate_file:
                    json.dump(form_data, duplicate_file)
                return jsonify({'message': 'Duplicate form detected, stored in duplicates folder'}), 409

            # Guardar localmente
            replicate_locally(form_data)

            # Realizar replicación
            replicate_to_other_nodes(form_data, (sender_ip, sender_port))

            return jsonify({'message': 'Form saved successfully'}), 201
        else:
            # Lógica para manejar solicitudes GET si es necesario
            return jsonify({'message': 'This endpoint only accepts POST requests'}), 405

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Función para ejecutar réplica
def run_replica(node_address):
    is_leader = next(item[2] for item in replica_nodes if item[0] == node_address[0] and item[1] == node_address[1])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((node_address[0], node_address[1]))
            s.listen()

            print(f"Replica {'(Líder)' if is_leader else ''} listening on {node_address}")

            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        break
                    form_data = json.loads(data.decode('utf-8'))
                    replicate_locally(form_data)
    except Exception as e:
        print(f"Error en réplica {node_address}: {e}")

# Ruta para obtener el estado de liderazgo
@app.route('/es_lider', methods=['GET'])
def obtener_estado_liderazgo():
    return jsonify({'es_lider': es_lider}), 200

# Después de la configuración de las réplicas
# ...

if __name__ == '__main__':
    # Configurar réplicas
    for node_address in replica_nodes:
        Thread(target=run_replica, args=(node_address,)).start()

    # Iniciar servidor Flask
    app.run(port=5020)
