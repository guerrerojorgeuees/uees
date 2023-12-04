# Importación de módulos
import pika
import json
from validarformulario import procesar_formulario

# Clase para gestionar la cola de mensajes
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

# Función de callback para procesar mensajes de la cola
def callback(ch, method, properties, body):
    # Crear una instancia de ColaMensajes
    cola_mensajes = ColaMensajes(host='localhost', cola='cola_formularios')

    # Procesar el formulario y obtener la cola de destino
    formulario, cola_destino = procesar_formulario(body, cola_mensajes)

    # Enviar el formulario a la cola de destino
    cola_mensajes.enviar_mensaje(json.dumps(formulario), cola_destino)

    print(f"Formulario enviado a la cola {cola_destino}")

# Función para iniciar el módulo de cola
def iniciar_cola():
    # Establecer conexión con el servidor de RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    # Declarar la cola
    canal.queue_declare(queue='cola_formularios')

    # Configurar la función de callback para procesar mensajes
    canal.basic_consume(queue='cola_formularios', on_message_callback=callback, auto_ack=True)

    # Iniciar el consumo de mensajes
    print('Módulo de cola esperando formularios. Para salir, presione CTRL+C')
    canal.start_consuming()

# Función principal
if __name__ == "__main__":
    iniciar_cola()
