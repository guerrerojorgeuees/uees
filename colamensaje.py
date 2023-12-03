import pika
import json
from validarformulario import procesar_formulario

class ColaMensajes:
    def __init__(self, host, cola):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.cola = cola

    def enviar_mensaje(self, mensaje, cola_destino):
        self.channel.queue_declare(queue=cola_destino)
        self.channel.basic_publish(exchange='', routing_key=cola_destino, body=mensaje)

    def cerrar_conexion(self):
        self.connection.close()

def callback(ch, method, properties, body):
    cola_mensajes = ColaMensajes(host='localhost', cola='cola_formularios')

    formulario, cola_destino = procesar_formulario(body, cola_mensajes)

    cola_mensajes.enviar_mensaje(json.dumps(formulario), cola_destino)

    print(f"Formulario enviado a la cola {cola_destino}")

def iniciar_cola():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    canal.queue_declare(queue='cola_formularios')

    canal.basic_consume(queue='cola_formularios', on_message_callback=callback, auto_ack=True)

    print('Módulo de cola esperando formularios. Para salir, presione CTRL+C')
    canal.start_consuming()

if __name__ == "__main__":
    iniciar_cola()
