import json
import pika
import os
import requests  # Asegúrate de tener instalada la biblioteca requests

# Definir la dirección del módulo de almacenamiento
direccion_modulo_almacenamiento = 'http://127.0.0.1:5009/form'  # Cambiar el puerto según la configuración real

def enviar_a_almacenamiento(formulario):
    url = f"{direccion_modulo_almacenamiento}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(formulario), headers=headers)

    if response.status_code == 201:
        print("Formulario enviado y almacenado correctamente en el módulo de almacenamiento.")
    else:
        print(f"Error al enviar el formulario al módulo de almacenamiento. Código de estado: {response.status_code}")
        # Aquí podrías tomar medidas adicionales en caso de un código de estado diferente a 201.


def formulario_no_vacio(formulario):
    return bool(formulario)

def validar_numero_cedula(cedula):
    return cedula.isdigit() and len(cedula) == 10

import requests

# ...

def validar_persona_existente(cedula):
    print("consulto si ya existe")
    # Hacer una solicitud GET al módulo de almacenamiento para verificar si la persona ya existe
    url = f"http://127.0.0.1:5009/form/existe_persona/{cedula}"  # Ajusta la URL según tu implementación real
    response = requests.get(url)

    if response.status_code == 200:
        # La persona existe, retorna True
        print("Ya existe este registro")
        return True
    elif response.status_code == 404:
        # La persona no existe, retorna False
        return False
    else:
        # Manejar otros códigos de estado si es necesario
        # print(f"Error al verificar existencia de persona. Código de estado: {response.status_code}")
        return False


def formulario_completo(formulario):
    return all([
        formulario_no_vacio(formulario),
        validar_numero_cedula(formulario.get('numero_identificacion', '')),
        not validar_persona_existente(formulario.get('numero_identificacion', ''))
    ])

def es_duplicado(formulario):
    # Lógica de validación de duplicado (por ahora siempre retorna False)
    return False

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

def procesar_formulario(body, canal):
    formulario = json.loads(body.decode('utf-8'))
    cola_destino = validar_deduplicar(formulario)

    if cola_destino == 'cola_no_validos':
        # Guardar el formulario no válido en una carpeta local
        guardar_formulario_no_valido(formulario)
    elif cola_destino == 'cola_validacion':
        # Guardar el formulario validado en otra carpeta local
        guardar_formulario_validado(formulario)

    return formulario, cola_destino

def guardar_formulario_no_valido(formulario):
    carpeta_no_validos = 'formularios_no_validos'
    os.makedirs(carpeta_no_validos, exist_ok=True)
    nombre_archivo = f"formulario_{formulario.get('numero_identificacion', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_no_validos, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario no válido guardado en: {ruta_archivo}")

def guardar_formulario_validado(formulario):
    carpeta_validados = 'formularios_validados'
    os.makedirs(carpeta_validados, exist_ok=True)
    nombre_archivo = f"formulario_{formulario.get('numero_identificacion', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_validados, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario validado guardado en: {ruta_archivo}")
