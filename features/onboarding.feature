# language: es
Característica: Onboarding de empleados
  Como sistema de gestión de empleados
  Quiero registrar nuevos empleados y crear sus credenciales automáticamente
  Para que puedan acceder al sistema tras su incorporación

  Antecedentes:
    Dado que el sistema está desplegado y operativo

  Escenario: Registro exitoso de empleado genera usuario en el sistema
    Cuando registro un nuevo empleado con email "bdd.test.onboarding@empresa.com"
    Entonces el sistema crea las credenciales del empleado en el auth-service
    Y el sistema registra el evento de onboarding en los logs

  Escenario: El empleado puede establecer su contraseña y autenticarse
    Dado que existe un empleado registrado con email "bdd.test.login@empresa.com"
    Cuando el empleado solicita recuperar su contraseña
    Y establece su nueva contraseña "NuevaPass123!"
    Entonces puede autenticarse exitosamente con su nueva contraseña

  Escenario: Registro con email inválido es rechazado
    Cuando intento registrar un empleado con email inválido "esto-no-es-un-email"
    Entonces el registro es rechazado con un error