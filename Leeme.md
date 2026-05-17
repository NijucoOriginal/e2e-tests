# E2E Tests - Reto 5 BDD

## ¿Qué es BDD y por qué se eligió este enfoque?

BDD por sus siglas en inglés Behavior Driven Development, en español Desarrollo Guiado Por Comportamiento, es una metodología ágil que busca integrar a los stakeholders y desarrolladores con el área de pruebas, a través de la conversión de lenguaje natural a código de pruebas completamente funcionales.

El uso de lenguaje natural para la definición de pruebas permite a los desarrolladores y stakeholders entender más fácilmente el flujo del negocio, lo que facilita la comprensión del funcionamiento de la aplicación, facilitando la comunicación entre las diferentes partes involucradas en el desarrollo, siendo lo mencionado anteriormente el principal motivo por el cual este enfoque fue seleccionado.

---

## Prerrequisitos

Para la ejecución de las pruebas funcionales se necesitan las siguientes tecnologías:

- **Docker Desktop**: aplicación de gestión de contenedores.
- **Python 3.13**: intérprete de Python.

El resto de dependencias se instalan automáticamente al ejecutar el archivo `run_tests.py`:
- `behave==1.2.6`
- `requests==2.31.0`
- `python-dotenv==1.0.1`
- `bcrypt==4.1.2`

### Puertos disponibles
Los siguientes puertos deben estar libres antes de levantar el sistema:

| Puerto | Servicio |
|--------|----------|
| 8081 | employee-backend |
| 8083 | department_backend |
| 8085 | microservice-logs |
| 8086 | auth-service |
| 5095 | management-profile |
| 5433/5446 | PostgreSQL |
| 3307 | MySQL |
| 27017 | MongoDB |
| 5672/15672 | RabbitMQ |

---

## Instrucciones de ejecución

### a. Cómo levantar el sistema

Dentro de la carpeta raíz del proyecto principal `challenges-microservices`, ejecutar:

```bash
docker-compose up --build -d
```

Esperar aproximadamente 60 segundos hasta que todos los servicios estén corriendo. Para verificar:

```bash
docker ps
```

Todos los contenedores deben aparecer con estado `healthy` o `Up`.

### b. Problema con RabbitMQ

Si RabbitMQ no inicia correctamente, ejecutar los siguientes comandos en orden:

```powershell
# 1. Bajar los contenedores
docker-compose down

# 2. Eliminar volúmenes anónimos corruptos
docker volume ls --filter dangling=true -q | ForEach-Object { docker volume rm $_ }

# 3. Levantar de nuevo
docker-compose up -d
```

### c. Cómo configurar las variables de entorno

Crear un archivo `.env` en la carpeta raíz de `e2e-tests` con el siguiente contenido:

```
BASE_URL=http://localhost:8086
ADMIN_USER=admin@empresa.com
ADMIN_PASS=admin123
USER_USER=empleado@test.com
USER_PASS=user123
```

### d. Comando para ejecutar las pruebas

Dentro de la carpeta raíz `e2e-tests`, ejecutar:

```bash
python run_tests.py
```

Este comando automáticamente:
1. Instala las dependencias del `requirements.txt`
2. Inserta los datos base en la base de datos (usuarios y departamentos)
3. Ejecuta la suite completa 3 veces consecutivas
4. Muestra un resumen de consistencia

---

## Cómo interpretar los resultados

Al finalizar cada ejecución, Behave muestra un resumen con el siguiente formato:

```
X features passed, X failed, X skipped
X scenarios passed, X failed, X skipped
X steps passed, X failed, X skipped, X undefined
```

### Significado de cada campo

- **features passed**: número de archivos `.feature` que pasaron completamente
- **scenarios passed**: número de escenarios individuales que pasaron
- **steps passed**: número de pasos individuales ejecutados correctamente
- **failed**: indica que algo falló — el mensaje de error aparece directamente bajo el step fallido
- **skipped**: pasos que no se ejecutaron porque un paso anterior falló

### Ejemplo de escenario exitoso
```
Escenario: Registro exitoso de empleado genera usuario en el sistema
  Dado que el sistema está desplegado y operativo         ✓
  Cuando registro un nuevo empleado                       ✓
  Entonces el sistema crea las credenciales               ✓
```

### Ejemplo de escenario fallido
```
Escenario: Usuario con rol USER puede autenticarse
  Cuando me autentico con email "empleado@test.com"       ✓
  Entonces la respuesta debe tener código 200             ✗
    Assertion Failed: Se esperaba código 200 pero el servidor respondió con 403.
```

El mensaje de error indica claramente qué se esperaba y qué se obtuvo.

### Resumen de consistencia
Al finalizar las 3 ejecuciones, `run_tests.py` muestra:

```
==================================================
RESUMEN DE CONSISTENCIA
==================================================
Ejecución 1: ✅ PASÓ
Ejecución 2: ✅ PASÓ
Ejecución 3: ✅ PASÓ

✅ Suite consistente - todas las ejecuciones pasaron
```

---

## Descripción de los escenarios implementados

### Punto 1 — Prueba de humo (`humo.feature`)
Verifica que el sistema está operativo antes de ejecutar cualquier prueba.

| Escenario | Flujo cubierto |
|-----------|---------------|
| El sistema responde correctamente | Llama a `POST /auth/login` y verifica que el sistema responde con 200 o 204 |

### Punto 2 — Seguridad (`seguridad.feature`)
Verifica el control de acceso y autenticación del sistema.

| Escenario | Flujo cubierto |
|-----------|---------------|
| Acceso denegado sin token | Llama a un recurso protegido sin token y verifica 403 |
| Acceso denegado con token malformado | Envía un JWT inválido y verifica 403 |
| Usuario USER puede autenticarse | Login con `empleado@test.com` y verifica token en respuesta |
| Usuario ADMIN puede autenticarse | Login con `admin@empresa.com` y verifica token en respuesta |

### Punto 3 — Onboarding (`onboarding.feature`)
Verifica el flujo completo de registro de empleados.

| Escenario | Flujo cubierto |
|-----------|---------------|
| Registro exitoso genera usuario | Crea empleado → RabbitMQ → auth-service crea usuario → service-logs registra evento |
| Empleado establece contraseña y se autentica | Crea empleado → recover-password → reset-password → login exitoso |
| Email inválido es rechazado | Intenta crear empleado con email inválido y verifica error |

### Punto 4 — Offboarding (`offboarding.feature`)
Verifica el flujo completo de desvinculación de empleados.

| Escenario | Flujo cubierto |
|-----------|---------------|
| Desvinculación genera notificación | Elimina empleado → RabbitMQ → auth-service deshabilita usuario → service-logs registra evento |
| Empleado desvinculado no puede hacer login | Elimina empleado → intenta login → verifica 403 |
| Recuperación de contraseña falla | Elimina empleado → intenta recover-password → verifica error |

---

## Herramientas y frameworks utilizados

### Behave
**Versión:** 1.2.6  
**Justificación:** Framework BDD para Python que permite escribir pruebas en lenguaje natural usando la sintaxis Gherkin (Dado/Cuando/Entonces). Se eligió porque integra directamente con Python, tiene soporte nativo para español con `# language: es`, y permite reutilizar steps entre diferentes features.

### Requests
**Versión:** 2.31.0  
**Justificación:** Librería HTTP para Python que permite hacer llamadas REST a los microservicios de forma simple e intuitiva. Se eligió por su simplicidad y amplia documentación.

### Python-dotenv
**Versión:** 1.0.1  
**Justificación:** Permite cargar variables de entorno desde un archivo `.env`, facilitando la configuración de URLs y credenciales sin hardcodearlas en el código.

### Bcrypt
**Versión:** 4.1.2  
**Justificación:** Librería para generar hashes BCrypt compatibles con Spring Security. Se usa en el `environment.py` para insertar usuarios con contraseñas correctamente hasheadas en PostgreSQL antes de cada ejecución.

### Subprocess (built-in Python)
**Justificación:** Módulo nativo de Python usado para ejecutar comandos de Docker directamente desde los steps. Se usa para hacer polling a PostgreSQL con `docker exec psql` cuando el auth-service no expone endpoints para consultar el estado de los usuarios.