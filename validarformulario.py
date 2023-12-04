# Importación de módulos
import json
import os
import requests

# URL del módulo de almacenamiento
direccion_modulo_almacenamiento = 'http://127.0.0.1:5020/form'

# Función para enviar un formulario al módulo de almacenamiento
def enviar_a_almacenamiento(formulario):
    url = f"{direccion_modulo_almacenamiento}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(formulario), headers=headers)

    if response.status_code == 201:
        print("Formulario enviado y almacenado correctamente en el módulo de almacenamiento.")
    else:
        print(f"Error al enviar el formulario al módulo de almacenamiento. Código de estado: {response.status_code}")

# Función para verificar si un formulario no está vacío
def formulario_no_vacio(formulario):
    return bool(formulario)

# Función para validar el formato de un número de cédula
def validar_numero_cedula(cedula):
    return cedula.isdigit() and len(cedula) == 10

# Función para verificar la existencia de una persona por su cédula en el módulo de almacenamiento
def validar_persona_existente(cedula):
    print("Consultando si ya existe el registro...")
    url = f"http://127.0.0.1:5020/form/existe_persona/{cedula}"
    response = requests.get(url)

    if response.status_code == 200:
        print("Ya existe este registro.")
        return True
    elif response.status_code == 404:
        print("La persona no existe.")
        return False
    else:
        return False

# Función para validar si un formulario está completo y no es duplicado
def formulario_completo(formulario):
    return all([
        formulario_no_vacio(formulario),
        validar_numero_cedula(formulario.get('numero_identificacion', '')),
        not validar_persona_existente(formulario.get('numero_identificacion', ''))
    ])

# Función para validar si un formulario es un duplicado
def es_duplicado(formulario):
    cedula = formulario.get('numero_identificacion', '')
    # Verificar si existe un formulario con la misma cédula en la carpeta de almacenamiento
    form_id = f'formulario_{cedula}.json'
    return validar_persona_existente(cedula) and not os.path.exists(os.path.join('storage_data', form_id))

# Función para validar y enviar el formulario al módulo de almacenamiento
def validar_deduplicar(formulario):
    if formulario_completo(formulario):
        if not es_duplicado(formulario):
            # Enviar el formulario al módulo de almacenamiento
            enviar_a_almacenamiento(formulario)
            return 'cola_validacion'
        else:
            return 'cola_duplicados'
    else:
        return 'cola_no_validos'

# Función para procesar un formulario y determinar su destino
def procesar_formulario(body, canal):
    formulario = json.loads(body.decode('utf-8'))
    cola_destino = validar_deduplicar(formulario)

    if cola_destino == 'cola_no_validos':
        # Guardar el formulario no válido en una carpeta local
        guardar_formulario_no_valido(formulario)
    elif cola_destino == 'cola_validacion':
        guardar_formulario_validado(formulario)

    return formulario, cola_destino

# Función para guardar un formulario no válido en una carpeta local
def guardar_formulario_no_valido(formulario):
    carpeta_no_validos = 'formularios_no_validos'
    os.makedirs(carpeta_no_validos, exist_ok=True)
    nombre_archivo = f"formulario_{formulario.get('numero_identificacion', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_no_validos, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario no válido guardado en: {ruta_archivo}")

# Función para guardar un formulario validado en una carpeta local
def guardar_formulario_validado(formulario):
    carpeta_validados = 'formularios_validados'
    os.makedirs(carpeta_validados, exist_ok=True)
    nombre_archivo = f"formulario_{formulario.get('numero_identificacion', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_validados, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario validado guardado en: {ruta_archivo}")
