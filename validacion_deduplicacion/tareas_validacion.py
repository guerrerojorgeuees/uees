from celery import Celery
import json

app = Celery('validacion_deduplicacion', include=['validacion_deduplicacion.tareas_validacion'])
app.config_from_object('config.celeryconfig')

@app.task
def validar_formulario(formulario_json):
    formulario = json.loads(formulario_json)  # Decodifica el JSON en un diccionario

    # Verificar si el campo "campo1" tiene al menos 4 caracteres
    if len(formulario.get("campo1", "")) >= 4:
        print("Campo 'campo1' tiene al menos 4 caracteres y es válido.")
    else:
        print("Campo 'campo1' debe tener al menos 4 caracteres y es inválido.")
