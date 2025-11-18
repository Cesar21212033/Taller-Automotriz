# 🚗 Taller Automotriz - Sistema Web Flask

Sistema web completo para gestión de taller automotriz desarrollado con **Flask (Python)** y **MySQL**. Permite gestionar servicios, citas, cotizaciones, usuarios y más.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación desde Cero](#-instalación-desde-cero)
- [Configuración](#-configuración)
- [Ejecución](#-ejecución)
- [Credenciales por Defecto](#-credenciales-por-defecto)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Solución de Problemas](#-solución-de-problemas)

## 🚀 Características

### Sitio Web Público
- ✅ Página de inicio con información del taller
- ✅ Catálogo de servicios ofrecidos
- ✅ Sistema de solicitud de cotizaciones personalizadas
- ✅ Agendamiento de citas en línea con validación de horarios
- ✅ Información de contacto

### Panel de Usuario
- ✅ Dashboard personalizado
- ✅ Visualización de citas agendadas
- ✅ Historial de cotizaciones solicitadas
- ✅ Seguimiento de estatus de citas

### Panel Administrativo
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión completa de usuarios (crear, editar, eliminar, cambiar contraseña)
- ✅ Gestión de servicios ofrecidos
- ✅ Gestión de roles y permisos
- ✅ Configuración de precios personalizados por servicio
- ✅ Gestión de citas y cotizaciones
- ✅ Sistema de autenticación seguro
- ✅ Envío automático de correos electrónicos

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior** (recomendado Python 3.10+)
  - Verificar versión: `python --version` o `python3 --version`
- **MySQL 5.7+** o **MariaDB 10.3+**
  - Verificar que MySQL esté instalado y ejecutándose
- **Git** (para clonar el repositorio)
- **pip** (gestor de paquetes Python, incluido con Python)

## 🔧 Instalación desde Cero

### Paso 1: Clonar el Repositorio

Abre tu terminal (PowerShell en Windows, Terminal en Mac/Linux) y ejecuta:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Taller-Automotriz
```

**Nota:** Reemplaza `<URL_DEL_REPOSITORIO>` con la URL real de tu repositorio en GitHub.

### Paso 2: Crear Entorno Virtual

Es importante usar un entorno virtual para aislar las dependencias del proyecto:

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Paso 3: Activar el Entorno Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**✅ Verificación:** Deberías ver `(venv)` al inicio de tu línea de comandos cuando esté activado.

### Paso 4: Instalar Dependencias

Con el entorno virtual activado, instala todas las dependencias necesarias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencias que se instalarán:**
- Flask 3.0.0
- mysql-connector-python 8.2.0
- Werkzeug 3.0.1
- Flask-Mail 0.9.1
- python-dotenv 1.0.0
- reportlab 4.0.7
- bcrypt 4.1.2

### Paso 5: Configurar Base de Datos

1. **Abrir MySQL Workbench** (o tu cliente MySQL preferido)

2. **Conectarte a tu servidor MySQL** con tus credenciales

3. **Ejecutar el script SQL:**
   - Abre el archivo: `base de datos/servicio_automotriz.sql`
   - Ejecuta todo el script (botón ⚡ o `Ctrl+Shift+Enter`)
   - Verifica que la base de datos `servicio_automotriz` se haya creado correctamente

4. **Verificar tablas creadas:**
   ```sql
   USE servicio_automotriz;
   SHOW TABLES;
   ```
   
   Deberías ver tablas como: `usuarios`, `roles`, `servicios`, `citas`, `cotizaciones`, etc.

### Paso 6: Configurar Conexión a MySQL

Edita el archivo `app.py` y busca la sección `DB_CONFIG` (alrededor de la línea 71):

```python
DB_CONFIG = {
    'host': 'localhost',              # Cambiar si MySQL está en otro servidor
    'database': 'servicio_automotriz', # Nombre de la base de datos
    'user': 'root',                   # Tu usuario de MySQL
    'password': 'TU_CONTRASEÑA',      # ⚠️ Cambiar por tu contraseña de MySQL
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}
```

**⚠️ IMPORTANTE:** Reemplaza `'TU_CONTRASEÑA'` con tu contraseña real de MySQL.

## ▶️ Ejecución

### Ejecutar el Servidor de Desarrollo

1. **Asegúrate de tener el entorno virtual activado** (deberías ver `(venv)` en tu terminal)

2. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

3. **Abre tu navegador** y visita:
   ```
   http://localhost:5000
   ```

4. **Deberías ver** la página de inicio del taller automotriz.

### Detener el Servidor

Presiona `Ctrl + C` en la terminal para detener el servidor.

## 🔐 Credenciales por Defecto

Después de ejecutar el script SQL, se crea un usuario administrador por defecto:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

**⚠️ IMPORTANTE:** 
- Cambia la contraseña después del primer acceso por seguridad
- En producción, elimina o modifica este usuario por defecto

### Acceder al Panel Administrativo

1. Ve a: `http://localhost:5000/login`
2. Ingresa las credenciales de administrador
3. Serás redirigido al panel administrativo

## 📁 Estructura del Proyecto

```
Taller-Automotriz/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── dependencias.txt                # Descripción detallada de dependencias
├── README.md                       # Este archivo
│
├── base de datos/
│   └── servicio_automotriz.sql    # Script SQL para crear la base de datos
│
├── templates/                      # Templates HTML (Jinja2)
│   ├── base.html                  # Layout base
│   ├── index.html                 # Página principal
│   ├── login.html                 # Inicio de sesión
│   ├── citas.html                 # Agendar citas
│   ├── cotizaciones.html          # Solicitar cotizaciones
│   ├── contacto.html              # Información de contacto
│   ├── servicios.html             # Listado de servicios
│   │
│   ├── usuario/                   # Templates del panel de usuario
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── citas.html
│   │   └── cotizaciones.html
│   │
│   ├── admin/                     # Templates del panel admin
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── usuarios.html
│   │   ├── servicios.html
│   │   ├── roles.html
│   │   ├── precios.html
│   │   ├── citas.html
│   │   └── cotizaciones.html
│   │
│   └── emails/                    # Templates de correos
│       ├── bienvenida_admin.html
│       ├── confirmacion_cita.html
│       └── cotizacion.html
│
└── static/                         # Archivos estáticos
    ├── css/
    │   ├── estilo.css
    │   ├── admin.css
    │   └── cotizaciones.css
    ├── imagenes/
    │   ├── logo.jpg
    │   └── ...
    └── js/
```

## 🐛 Solución de Problemas

### Error: "TemplateNotFound: index.html"

**Causa:** Los archivos de templates no están en la ubicación correcta.

**Solución:**
- Verifica que la carpeta `templates/` exista en la raíz del proyecto
- Asegúrate de estar ejecutando Flask desde la carpeta raíz del proyecto
- Verifica que todos los archivos HTML estén en `templates/`

### Error: "ModuleNotFoundError: No module named 'flask'"

**Causa:** El entorno virtual no está activado o las dependencias no están instaladas.

**Solución:**
```bash
# Activar entorno virtual
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Error de Conexión a MySQL

**Causa:** Credenciales incorrectas o MySQL no está ejecutándose.

**Solución:**
1. Verifica que MySQL esté ejecutándose:
   ```bash
   # Windows (Servicios)
   services.msc
   # Buscar "MySQL" y verificar que esté "En ejecución"
   ```

2. Verifica las credenciales en `app.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'database': 'servicio_automotriz',
       'user': 'root',              # Verificar usuario
       'password': 'TU_PASSWORD',   # Verificar contraseña
   }
   ```

3. Verifica que la base de datos exista:
   ```sql
   SHOW DATABASES;
   -- Deberías ver 'servicio_automotriz' en la lista
   ```

### Error: "Port 5000 is already in use"

**Causa:** Otro proceso está usando el puerto 5000.

**Solución:**
1. Cambiar el puerto en `app.py` (al final del archivo):
   ```python
   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar a 5001
   ```

2. O detener el proceso que usa el puerto 5000.

### Error al Instalar Dependencias

**Solución:**
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias una por una si falla
pip install Flask==3.0.0
pip install mysql-connector-python==8.2.0
# ... etc
```

### Error: "Access denied for user"

**Causa:** Credenciales de MySQL incorrectas o usuario sin permisos.

**Solución:**
1. Verifica usuario y contraseña en `app.py`
2. Verifica que el usuario tenga permisos:
   ```sql
   GRANT ALL PRIVILEGES ON servicio_automotriz.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

### El CSS no se ve correctamente

**Causa:** Los archivos estáticos no se están cargando.

**Solución:**
- Verifica que la carpeta `static/` exista
- Asegúrate de que Flask esté ejecutándose desde la carpeta raíz
- Limpia la caché del navegador (`Ctrl + F5`)

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (Werkzeug)
- ✅ Sesiones seguras
- ✅ Protección de rutas con decoradores
- ✅ Validación de formularios
- ✅ Prevención de SQL injection (consultas parametrizadas)

**⚠️ IMPORTANTE para Producción:**
- Cambiar `SECRET_KEY` en `app.py`
- Desactivar modo debug: `app.run(debug=False)`
- Usar variables de entorno para credenciales sensibles
- Cambiar contraseñas por defecto
- Usar HTTPS en producción

## 🚀 Despliegue en Producción

1. **Cambiar SECRET_KEY:**
   ```python
   app.secret_key = os.environ.get('SECRET_KEY', 'clave-muy-larga-y-aleatoria')
   ```

2. **Desactivar modo debug:**
   ```python
   app.run(debug=False)
   ```

3. **Usar servidor WSGI (Gunicorn):**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Configurar servidor web (Nginx/Apache)**

5. **Variables de entorno:**
   - Crear archivo `.env` con credenciales
   - Nunca subir `.env` al repositorio (agregar a `.gitignore`)

## 📞 Soporte

Si encuentras problemas:

1. Revisa la sección [Solución de Problemas](#-solución-de-problemas)
2. Verifica que todos los pasos de instalación se hayan completado
3. Revisa los logs del servidor Flask en la terminal
4. Contacta al equipo de desarrollo

## 📄 Licencia

Este proyecto es de uso educativo y comercial.

---

**¡Listo!** 🎉 Ahora deberías tener el proyecto funcionando correctamente. Si tienes dudas, revisa esta documentación o contacta al equipo.
