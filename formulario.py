import random

CAMPOS_FORMULARIO = [
    "nombre",
    "apellido",
    "numero_identificacion",
    "fecha_nacimiento",
    "genero",
    "nacionalidad",
    "direccion",
    "ciudad",
    "codigo_postal",
    "telefono",
    "correo_electronico",
    "estado_civil",
    "numero_hijos",
    "fecha_matrimonio",
    "nivel_educativo",
    "ultimo_grado_completado",
    "especializacion",
    "ocupacion_actual",
    "sector_laboral",
    "tiempo_empleo_actual",
    "ingresos_mensuales",
    "propiedad_vivienda",
    "deudas",
    "estado_salud",
]

def generar_formulario():
    formulario = {campo: generar_valor(campo) for campo in CAMPOS_FORMULARIO}
    return formulario

def generar_valor(campo):
    if campo == "fecha_nacimiento" or campo == "fecha_matrimonio":
        return f"{random.randint(1, 28)}/{random.randint(1, 12)}/{random.randint(1950, 2005)}"
    elif campo == "telefono":
        return f"+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    elif campo == "correo_electronico":
        return f"{campo.lower()}_{random.randint(1, 100)}@dominio.com"
    elif campo == "numero_identificacion":
        return str(random.randint(1000000000, 9999999999))  # Garantizar 10 dígitos
        # return '0942807462' # Garantizar 10 dígitos
    elif campo == "ingresos_mensuales":
        return str(round(random.uniform(1000, 10000), 2))
    elif campo == "estado_salud_general":
        return random.choice(["Excelente", "Bueno", "Regular", "Malo"])
    elif campo == "acceso_electricidad" or campo == "acceso_agua_potable" or campo == "servicios_saneamiento":
        return random.choice(["Sí", "No"])
    elif campo == "tiempo_residencia_actual":
        return f"{random.randint(1, 10)} años {random.randint(1, 12)} meses"
    else:
        return f"{campo.capitalize()} {random.randint(1, 100)}"