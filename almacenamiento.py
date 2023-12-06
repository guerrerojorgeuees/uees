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
lider_actual = 0
# Definición de carpetas de almacenamiento y nodos de réplica
storage_folder = 'storage_data'
duplicates_folder = 'duplicates'
replica_nodes = [
    ('127.0.0.1', 5015, True),  # Líder
    ('127.0.0.1', 5016, False),  # Seguidora 1
    ('127.0.0.1', 5017, False),  # Seguidora 2
    ('127.0.0.1', 5018, False)   # Seguidora 3
]





# Ruta para simular la caída del líder
@app.route('/form/simular_caida_lider')
def hacer_caer_leader():
    global replica_nodes

    # Encuentra la posición del líder actual en el array
    lider_pos = next((i for i, node in enumerate(replica_nodes) if node[2]), None)

    if lider_pos is not None:
        # Cambia el estado del líder actual a False
        replica_nodes[lider_pos] = (replica_nodes[lider_pos][0], replica_nodes[lider_pos][1], False)

        # Encuentra la siguiente posición en el array para el nuevo líder
        nuevo_lider_pos = (lider_pos + 1) % len(replica_nodes)

        # Cambia el estado del nuevo líder a True
        replica_nodes[nuevo_lider_pos] = (replica_nodes[nuevo_lider_pos][0], replica_nodes[nuevo_lider_pos][1], True)

        return jsonify({'message': f'Leader simulated to be down. New leader: {nuevo_lider_pos}'})
    else:
        return jsonify({'message': 'No leader found'})

# Ruta para simular la desconexión temporal de un seguidor específico y la conexión de un nuevo seguidor
@app.route('/form/simular_desconexion_y_nuevo_seguidor/<int:seguidor_index>')
def simular_desconexion_y_nuevo_seguidor(seguidor_index):
    global replica_nodes

    if 1 <= seguidor_index < len(replica_nodes):
        # Desconectar el seguidor específico
        replica_nodes[seguidor_index] = (replica_nodes[seguidor_index][0], replica_nodes[seguidor_index][1], False)

        # Conectar un nuevo seguidor
        nuevo_seguidor = ('127.0.0.1', 5020 + len(replica_nodes), False)  # Nueva dirección IP y puerto para el nuevo seguidor
        replica_nodes.append(nuevo_seguidor)

        return jsonify({'message': f'Seguidor {seguidor_index} desconectado temporalmente. Nuevo seguidor conectado en {nuevo_seguidor}'})

    else:
        return jsonify({'error': 'Índice de seguidor no válido'}), 400






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
            host, port, lider_nodo = node_address
            s.connect((host, port))
            
            # Serializar los datos con comillas dobles y codificar a bytes antes de enviar
            serialized_data = json.dumps(form_data, ensure_ascii=False).encode('utf-8')

            s.sendall(serialized_data)
            if lider_nodo:  #solo el lider puede guardar
                print(node_address)
                print("es nodo lider!! si registro")
                print(lider_nodo)
                replicate_locally(form_data)


    except Exception as e:
        print(f"Error replicando a {node_address}: {e}")
        import traceback
        traceback.print_exc()

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
                            form_data = json.loads(data.decode('utf-8'))
                        else:
                            form_data = json.loads(data)
                        
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
