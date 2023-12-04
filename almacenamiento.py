# Importación de módulos
import json
import os
from flask import Flask, request, jsonify
from threading import Thread
import socket
import threading
import time

# Creación de la aplicación Flask
app = Flask(__name__)

# Definición de carpetas de almacenamiento y nodos de réplica
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

# Función para convertirse en líder
def convertirse_en_lider():
    global es_lider
    es_lider = True
    print("¡Ahora eres el líder!")

# Función para simular la detección de fallos y la elección de un nuevo líder
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

# Función para replicar a otros nodos
def replicate_to_other_nodes(form_data, sender_address):
    for node_address in replica_nodes:
        if node_address != sender_address:  # Evitar enviar de vuelta al remitente
            Thread(target=send_replication_request, args=(node_address, form_data)).start()

# Función para enviar una solicitud de replicación a un nodo específico
def send_replication_request(node_address, form_data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Desempaquetar la dirección del nodo
            print("Dirección del nodo:", node_address)
            host, port, _ = node_address

            print("aqui estamos 1")
            print(port)
            s.connect((host, port))
            
            # Serializar los datos antes de enviar con comillas dobles
            serialized_data = json.dumps(form_data, ensure_ascii=False).encode('utf-8')
            s.sendall(serialized_data)
    except Exception as e:
        print(f"Error replicando a {node_address}: {e}")
        import traceback
        traceback.print_exc()





# # Función para replicar localmente
# def replicate_locally(form_data):
#     global es_lider
#     form_id = form_data.get('id')
#     print("aqui estamos")
#     print(es_lider)
#     try:
#         if es_lider:
#             os.makedirs(storage_folder, exist_ok=True)
#             with open(os.path.join(storage_folder, f'{form_id}.json'), 'w') as form_file:
#                 json.dump(form_data, form_file)
#             print("Soy el líder, almacenando localmente.")
#         else:
#             print("No soy el líder, solo replicando el formulario.")
#     except Exception as e:
#         print(f"Error al guardar localmente: {e}")

# Función para replicar localmente
def replicate_locally(form_data):
    form_id = form_data.get('numero_identificacion')
    try:
        os.makedirs(storage_folder, exist_ok=True)
        with open(os.path.join(storage_folder, f'{form_id}.json'), 'w') as form_file:
            # Imprimir el formulario antes de guardarlo
            # print("Formulario a guardar:", form_id)
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

# Ruta para guardar un formulario y realizar replicación
@app.route('/form', methods=['GET', 'POST'])
def save_form():

    try:
        if request.method == 'POST':
            form_data = request.get_json()
            # print("Datos recibidos:", form_data)  # Agrega esta línea para imprimir los datos recibidos
            form_id = form_data.get('numero_identificacion')

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

            # if es_lider:
            #     # Guardar localmente solo si es líder
           
            # if isinstance(form_data, bytes):
            #      form_data = json.loads(form_data.decode('utf-8').replace("'", "\""))
            # else:
            #     form_data = json.loads(form_data.replace("'", "\""))

            # print("JSON a enviar:", form_data)
            replicate_locally(form_data)

            # Realizar replicación solo si es líder
            replicate_to_other_nodes(form_data, (sender_ip, sender_port))

            return jsonify({'message': 'Form saved successfully'}), 201
        else:
            # Lógica para manejar solicitudes GET si es necesario
            return jsonify({'message': 'This endpoint only accepts POST requests'}), 405

    except Exception as e:
        print("Error al procesar la solicitud:", str(e))
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
                    try:
                        # Decodificar los datos correctamente
                        if isinstance(data, bytes):
                            form_data = json.loads(data.decode('utf-8').replace("'", "\""))
                        else:
                            form_data = json.loads(data.replace("'", "\""))

                        print("JSON recibido:", form_data)
                        replicate_locally(form_data)
                    except json.JSONDecodeError as json_error:
                        print(f"Error en réplica {node_address}: JSON no válido - {json_error}")        

    except Exception as e:
        print(f"Error en réplica {node_address}: {e}")


# Configuración y ejecución de réplicas
if __name__ == '__main__':
    for node_address in replica_nodes:
        Thread(target=run_replica, args=(node_address,)).start()

    # Iniciar servidor Flask
    app.run(port=5020)
