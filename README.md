# Taller Automotriz - Sistema Web Flask

Sistema web completo para gestión de taller automotriz desarrollado con **Flask (Python)** y **MySQL**.

## 🚀 Características

### Sitio Web Público
- ✅ Página de inicio con información del taller
- ✅ Catálogo de servicios ofrecidos
- ✅ Sistema de solicitud de cotizaciones
- ✅ Agendamiento de citas en línea
- ✅ Generación de presupuestos con items
- ✅ Información de contacto con mapa

### Panel Administrativo
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión completa de usuarios (crear, editar, eliminar, cambiar contraseña)
- ✅ Gestión de servicios ofrecidos
- ✅ Gestión de roles y permisos
- ✅ Sistema de autenticación seguro

## 📋 Requisitos

- **Python 3.8+**
- **MySQL 5.7+** o **MariaDB 10.3+**
- **pip** (gestor de paquetes Python)

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd Taller-Automotriz
```

### 2. Crear entorno virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

1. Abrir **MySQL Workbench**
2. Ejecutar el script: `base de datos/servicio_automotriz_completo.sql`
3. Verificar que la base de datos `servicio_automotriz` se haya creado correctamente

### 5. Configurar conexión a MySQL

Editar `app.py` (líneas 15-21) con tus credenciales:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'servicio_automotriz',
    'user': 'root',           # Cambiar si es necesario
    'password': '',           # Cambiar si es necesario
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 🔐 Credenciales por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambiar la contraseña después del primer acceso por seguridad.

## 📁 Estructura del Proyecto

```
Taller-Automotriz/
├── app.py                      # Aplicación principal Flask
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos ignorados por Git
├── README.md                   # Este archivo
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── base.html              # Layout base
│   ├── index.html             # Página principal
│   ├── login.html             # Inicio de sesión
│   ├── citas.html             # Agendar citas
│   ├── cotizaciones.html      # Solicitar cotizaciones
│   ├── contacto.html          # Información de contacto
│   ├── servicios.html         # Listado de servicios
│   ├── presupuesto.html       # Generar presupuestos
│   └── admin/                 # Templates del panel admin
│       ├── base.html
│       ├── dashboard.html
│       ├── usuarios.html
│       ├── servicios.html
│       └── roles.html
│
├── static/                     # Archivos estáticos
│   ├── css/
│   │   ├── estilo.css        # Estilos principales
│   │   └── admin.css         # Estilos del panel admin
│   ├── js/
│   │   └── scripts.js        # JavaScript
│   └── imagenes/              # Imágenes del sitio
│
└── base de datos/              # Scripts SQL
    ├── servicio_automotriz_completo.sql
    ├── agregar_usuarios_roles.sql
    └── README_MYSQL_WORKBENCH.md
```

## 🛠️ Tecnologías Utilizadas

- **Backend:** Flask (Python)
- **Base de Datos:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript
- **Templates:** Jinja2
- **PDF:** ReportLab (para generación de PDFs)
- **Autenticación:** Werkzeug (hashing de contraseñas)

## 📝 Funcionalidades Detalladas

### Sitio Público

1. **Inicio (`/`)**
   - Información del taller
   - Servicios destacados
   - Historia de la empresa

2. **Servicios (`/servicios`)**
   - Catálogo visual de servicios
   - Imágenes y descripciones

3. **Cotizaciones (`/cotizaciones`)**
   - Formulario para solicitar cotizaciones
   - Almacenamiento en base de datos

4. **Citas (`/citas`)**
   - Sistema de agendamiento
   - Selección de fecha, hora y servicio

5. **Presupuestos (`/presupuesto`)**
   - Creación de presupuestos con múltiples items
   - Cálculo automático de totales
   - Generación de PDF

6. **Contacto (`/contacto`)**
   - Información de contacto
   - Mapa de ubicación (Google Maps)

### Panel Administrativo

1. **Dashboard (`/admin`)**
   - Estadísticas de usuarios, servicios, citas y cotizaciones
   - Vista general del sistema

2. **Usuarios (`/admin/usuarios`)**
   - Crear nuevos usuarios
   - Editar información de usuarios
   - Cambiar contraseñas
   - Activar/desactivar usuarios
   - Asignar roles

3. **Servicios (`/admin/servicios`)**
   - Gestionar servicios ofrecidos
   - Agregar, editar y eliminar servicios

4. **Roles (`/admin/roles`)**
   - Gestionar roles del sistema
   - Asignar permisos

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (Werkzeug)
- ✅ Sesiones seguras
- ✅ Protección de rutas con decoradores
- ✅ Validación de formularios
- ✅ Prevención de SQL injection (consultas parametrizadas)

## 🐛 Solución de Problemas

### Error de conexión a MySQL

```python
# Verificar en app.py:
DB_CONFIG = {
    'host': 'localhost',        # Verificar que MySQL esté corriendo
    'database': 'servicio_automotriz',  # Verificar que exista
    'user': 'root',             # Tu usuario MySQL
    'password': '',             # Tu contraseña MySQL
}
```

### Error al instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Puerto 5000 ocupado

Editar `app.py` al final:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar puerto
```

### Error "ModuleNotFoundError"

Asegúrate de tener el entorno virtual activado:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## 🚀 Despliegue en Producción

1. **Cambiar SECRET_KEY:**
   ```python
   app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-muy-larga-y-aleatoria')
   ```

2. **Desactivar modo debug:**
   ```python
   app.run(debug=False)
   ```

3. **Usar servidor WSGI:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Configurar servidor web (Nginx/Apache)**

5. **Variables de entorno:**
   - Crear archivo `.env` con credenciales
   - Usar `python-dotenv` para cargar variables

## 📄 Licencia

Este proyecto es de uso educativo.

## 👨‍💻 Desarrollo

Para desarrollo local:
```bash
python app.py
```

El modo debug está activado por defecto para desarrollo.

## 📞 Soporte

Para problemas o preguntas:
1. Revisar este README
2. Verificar logs de la aplicación
3. Revisar configuración de MySQL

---

**Desarrollado con ❤️ usando Flask (Python)**

