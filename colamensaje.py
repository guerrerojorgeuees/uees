import pika
import json
from validarformulario import procesar_formulario

def callback(ch, method, properties, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    formulario, cola_destino = procesar_formulario(body, canal)
    
    canal.queue_declare(queue=cola_destino)

    canal.basic_publish(exchange='', routing_key=cola_destino, body=json.dumps(formulario))

    print(f"Formulario enviado a la cola {cola_destino}: {body.decode()}")

def iniciar_cola():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    canal.queue_declare(queue='cola_formularios')

    canal.basic_consume(queue='cola_formularios', on_message_callback=callback, auto_ack=True)

    print('Módulo de cola esperando formularios. Para salir, presione CTRL+C')
    canal.start_consuming()

if __name__ == "__main__":
    iniciar_cola()
