import pika

def callback(ch, method, properties, body):
    print(f"Formulario recibido desde la cola en el servidor: {body.decode()}")

def iniciar_servidor():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    canal.queue_declare(queue='cola_formularios')

    canal.basic_consume(queue='cola_formularios', on_message_callback=callback, auto_ack=True)

    print('Servidor esperando formularios desde la cola. Para salir, presione CTRL+C')
    canal.start_consuming()

if __name__ == "__main__":
    iniciar_servidor()
