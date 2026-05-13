import requests
from behave import given, when, then


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _headers_con_token(token):
    return {"Authorization": f"Bearer {token}"}


# ── STEPS: CUANDO ─────────────────────────────────────────────────────────────

@when('consulto un recurso protegido sin token de autenticación')
def step_consultar_sin_token(context):
    url = f"{context.base_url}/empleados/"
    context.respuesta_api = requests.get(url)


@when('consulto un recurso protegido con el token "{token_invalido}"')
def step_consultar_con_token_invalido(context, token_invalido):
    url = f"{context.base_url}/empleados/"
    headers = {"Authorization": f"Bearer {token_invalido}"}
    context.respuesta_api = requests.get(url, headers=headers)


@when('me autentico con email "{email}" y contraseña "{contrasena}"')
def step_autenticar(context, email, contrasena):
    url = f"{context.base_url}/auth/login"
    payload = {"email": email, "password": contrasena}
    context.respuesta_api = requests.post(url, json=payload)


# ── STEPS: ENTONCES ───────────────────────────────────────────────────────────

@then('la respuesta debe tener código {codigo:d}')
def step_verificar_codigo(context, codigo):
    codigo_real = context.respuesta_api.status_code
    assert codigo_real == codigo, (
        f"Se esperaba código {codigo} pero el servidor respondió con {codigo_real}. "
        f"Detalle: {context.respuesta_api.text}"
    )


@then('la respuesta debe contener un token')
def step_verificar_token(context):
    data = context.respuesta_api.json()
    token = data.get("token") or data.get("accessToken") or data.get("access_token")
    assert token is not None, (
        f"Se esperaba un token en la respuesta pero no se encontró. "
        f"Respuesta: {context.respuesta_api.text}"
    )
    assert len(token) > 20, "El token parece demasiado corto para ser válido"