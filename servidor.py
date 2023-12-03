import requests
import json

url = "http://127.0.0.1:5009/form"

# Ejemplo de datos del formulario
form_data = {
    "id": 123,
    "name": "Ejemplo",
    "content": "Contenido de ejemplo"
}

# Hacer una solicitud POST al servidor
response = requests.post(url, json=form_data, headers={"X-Real-Ip": "127.0.0.1", "X-Real-Port": "5005"})

# Imprimir la respuesta del servidor
print(response.status_code)
print(response.json())
