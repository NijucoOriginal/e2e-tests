import time
import requests
from behave import given, when, then

# ── HELPERS ───────────────────────────────────────────────────────────────────

AUTH_URL = "http://localhost:8086"
EMPLOYEES_URL = "http://localhost:8081"
LOGS_URL = "http://localhost:8085"

POLLING_INTENTOS = 20
POLLING_ESPERA = 3  # segundos


def _crear_empleado(email, id_empleado=90001):
    payload = {
        "id_employee": id_empleado,
        "name_one": "BDD",
        "other_name": "Test",
        "first_surname": "Onboarding",
        "second_surname": "Prueba",
        "telephone": "3001234567",
        "address": "Calle BDD 123",
        "postcode": 11001,
        "email": email,
        "city_name": "Bogota",
        "position_name": "Tester",
        "department_id": 1
    }
    return requests.post(f"{EMPLOYEES_URL}/employee/save/", json=payload)


import subprocess

def _polling_usuario_creado(email):
    for _ in range(POLLING_INTENTOS):
        try:
            result = subprocess.run([
                "docker", "exec", "challenges-microservices-db-e-1",
                "psql", "-U", "carlos", "-d", "employees",
                "-t", "-c", f"SELECT COUNT(*) FROM users WHERE email = '{email}';"
            ], capture_output=True, text=True, timeout=10)
            count = result.stdout.strip()
            if count and int(count) > 0:
                return True
        except Exception:
            pass
        time.sleep(POLLING_ESPERA)
    return False

def _polling_log_creado(email):
    """Hace polling hasta que aparezca el log del empleado en MongoDB."""
    for _ in range(POLLING_INTENTOS):
        resp = requests.get(f"{LOGS_URL}/notifications")
        if resp.status_code == 200:
            logs = resp.json()
            if any(email in str(log) for log in logs):
                return True
        time.sleep(POLLING_ESPERA)
    return False


def _limpiar_empleado(email):
    """Elimina el empleado creado durante la prueba."""
    try:
        resp = requests.get(f"{EMPLOYEES_URL}/employee/all/")
        if resp.status_code == 200:
            empleados = resp.json()
            for emp in empleados:
                if emp.get("email") == email or emp.get("emailEmployee") == email:
                    id_emp = emp.get("id_employee") or emp.get("idEmployee")
                    if id_emp:
                        requests.delete(f"{EMPLOYEES_URL}/employee/delete/{id_emp}")
    except Exception:
        pass


# ── STEPS: DADO ───────────────────────────────────────────────────────────────

@given('que existe un empleado registrado con email "{email}"')
def step_empleado_existente(context, email):
    context.email_prueba = email
    resp = _crear_empleado(email, id_empleado=90002)
    assert resp.status_code in [200, 201], (
        f"No se pudo crear el empleado previo. Código: {resp.status_code}. "
        f"Detalle: {resp.text}"
    )
    creado = _polling_usuario_creado(email)
    assert creado, f"El usuario '{email}' no apareció en el auth-service tras esperar."


# ── STEPS: CUANDO ─────────────────────────────────────────────────────────────

@when('registro un nuevo empleado con email "{email}"')
def step_registrar_empleado(context, email):
    context.email_prueba = email
    resp = _crear_empleado(email, id_empleado=90001)
    assert resp.status_code in [200, 201], (
        f"No se pudo registrar el empleado. Código: {resp.status_code}. "
        f"Detalle: {resp.text}"
    )


@when('el empleado solicita recuperar su contraseña')
def step_recuperar_contrasena(context):
    resp = requests.post(
        f"{AUTH_URL}/auth/recover-password",
        json={"email": context.email_prueba}
    )
    assert resp.status_code == 200, (
        f"Error al solicitar recuperación. Código: {resp.status_code}. "
        f"Detalle: {resp.text}"
    )
    context.reset_token = resp.json().get("resetToken")
    assert context.reset_token, "No se recibió resetToken en la respuesta."


@when('establece su nueva contraseña "{nueva_password}"')
def step_establecer_contrasena(context, nueva_password):
    context.nueva_password = nueva_password
    resp = requests.post(
        f"{AUTH_URL}/auth/reset-password",
        json={"token": context.reset_token, "newPassword": nueva_password}
    )
    assert resp.status_code == 200, (
        f"Error al establecer contraseña. Código: {resp.status_code}. "
        f"Detalle: {resp.text}"
    )


@when('intento registrar un empleado con email inválido "{email}"')
def step_registrar_email_invalido(context, email):
    context.respuesta_api = _crear_empleado(email, id_empleado=90003)


# ── STEPS: ENTONCES ───────────────────────────────────────────────────────────

@then('el sistema crea las credenciales del empleado en el auth-service')
def step_verificar_credenciales(context):
    creado = _polling_usuario_creado(context.email_prueba)
    assert creado, (
        f"El usuario '{context.email_prueba}' no fue creado en el auth-service "
        f"tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )


@then('el sistema registra el evento de onboarding en los logs')
def step_verificar_log(context):
    encontrado = _polling_log_creado(context.email_prueba)
    assert encontrado, (
        f"No se encontró log para '{context.email_prueba}' en service-logs "
        f"tras {POLLING_INTENTOS * POLLING_ESPERA} segundos."
    )


@then('puede autenticarse exitosamente con su nueva contraseña')
def step_autenticar_nueva_contrasena(context):
    resp = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"email": context.email_prueba, "password": context.nueva_password}
    )
    assert resp.status_code == 200, (
        f"No se pudo autenticar con la nueva contraseña. "
        f"Código: {resp.status_code}. Detalle: {resp.text}"
    )
    token = resp.json().get("token") or resp.json().get("accessToken")
    assert token, "Login exitoso pero no se recibió token."


@then('el registro es rechazado con un error')
def step_registro_rechazado(context):
    assert context.respuesta_api.status_code in [400, 422, 500], (
        f"Se esperaba un error pero el servidor respondió con "
        f"{context.respuesta_api.status_code}. Detalle: {context.respuesta_api.text}"
    )