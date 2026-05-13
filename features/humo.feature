# language: es
Característica: Verificación del sistema
  Como equipo de desarrollo
  Quiero verificar que el sistema está operativo
  Para confirmar que Docker Compose levantó todos los servicios correctamente

  Escenario: El sistema responde correctamente
    Dado que el sistema está desplegado y operativo
    Entonces la respuesta debe ser exitosa indicando 200 o 204
