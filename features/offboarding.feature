# language: es
Característica: Offboarding de empleados
  Como sistema de gestión de empleados
  Quiero limitar el acceso a los servicios de la plataforma
  A los empleados que por una u otra razón hayan sido desvinculados de la aplicación

  Antecedentes:
    Dado que el sistema está desplegado y operativo
    Y que existe un empleado activo con credenciales configuradas

  Escenario: Desvinculación completa genera notificación asincrónica
    Cuando elimino al empleado del sistema
    Entonces el usuario queda deshabilitado en el auth-service
    Y el sistema registra el evento de desvinculación en los logs

  Escenario: El empleado desvinculado no puede hacer login
    Cuando elimino al empleado del sistema
    Entonces el empleado no puede autenticarse en el sistema

  Escenario: La recuperación de contraseña falla para un empleado desvinculado
    Cuando elimino al empleado del sistema
    Entonces la recuperación de contraseña falla para el empleado desvinculado