# language: es
Característica: Seguridad y control de acceso
  Como sistema de autenticación
  Quiero controlar el acceso a los recursos
  Para garantizar que solo los usuarios autorizados realicen operaciones

  Antecedentes:
    Dado que el sistema está desplegado y operativo

  # ── ESCENARIO 1 (dado por el enunciado) ─────────────────────────────────────
  Escenario: Acceso denegado sin token de autenticación
    Cuando consulto un recurso protegido sin token de autenticación
    Entonces la respuesta debe tener código 403

  # ── ESCENARIO 2 ──────────────────────────────────────────────────────────────
  Escenario: Acceso denegado con token malformado
    Cuando consulto un recurso protegido con el token "esto.no.es.un.jwt.valido"
    Entonces la respuesta debe tener código 403

  # ── ESCENARIO 3 ──────────────────────────────────────────────────────────────
  # Verifica que un usuario con rol USER puede autenticarse exitosamente.
  # El sistema debe responder con código 200 y retornar un token JWT válido.
  # Este escenario cubre el flujo normal de autenticación para usuarios regulares.
  @fallo-simulado
  Escenario: Usuario con rol USER puede autenticarse exitosamente
    Cuando me autentico con email "empleado@test.com" y contraseña "user123"
    Entonces la respuesta debe tener código 200
    Y la respuesta debe contener un token

  # ── ESCENARIO 3 SIMULACIÓN DE FALLO ──────────────────────────────────────────
  # Este escenario demuestra cómo se ve un fallo descriptivo en Behave.
  # Se modificó el código esperado de 200 a 404 para simular un fallo.
  # Mensaje esperado: "Se esperaba código 404 pero el servidor respondió con 200"
  Escenario: Usuario con rol USER puede autenticarse exitosamente - FALLO SIMULADO
    Cuando me autentico con email "empleado@test.com" y contraseña "user123"
    Entonces la respuesta debe tener código 404
    Y la respuesta debe contener un token

  # ── ESCENARIO 4 ──────────────────────────────────────────────────────────────
  Escenario: Usuario con rol ADMIN puede autenticarse exitosamente
    Cuando me autentico con email "admin@empresa.com" y contraseña "admin123"
    Entonces la respuesta debe tener código 200
    Y la respuesta debe contener un token