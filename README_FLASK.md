# Taller Automotriz - Aplicación Flask

Sistema web para gestión de taller automotriz desarrollado con Flask (Python) y MySQL.

## 🚀 Características

- **Sitio Web Público:**
  - Página de inicio
  - Servicios ofrecidos
  - Solicitud de cotizaciones
  - Agendamiento de citas
  - Generación de presupuestos
  - Información de contacto

- **Panel Administrativo:**
  - Dashboard con estadísticas
  - Gestión de usuarios (CRUD)
  - Gestión de servicios (CRUD)
  - Gestión de roles (CRUD)
  - Sistema de autenticación

## 📋 Requisitos

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd Taller-Automotriz
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

1. Ejecutar el script SQL en MySQL Workbench:
   - Abrir `base de datos/servicio_automotriz_completo.sql`
   - Ejecutar el script completo

2. Verificar la configuración en `app.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'database': 'servicio_automotriz',
       'user': 'root',
       'password': '',  # Cambiar si es necesario
   }
   ```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🔐 Credenciales por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambiar la contraseña después del primer acceso.

## 📁 Estructura del Proyecto

```
Taller-Automotriz/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── templates/            # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── citas.html
│   ├── cotizaciones.html
│   ├── contacto.html
│   ├── servicios.html
│   ├── presupuesto.html
│   └── admin/
│       ├── base.html
│       ├── dashboard.html
│       ├── usuarios.html
│       ├── servicios.html
│       └── roles.html
├── static/               # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── imagenes/
├── base de datos/        # Scripts SQL
└── README_FLASK.md       # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **Backend:** Flask (Python)
- **Base de Datos:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Templates:** Jinja2
- **PDF:** ReportLab

## 📝 Funcionalidades Principales

### Sitio Público

1. **Inicio:** Página principal con información del taller
2. **Servicios:** Listado de servicios ofrecidos
3. **Cotizaciones:** Formulario para solicitar cotizaciones
4. **Citas:** Sistema de agendamiento de citas
5. **Presupuestos:** Generación de presupuestos con items
6. **Contacto:** Información de contacto y mapa

### Panel Administrativo

1. **Dashboard:** Estadísticas generales del sistema
2. **Usuarios:** 
   - Crear, editar, eliminar usuarios
   - Cambiar contraseñas
   - Asignar roles
3. **Servicios:**
   - Gestionar servicios ofrecidos
4. **Roles:**
   - Gestionar roles del sistema

## 🔒 Seguridad

- Contraseñas hasheadas con Werkzeug
- Sesiones seguras
- Protección de rutas administrativas
- Validación de formularios

## 🐛 Solución de Problemas

### Error de conexión a MySQL

- Verificar que MySQL esté ejecutándose
- Revisar credenciales en `app.py`
- Verificar que la base de datos exista

### Error al instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Puerto 5000 ocupado

Cambiar el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📄 Licencia

Este proyecto es de uso educativo.

## 👨‍💻 Desarrollo

Para desarrollo, activar el modo debug:
```python
app.run(debug=True)
```

**Nota:** No usar `debug=True` en producción.

## 🚀 Despliegue

Para producción:
1. Cambiar `SECRET_KEY` en `app.py`
2. Configurar variables de entorno
3. Usar servidor WSGI (Gunicorn, uWSGI)
4. Configurar servidor web (Nginx, Apache)
5. Desactivar modo debug

---

Desarrollado con ❤️ usando Flask

