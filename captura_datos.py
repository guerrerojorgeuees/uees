import json
import pika
from formulario import generar_formulario

def enviar_formulario(formulario, canal):
    formulario_json = json.dumps(formulario)
    canal.basic_publish(exchange='', routing_key='cola_formularios', body=formulario_json)
    print(f"Formulario enviado a la cola: {formulario_json}")

def ejecutar_simulador(num_formularios):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    canal.queue_declare(queue='cola_formularios')

    for _ in range(num_formularios):
        formulario = generar_formulario()
        enviar_formulario(formulario, canal)

    connection.close()

if __name__ == "__main__":
    while True:
        num_formularios = int(input("¿Cuántos formularios desea generar y enviar? "))

        ejecutar_simulador(num_formularios)

        continuar = input("¿Desea seguir generando formularios? (s/n): ").lower()
        if continuar != 's':
            break
