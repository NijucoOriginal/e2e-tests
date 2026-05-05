import requests
from behave import given, then


@given('que el sistema está desplegado y operativo')
def step_impl(context):
    # Usamos la ruta real de tu controlador Java
    url_prueba = f"{context.base_url}/employee/all/"

    try:
        # Ejecutamos la petición GET y la guardamos en la mochila
        context.respuesta_api = requests.get(url_prueba)
    except requests.exceptions.ConnectionError:
        # Si Docker está apagado, avisamos claramente
        assert False, f"El sistema NO está operativo. No se pudo conectar a {url_prueba}"


@then('la respuesta debe ser exitosa indicando 200 o 204')
def step_impl(context):
    # Extraemos el código real que devolvió Spring Boot
    codigo_real = context.respuesta_api.status_code

    # Definimos cuáles son los códigos que consideramos como "éxito" para esta prueba
    codigos_exitosos = [200, 204]

    # El juez (assert) verifica si el código real está dentro de nuestra lista permitida
    assert codigo_real in codigos_exitosos, \
        f"Fallo crítico: Se esperaba 200 o 204, pero Spring Boot respondió con {codigo_real}. Detalle: {context.respuesta_api.text}"