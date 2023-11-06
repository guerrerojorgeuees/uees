from captura_datos.tareas_captura_datos import app
from captura_datos.tareas_captura_datos import generar_formulario
from validacion_deduplicacion.tareas_validacion import validar_formulario


if __name__ == '__main__':
    formulario_json = generar_formulario()
    validar_formulario.delay(formulario_json)
    print("Formulario generado y encolado:", formulario_json)



