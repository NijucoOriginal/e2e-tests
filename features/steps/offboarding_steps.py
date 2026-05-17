import time
import subprocess
import requests
from behave import given, when, then

AUTH_URL = "http://localhost:8086"
EMPLOYEES_URL = "http://localhost:8081"
LOGS_URL = "http://localhost:8085"

POLLING_INTENTOS = 20
POLLING_ESPERA = 3

EMAIL_OFFBOARDING = "bdd.offboarding@empresa.com"
ID_OFFBOARDING = 88001


def _crear_empleado_offboarding():
    payload = {
        "id_employee": ID_OFFBOARDING,
        "name_one": "BDD",
        "other_name": "Off",
        "first_surname": "Boarding",
        "second_surname": "Test",
        "telephone": "3001234567",
        "address": "Calle BDD 123",
        "postcode": 11001,
        "email": EMAIL_OFFBOARDING,
        "city_name": "Bogota",
        "position_name": "Tester",
        "department_id": 1
    }
    return requests.post(f"{EMPLOYEES_URL}/employee/save/", json=payload, timeout=30)


def _polling_usuario_habilitado(email):
    """Espera hasta que el usuario exista y esté habilitado en PostgreSQL."""
    for _ in range(POLLING_INTENTOS):
        try:
            result = subprocess.run([
                "docker", "exec", "challenges-microservices-db-e-1",
                "psql", "-U", "carlos", "-d", "employees",
                "-t", "-c", f"SELECT COUNT(*) FROM users WHERE email = '{email}' AND enabled = true;"
            ], capture_output=True, text=True, timeout=10)
            count = result.stdout.strip()
            if count and int(count) > 0:
                return True
        except Exception:
            pass
        time.sleep(POLLING_ESPERA)
    return False


def _polling_usuario_deshabilitado(email):
    """Espera hasta que el usuario quede con enabled=false en PostgreSQL."""
    for _ in range(POLLING_INTENTOS):
        try:
            result = subprocess.run([
                "docker", "exec", "challenges-microservices-db-e-1",
                "psql", "-U", "carlos", "-d", "employees",
                "-t", "-c", f"SELECT COUNT(*) FROM users WHERE email = '{email}' AND enabled = false;"
            ], capture_output=True, text=True, timeout=10)
            count = result.stdout.strip()
            if count and int(count) > 0:
                return True
        except Exception:
            pass
        time.sleep(POLLING_ESPERA)
    return False


def _polling_log_desvinculacion(email):
    """Espera hasta que aparezca el log de desvinculación en MongoDB."""
    for _ in range(POLLING_INTENTOS):
        try:
            resp = requests.get(f"{LOGS_URL}/notifications/delete", timeout=5)
            if resp.status_code == 200:
                logs = resp.json()
                if any(email in str(log) for log in logs):
                    return True
        except Exception:
            pass
        time.sleep(POLLING_ESPERA)
    return False


def _obtener_id_empleado(email):
    """Obtiene el id_employee desde PostgreSQL."""
    try:
        result = subprocess.run([
            "docker", "exec", "challenges-microservices-db-e-1",
            "psql", "-U", "carlos", "-d", "employees",
            "-t", "-c", f"SELECT id_employee FROM employees WHERE email = '{email}';"
        ], capture_output=True, text=True, timeout=10)
        id_emp = result.stdout.strip()
        if id_emp:
            return int(id_emp)
    except Exception:
        pass
    return None


def _configurar_credenciales(email):
    """Hace recover-password y reset-password para activar las credenciales."""
    resp = requests.post(
        f"{AUTH_URL}/auth/recover-password",
        json={"email": email},
        timeout=5
    )
    if resp.status_code != 200:
        return False
    token = resp.json().get("resetToken")
    if not token:
        return False
    resp2 = requests.post(
        f"{AUTH_URL}/auth/reset-password",
        json={"token": token, "newPassword": "OffPass123!"},
        timeout=5
    )
    return resp2.status_code == 200


def _limpiar_offboarding():
    """Limpia empleados y usuarios de offboarding en PostgreSQL."""
    try:
        subprocess.run([
            "docker", "exec", "challenges-microservices-db-e-1",
            "psql", "-U", "carlos", "-d", "employees",
            "-c", f"DELETE FROM employees WHERE email = '{EMAIL_OFFBOARDING}'; DELETE FROM users WHERE email = '{EMAIL_OFFBOARDING}';"
        ], capture_output=True, timeout=10)
    except Exception:
        pass


# ── STEPS: DADO ───────────────────────────────────────────────────────────────

@given('que existe un empleado activo con credenciales configuradas')
def step_empleado_activo(context):
    context.email_offboarding = EMAIL_OFFBOARDING
    context.password_offboarding = "OffPass123!"

    # Limpia datos previos
    _limpiar_offboarding()

    # Crea el empleado
    resp = _crear_empleado_offboarding()
    assert resp.status_code in [200, 201], (
        f"No se pudo crear el empleado de offboarding. "
        f"Código: {resp.status_code}. Detalle: {resp.text}"
    )

    # Espera que el usuario se cree en auth-service
    creado = _polling_usuario_habilitado(EMAIL_OFFBOARDING)
    assert creado, f"El usuario '{EMAIL_OFFBOARDING}' no fue creado en el auth-service."

    # Configura credenciales activas
    configurado = _configurar_credenciales(EMAIL_OFFBOARDING)
    assert configurado, f"No se pudieron configurar las credenciales para '{EMAIL_OFFBOARDING}'."


# ── STEPS: CUANDO ─────────────────────────────────────────────────────────────

@when('elimino al empleado del sistema')
def step_eliminar_empleado(context):
    id_emp = _obtener_id_empleado(context.email_offboarding)
    assert id_emp, f"No se encontró el id del empleado '{context.email_offboarding}'."
    context.id_offboarding = id_emp

    resp = requests.delete(
        f"{EMPLOYEES_URL}/employee/delete/{id_emp}",
        timeout=10
    )
    assert resp.status_code in [200, 204], (
        f"No se pudo eliminar el empleado. "
        f"Código: {resp.status_code}. Detalle: {resp.text}"
    )


# ── STEPS: ENTONCES ───────────────────────────────────────────────────────────

@then('el usuario queda deshabilitado en el auth-service')
def step_usuario_deshabilitado(context):
    deshabilitado = _polling_usuario_deshabilitado(context.email_offboarding)
    assert deshabilitado, (
        f"El usuario '{context.email_offboarding}' no fue deshabilitado "
        f"en el auth-service tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )


@then('el sistema registra el evento de desvinculación en los logs')
def step_log_desvinculacion(context):
    encontrado = _polling_log_desvinculacion(context.email_offboarding)
    assert encontrado, (
        f"No se encontró log de desvinculación para '{context.email_offboarding}' "
        f"tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )


@then('el empleado no puede autenticarse en el sistema')
def step_no_puede_autenticar(context):
    # Espera que el usuario quede deshabilitado antes de intentar login
    deshabilitado = _polling_usuario_deshabilitado(context.email_offboarding)
    assert deshabilitado, (
        f"El usuario '{context.email_offboarding}' no fue deshabilitado "
        f"tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )

    resp = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"email": context.email_offboarding, "password": context.password_offboarding},
        timeout=5
    )
    assert resp.status_code in [401, 403], (
        f"Se esperaba error de autenticación pero el servidor respondió "
        f"con {resp.status_code}."
    )


@then('la recuperación de contraseña falla para el empleado desvinculado')
def step_recuperacion_falla(context):
    # Espera que el usuario quede deshabilitado antes de intentar recover
    deshabilitado = _polling_usuario_deshabilitado(context.email_offboarding)
    assert deshabilitado, (
        f"El usuario '{context.email_offboarding}' no fue deshabilitado "
        f"tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )

    resp = requests.post(
        f"{AUTH_URL}/auth/recover-password",
        json={"email": context.email_offboarding},
        timeout=5
    )
    assert resp.status_code in [400, 403, 404, 500], (
        f"Se esperaba error en recuperación de contraseña pero el servidor "
        f"respondió con {resp.status_code}. Detalle: {resp.text}"
    )