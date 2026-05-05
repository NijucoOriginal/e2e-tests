import os
from dotenv import load_dotenv


def before_all(context):
    # Cargar las variables del archivo .env de pruebas
    load_dotenv()

    # --- CUMPLIENDO EL PUNTO 3 DE LA RÚBRICA ---
    # a) Acceder a la URL base mediante variable de entorno
    context.base_url = os.getenv("BASE_URL", "http://localhost:8081")

    # Credenciales de entorno
    context.admin_user = os.getenv("ADMIN_USER")
    context.admin_pass = os.getenv("ADMIN_PASS")

    # b) Almacenar el token de autenticación actual
    context.token = None

    # c) Almacenar la última respuesta HTTP recibida
    context.respuesta_api = None


def before_scenario(context, scenario):
    # Limpiamos el token y la respuesta antes de cada prueba para mantener aislamiento
    context.token = None
    context.respuesta_api = None