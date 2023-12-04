# Importación de módulos
import json
import pika
from formulario import generar_formulario

# Función para enviar un formulario a la cola
def enviar_formulario(formulario, canal):
    formulario_json = json.dumps(formulario)
    canal.basic_publish(exchange='', routing_key='cola_formularios', body=formulario_json)
    print(f"Formulario enviado a la cola: {formulario_json}")

# Función para ejecutar el simulador y enviar formularios a la cola
def ejecutar_simulador(num_formularios):
    # Establecer conexión con el servidor de RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    # Declarar la cola
    canal.queue_declare(queue='cola_formularios')

    # Generar y enviar los formularios a la cola
    for _ in range(num_formularios):
        formulario = generar_formulario()
        enviar_formulario(formulario, canal)

    # Cerrar la conexión
    connection.close()

# Función principal
if __name__ == "__main__":
    while True:
        # Solicitar al usuario la cantidad de formularios a generar y enviar
        num_formularios = int(input("¿Cuántos formularios desea generar y enviar? "))

        # Ejecutar el simulador
        ejecutar_simulador(num_formularios)

        # Preguntar al usuario si desea seguir generando formularios
        continuar = input("¿Desea seguir generando formularios? (s/n): ").lower()
        if continuar != 's':
            break
