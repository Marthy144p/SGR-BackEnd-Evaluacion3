# Sistema de Gestión de Resultados (SGR) - Evaluación 3 de Back End

**Caso:** SGR municipal, La Serena, Chile. **Integrante y desarrollo:** Martin Aguilera Arismendi. **Modalidad informada:** grupal; en esta entrega el proyecto se trabaja individualmente. **Datos:** todos los ejemplos nuevos son ficticios. **Asignatura:** Programación Back End, Unidad 2. **Estado del paquete:** código y pruebas locales preparados; **NO se ha comprobado ni realizado el despliegue en AWS**.

## 1. Alcance y estado de la entrega

El proyecto continúa **Aguilera_BackEnd_Evaluacion2.zip** y la ampliación del Paso 1. Conserva las aplicaciones Django `organizacion`, `actividades`, `agenda` y `resultados`, la lógica del prototipo JSON de evaluaciones anteriores, los modelos históricos `Delegacion`, `Rol`, `PerfilUsuario`, `Item`, `TipoAtencion` y `SubAtencion` y sus migraciones. Añade la app `gestion`, que ofrece el CRUD web con ModelForm y plantillas propias para las **17 entidades obligatorias**. Django Admin se mantiene para la administración del servidor, pero **no** sustituye las pantallas web propias.

### Entidades (17)

| Área | Entidades |
|---|---|
| Organización | Delegación, Territorio, Usuario funcionario (`PerfilUsuario`), Cargo, Rol, Vecino, Junta de vecinos, Participación en junta |
| Agenda | Hito |
| Actividades | Actividad, Gestión social, Tipo de atención, Subtipo de atención (`SubAtencion`), Evidencia |
| Resultados | Meta, Asignación de meta, Trimestre |

`Item` se conserva por compatibilidad con la Evaluación 2, pero **no cuenta** entre las 17 entidades. Las URL del nuevo CRUD son `/gestion/<modulo>/`; `/organizacion/`, `/actividades/`, `/agenda/`, `/resultados/` agrupan las entidades. Se mantienen las páginas JSON heredadas bajo `/prototipo/` **protegidas por autenticación y permisos de consulta**; no son sustitutos del CRUD de la Evaluación 3.

### Operaciones

Cada una de las 17 entidades ofrece listado, detalle, creación, edición y desactivación/anulación con confirmación (páginas HTML propias y métodos HTTP correctos). Las ediciones conservan el identificador; `is_valid()` impide guardar formularios inválidos. **La eliminación es lógica:** los modelos con `activo` pasan a `False`, los modelos con `estado` pasan a `anulado/anulada` y `PerfilUsuario` desactiva `User.is_active`. Esto conserva referencias, evidencia, historial y el identificador de los registros. El método GET de confirmación y el enlace Cancelar **no alteran datos**; únicamente POST con CSRF cambia el estado. No se elimina físicamente información histórica.

### Seguridad

Todas las rutas de los módulos requieren usuario autenticado. Django `LoginView` y `LogoutView` implementan acceso y salida por POST. Sin sesión se redirige a login; sin permisos Django, **403 incluso por URL directa**. Las rutas CRUD validan `view/add/change/delete` del modelo real en servidor. `Consulta` solo ve listados y detalles de las 17 entidades; `Gestión` puede consultar, crear, modificar y desactivar. Los enlaces se ocultan según permisos. Las contraseñas se manejan con el sistema `User.set_password()`, nunca en campos propios de texto. `FuncionarioForm` **no permite modificar** `is_staff`, `is_superuser`, grupos ni permisos; `RolForm` no concede privilegios ni expone `grupo`. Los privilegios se administran únicamente desde Django Admin o consola segura. Una cuenta de staff o superusuario tampoco puede editarse/desactivarse desde el CRUD general.

## 2. Modelo de datos y decisiones de relaciones

- `Delegacion` tiene territorios, delegado opcional vinculado a `PerfilUsuario`, y funcionarios; el delegado es opcional inicialmente para permitir la carga de datos circulares: primero se registra la delegación, después el funcionario y finalmente se asigna el delegado. Se valida que el funcionario pertenezca a esa delegación.
- `Territorio` está ligado a una delegación; `Vecino` a un territorio; `JuntaVecinos` a delegación y territorio, con coherencia validada; `ParticipacionJunta` es la entidad intermedia explícita de vecino y junta.
- `PerfilUsuario` conserva una relación `OneToOne` con `User` de Django, `cargo` y `delegacion` y `rol` principal original, más `roles` adicionales. El estado y último login se obtienen desde `User` de Django.
- `Rol.grupo` enlaza al `Group` de Django para consulta; **los permisos efectivos los concede la pertenencia al grupo Django**, nunca el nombre o el estado de un `Rol`. Inactivar un rol de catálogo no cambia permisos ni membresías: los cambios de permisos se administran por separado, en una función protegida.
- `SubAtencion` pertenece a `TipoAtencion`; `GestionSocial` obliga a seleccionar un subtipo compatible con su tipo.
- `Hito` pertenece a una delegación/territorio y tiene responsables; `Actividad` está ligada a funcionario, asignación, territorio, responsable y opcionalmente hito/vecino. Se valida coherencia territorial y asignación con funcionario.
- `Meta` contiene definición y unidad; **cantidad objetivo** y **ponderación** se almacenan en `AsignacionMeta`, junto con funcionario/trimestre. `Trimestre` controla año, número 1..4 y fechas.
- `Evidencia` apunta **exactamente a una** actividad o gestión social; se valida en el modelo y con restricción de base. Guarda únicamente metadatos ficticios (no carga de archivos).
- Todas las referencias históricas usan `on_delete=PROTECT` donde corresponde. Los datos anteriores conservan ID y sus migraciones útiles.

## 3. Validaciones

Validación en servidor con ModelForm y modelos: campos obligatorios, correo válido, longitud, unicidad de códigos/RUT, tipos y opciones; `fecha_termino >= fecha_inicio`, `fecha_compromiso >= fecha`, `fecha_atencion >= fecha_ingreso`, ponderación 0..100, cantidad objetivo > 0, trimestre 1..4, territorialidad delegación/territorio, beneficiario y subtipo compatibles. Errores legibles con datos rellenados en el mismo formulario. No se calcula cumplimiento ni se obliga a suma de ponderaciones.

## 4. Versiones y dependencias

Versiones fijadas en `requirements.txt`: **Django 5.0.14**, **mysqlclient 2.3.0**, **Gunicorn 23.0.0**; resto de dependencias según ese archivo. Configuración del proyecto: MySQL/MariaDB, charset `utf8mb4`. La evaluación anterior documentaba Python **3.12 Windows / 3.11.16 AWS**, MySQL **8.4.11 AWS**, Nginx **1.30.5**, Amazon Linux 2023; esas son **versiones históricas declaradas**, no verificadas en el servidor actual. Se recomienda confirmar sus versiones instaladas antes de desplegar. Usar combinaciones de versiones compatibles, con mysqlclient compilado para el servidor.

## 5. Instalación en Windows (MySQL / WAMP)

1. Respaldar **antes** de sustituir archivos o aplicar cambios sobre una base existente. Descomprimir el ZIP completo en otra carpeta; no borrar el proyecto anterior.
2. Crear y activar entorno virtual desde la carpeta que contiene `manage.py`:

   ```powershell
   py -m venv entorno
   .\entorno\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
3. En MySQL crear una base (solo si no existe): `CREATE DATABASE IF NOT EXISTS sgr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`. Disponer de usuario con permisos sobre esa base.
4. Configurar variables de entorno en **la misma terminal** (no publicar claves):

   ```powershell
   $env:DJANGO_DEBUG='True'
   $env:DJANGO_SECRET_KEY='clave-local-generada-para-pruebas-no-produccion'
   $env:DB_NAME='sgr_db'
   $env:DB_USER='USUARIO_MYSQL'
   $env:DB_PASSWORD='CONTRASENA_MYSQL'
   $env:DB_HOST='127.0.0.1'
   $env:DB_PORT='3306'
   ```
5. **Con respaldo hecho**, aplicar las migraciones ya incluidas (no borrar las históricas):

   ```powershell
   python manage.py check
   python manage.py makemigrations --check --dry-run
   python manage.py migrate
   python manage.py preparar_permisos_sgr
   python manage.py cargar_demo_sgr
   python manage.py runserver
   ```
6. El comando `cargar_demo_sgr` añade dos ejemplos ficticios por entidad y dos cuentas normales `sgr_demo_consulta` y `sgr_demo_gestion`. Sus claves nuevas **se muestran una única vez en la terminal** y NO se incluyen en el ZIP. Puedes definir `SGR_CONSULTA_PASSWORD` y `SGR_GESTION_PASSWORD` antes de ejecutar la carga. El comando es idempotente y **no restablece claves existentes** salvo que se indique `--restablecer-claves`.
7. Abrir `http://127.0.0.1:8000/` y acceder con las cuentas demo. Si ya había datos históricos, seguirán estando disponibles; se agregan registros DEMO separados.

### Pruebas automatizadas, sin MySQL real

```powershell
python manage.py test --settings=sgr.settings_pruebas
```

Se usa SQLite **solo como base aislada de pruebas**. No sustituye el requisito de MySQL en desarrollo/producción. Para una demostración persistente, sin tocar MySQL, existe `sgr.settings_demo` con `demo_local.sqlite3` (EXCLUSIVAMENTE LOCAL):

```powershell
python manage.py migrate --settings=sgr.settings_demo
python manage.py cargar_demo_sgr --settings=sgr.settings_demo
python manage.py runserver --settings=sgr.settings_demo
```

## 6. Despliegue AWS - pendiente de validación real

**Dirección referenciada en la Evaluación 2:** `https://100.60.3.98/admin/` (aportada por el estudiante). No se ha comprobado desde este entorno que actualmente responda ni que el certificado HTTPS esté vigente. La Evaluación 3 exige **el mismo código en AWS** y base persistente; la preparación local no acredita este criterio.

Procedimiento recomendado (adaptar rutas y usuarios a tu instalación real):

1. En la EC2, confirmar `python3 --version`, MySQL/mariadb, Gunicorn, Nginx, dominio/IP actual, HTTPS y servicios. Respaldar la base **antes** de cambios, p. ej. `mysqldump -u USUARIO_SGR -p --single-transaction --routines sgr_db > respaldo_sgr_antes_e3.sql` en una ruta protegida. No poner contraseñas en comandos públicos ni compartir el respaldo.
2. Subir el código nuevo al directorio de despliegue **sin** reemplazar `.env`/credenciales, entorno virtual existente, configuraciones de servicio ni archivos históricos hasta verificar respaldos. Crear una carpeta de versión nueva si es posible.
3. Instalar dependencias Python con el entorno que utiliza Gunicorn: `python -m pip install -r requirements.txt` (puede requerir paquetes de desarrollo de MySQL para compilar mysqlclient).
4. Configurar `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` seguro, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` (orígenes completos con `https://`), `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` en entorno **fuera** del repositorio. Las cookies serán Secure, y la redirección HTTPS depende de proxy HTTPS correcto en Nginx (`X-Forwarded-Proto`). Confirmar los certificados antes de activar.
5. **Tras respaldar:** `python manage.py check --deploy`, `python manage.py migrate`, `python manage.py preparar_permisos_sgr`, `python manage.py cargar_demo_sgr`, `python manage.py collectstatic --noinput`.
6. Reiniciar con el nombre **real** del servicio Gunicorn usado por tu instancia y recargar Nginx tras validar su configuración; revisar logs, HTTPS, rutas `/cuentas/login/` y `/gestion/`, base persistente, estáticos, CSRF, login/logout, permisos. Probar con cuentas normales Consulta/Gestión, no solo un superusuario.
7. Repetir el plan de pruebas indicado en `Evidencias.pdf` y añadir **capturas reales desde AWS**. Entregar cuentas de prueba y claves por canal privado del docente, nunca en README ni repositorios públicos.

## 7. Datos de prueba y reproducción

Comando `cargar_demo_sgr` carga entidades relacionadas con códigos prefijados `DEMO-E3`; incluye un vecino inactivo, 2 funcionarios normales y 2 evidencias que apuntan a orígenes distintos. Se incluyen pruebas automatizadas para operaciones CRUD sobre **cada entidad** que crean registros desechables, editan sin cambiar ID y los desactivan. Si ejecutas el comando varias veces conserva los registros ya presentes (las claves de cuentas preexistentes no cambian).

## 8. Evidencias y pruebas

`Evidencias.pdf` muestra matriz de entidades y resultados de pruebas **locales**, capturas locales si disponibles y un apartado de pruebas **pendientes de ejecutar en AWS**. No se deben presentar capturas locales como si fuesen de AWS. Repetir manualmente con sesiones reales: crear, listar, ver detalle, editar, desactivar, cancelar, POST/CSRF, 403, 404, datos inválidos, relaciones y persistencia tras recargar.

## 9. Decisiones, diferencias y apoyo de IA

- Eval. 2: el CRUD persistente usaba Django Admin sobre seis modelos. Eval. 3: interfaz CRUD propia para 17 entidades y permisos diferenciados; conserva las tablas útiles, modelos anteriores y prototipo histórico JSON separado. El ZIP incorpora migraciones que preservan los IDs. `Rol` recibe códigos únicos vía migración de datos antes de hacerse obligatorio.
- La eliminación es **lógica en todas las entidades**; evita rotura de vínculos y conserva antecedentes históricos. `Delegacion.delegado`, `PerfilUsuario.cargo` y `PerfilUsuario.rut` son opcionales por compatibilidad con datos anteriores, pero se pueden completar con formularios.
- **Uso de IA:** se utilizó ChatGPT para asistir en análisis de instrucciones, generación de código Python, plantillas, pruebas y documentación. Las pruebas automatizadas locales sirven para revisar rutas, permisos y validaciones. Se debe realizar una última verificación manual del código y del despliegue AWS antes de entregar. El responsable de la presentación debe comprender modelos, ModelForm, migraciones, CRUD y seguridad.

## 10. Entregables

Este ZIP incluye código, migraciones, HTML, CSS, dependencias, README, `Evidencias.pdf`, scripts de datos/pruebas y notas de instalación. Excluye deliberadamente entornos virtuales, caches, bases de datos locales, contraseñas reales, secretos y datos no ficticios. Para completar la entrega académica, **actualizar las evidencias de AWS** después de desplegar en el servidor.
