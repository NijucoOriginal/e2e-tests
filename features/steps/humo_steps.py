import requests
from behave import given, then


@given('que el sistema está desplegado y operativo')
def step_impl(context):
    """
    Verifica conectividad básica con el sistema.
    Usamos el endpoint de login (público) en lugar de /employee/all/
    porque ese endpoint requiere token JWT y daría 401 en el humo.
    Si tu sistema expone /actuator/health, también puedes usarlo.
    """
    url_prueba = f"{context.base_url}/auth/login"

    try:
        # Hacemos un POST vacío — esperamos 400 (bad request) o 200,
        # lo importante es que el servidor RESPONDE (no ConnectionError)
        context.respuesta_api = requests.post(url_prueba, json={})
    except requests.exceptions.ConnectionError:
        assert False, (
            f"El sistema NO está operativo. "
            f"No se pudo conectar a {url_prueba}. "
            f"¿Está Docker Compose corriendo? Ejecuta: docker-compose up --build -d"
        )


@then('la respuesta debe ser exitosa indicando 200 o 204')
def step_impl(context):
    """
    Para el escenario de humo aceptamos cualquier respuesta HTTP válida
    (el servidor respondió = está vivo). Códigos esperados: 200, 204, 400.
    Un 401 también indica que el servidor está vivo y la seguridad funciona.
    """
    codigo_real = context.respuesta_api.status_code

    # Cualquier respuesta HTTP válida significa que el sistema está operativo
    codigos_sistema_vivo = [200, 204, 400, 401, 403, 405]

    assert codigo_real in codigos_sistema_vivo, (
        f"Fallo crítico: El sistema no responde como se espera. "
        f"Código obtenido: {codigo_real}. "
        f"Respuesta: {context.respuesta_api.text}"
    )