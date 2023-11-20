import json
import pika
import os

def formulario_no_vacio(formulario):
    return bool(formulario)

def validar_numero_cedula(cedula):
    return cedula.isdigit() and len(cedula) == 10

def validar_persona_existente(cedula):
    # Lógica de validación de persona existente (por ahora siempre retorna False)
    return False

def formulario_completo(formulario):
    return all([
        formulario_no_vacio(formulario),
        validar_numero_cedula(formulario.get('cedula', '')),
        not validar_persona_existente(formulario.get('cedula', ''))
    ])

def es_duplicado(formulario):
    # Lógica de validación de duplicado (por ahora siempre retorna False)
    return False

def validar_deduplicar(formulario):
    if formulario_completo(formulario):
        if not es_duplicado(formulario):
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
    nombre_archivo = f"formulario_{formulario.get('cedula', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_no_validos, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario no válido guardado en: {ruta_archivo}")

def guardar_formulario_validado(formulario):
    carpeta_validados = 'formularios_validados'
    os.makedirs(carpeta_validados, exist_ok=True)
    nombre_archivo = f"formulario_{formulario.get('cedula', 'sin_cedula')}.json"
    ruta_archivo = os.path.join(carpeta_validados, nombre_archivo)

    with open(ruta_archivo, 'w') as archivo:
        json.dump(formulario, archivo)
    
    print(f"Formulario validado guardado en: {ruta_archivo}")
