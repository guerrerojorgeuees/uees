import json
import pika
import random

CAMPOS_FORMULARIO = ["nombres", "apellidos", "cedula", "edad", "estudios", "correo", "ciudad"]

def generar_formulario():
    formulario = {campo: generar_valor(campo) for campo in CAMPOS_FORMULARIO}
    return formulario

def generar_valor(campo):
    if campo == "edad":
        return random.randint(18, 80)
    elif campo == "estudios":
        niveles_estudio = ["Primaria", "Secundaria", "Universitaria"]
        return random.choice(niveles_estudio)
    elif campo == "cedula":
        return str(random.randint(1000000000, 9999999999))  # Garantizar 10 dígitos
    else:
        return f"{campo.capitalize()} {random.randint(1, 100)}"



def enviar_formulario(formulario, canal):
    formulario_json = json.dumps(formulario)
    canal.basic_publish(exchange='', routing_key='cola_formularios', body=formulario_json)
    print(f"Formulario enviado a la cola: {formulario_json}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    canal = connection.channel()

    canal.queue_declare(queue='cola_formularios')

    while True:
        num_formularios = int(input("¿Cuántos formularios desea generar y enviar? "))
        
        for _ in range(num_formularios):
            formulario = generar_formulario()
            enviar_formulario(formulario, canal)
        
        continuar = input("¿Desea seguir generando formularios? (s/n): ").lower()
        if continuar != 's':
            break

    connection.close()

if __name__ == "__main__":
    main()
