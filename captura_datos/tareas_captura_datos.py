from celery import Celery
import json
import random
app = Celery('captura_datos', include=['captura_datos.tareas_captura_datos'])
app.config_from_object('config.celeryconfig')

@app.task
def generar_formulario():
    # Tu lógica para generar el formulario, por ejemplo, llenarlo de forma aleatoria
    formulario = {
    "campo1": generar_valor_aleatorio(),
    "campo2": generar_valor_aleatorio(),
    "campo3": generar_valor_aleatorio(),
    }

    formulario_json = json.dumps(formulario)

    # Aquí puedes agregar un mensaje para indicar que se está enviando a la cola de mensajes
    print("Formulario enviado a la cola de mensajes:", formulario_json)

    # Envía el formulario a la cola de mensajes
    return formulario_json

def generar_valor_aleatorio():
    valores_posibles = ["valor1", "valor2", "valor3", "valor4", "valor5"]
    return random.choice(valores_posibles)

