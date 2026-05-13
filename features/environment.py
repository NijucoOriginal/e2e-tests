import os
from dotenv import load_dotenv
from pathlib import Path


def before_all(context):
    # Carga el .env desde la misma carpeta donde está environment.py
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    context.base_url   = os.getenv("BASE_URL", "http://localhost:8086")
    context.admin_user = os.getenv("ADMIN_USER")
    context.admin_pass = os.getenv("ADMIN_PASS")
    context.user_user  = os.getenv("USER_USER")
    context.user_pass  = os.getenv("USER_PASS")
    context.token      = None
    context.respuesta_api = None


def before_scenario(context, scenario):
    """
    Se ejecuta antes de CADA escenario.
    Limpia el estado para garantizar aislamiento total entre pruebas.
    Sin esto, el token de un escenario ADMIN podría 'contaminar' el siguiente.
    """
    context.token = None
    context.respuesta_api = None


def after_scenario(context, scenario):
    """
    Se ejecuta después de CADA escenario.
    Útil para limpiar datos creados durante la prueba (evitar 'basura').
    Por ahora limpiamos las referencias; en Punto 3 y 4 agregaremos
    lógica de cleanup de empleados creados.
    """
    context.token = None
    context.respuesta_api = None