import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv


def _limpiar_bd_pruebas():
    """Limpia empleados y usuarios BDD directamente en PostgreSQL."""
    try:
        subprocess.run([
            "docker", "exec", "challenges-microservices-db-e-1",
            "psql", "-U", "carlos", "-d", "employees",
            "-c", "DELETE FROM employees WHERE email LIKE 'bdd.%'; DELETE FROM users WHERE email LIKE 'bdd.%';"
        ], capture_output=True, timeout=10)
    except Exception:
        pass


def before_all(context):
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    context.base_url      = os.getenv("BASE_URL", "http://localhost:8086")
    context.admin_user    = os.getenv("ADMIN_USER")
    context.admin_pass    = os.getenv("ADMIN_PASS")
    context.user_user     = os.getenv("USER_USER")
    context.user_pass     = os.getenv("USER_PASS")
    context.token         = None
    context.respuesta_api = None


def before_scenario(context, scenario):
    context.token         = None
    context.respuesta_api = None
    context.email_prueba  = None
    if "onboarding" in scenario.feature.filename:
        _limpiar_bd_pruebas()


def after_scenario(context, scenario):
    context.token         = None
    context.respuesta_api = None
    context.email_prueba  = None
    if "onboarding" in scenario.feature.filename:
        _limpiar_bd_pruebas()

def _limpiar_offboarding_bd():
    try:
        subprocess.run([
            "docker", "exec", "challenges-microservices-db-e-1",
            "psql", "-U", "carlos", "-d", "employees",
            "-c", "DELETE FROM employees WHERE email = 'bdd.offboarding@empresa.com'; DELETE FROM users WHERE email = 'bdd.offboarding@empresa.com';"
        ], capture_output=True, timeout=10)
    except Exception:
        pass